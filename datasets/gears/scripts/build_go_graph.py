#!/usr/bin/env python3
"""
构建 Gene Ontology 相似度图 (GO similarity graph)。

由 GO 条目的 Jaccard 相似度构建，保存:
- 节点表
- 边表
- edge_index
- edge_weight
- 构图阈值
- 每个节点保留的邻居数
- 图统计信息
"""
import sys
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

GRAPH_DIR = Path(__file__).resolve().parent.parent / "graphs" / "go_similarity"
GO_DIR = Path(__file__).resolve().parent.parent / "data" / "external" / "gene_ontology"


def download_go_data():
    """下载 Gene Ontology 数据。"""
    GO_DIR.mkdir(parents=True, exist_ok=True)

    obo_path = GO_DIR / "go-basic.obo"
    if obo_path.exists():
        print(f"[OK] GO OBO 已存在: {obo_path}")
        return obo_path

    print("[INFO] 下载 Gene Ontology OBO 文件...")
    url = "http://purl.obolibrary.org/obo/go/go-basic.obo"
    try:
        from urllib.request import urlretrieve
        urlretrieve(url, str(obo_path))
        print(f"[OK] 下载完成: {obo_path}")
        return obo_path
    except Exception as e:
        print(f"[ERROR] 下载失败: {e}")
        print("[INFO] 请手动下载: http://purl.obolibrary.org/obo/go/go-basic.obo")
        return None


def build_go_similarity_graph(gene_names, threshold=0.3, max_neighbors=10):
    """基于 GO 注释构建基因相似度图。"""
    print("[INFO] 构建 GO 相似度图...")
    print(f"       阈值: {threshold}")
    print(f"       最大邻居数: {max_neighbors}")
    print(f"       基因数: {len(gene_names)}")

    obo_path = download_go_data()
    if obo_path is None:
        print("[ERROR] 无法获取 GO 数据，跳过图构建。")
        return None

    # 解析 OBO
    try:
        import obonet
        import networkx as nx
        print("[INFO] 解析 GO OBO...")
        graph = obonet.read_obo(obo_path)
        print(f"[OK] GO 术语数: {graph.number_of_nodes()}")
    except ImportError:
        print("[ERROR] obonet 未安装。请运行: pip install obonet")
        return None

    # 注意: 完整的 GO 相似度图需要基因-GO 注释文件 (GAF)
    # 这里提供框架，实际使用时需要下载对应物种的 GAF 文件
    print()
    print("[WARN] 构建完整 GO 相似度图需要基因-GO 注释文件 (GAF)。")
    print("[WARN] 请从 Gene Ontology 官网下载对应物种的 GAF:")
    print("       http://current.geneontology.org/products/pages/downloads.html")
    print("[WARN] 本脚本提供图构建框架，GAF 解析和 Jaccard 计算需根据实际数据完成。")
    print()

    # 框架: 如果有 GAF 数据，计算基因间 GO 集合的 Jaccard 相似度
    # gene_go_sets = {gene: set(go_terms) for gene in gene_names}
    # for i in range(len(gene_names)):
    #     for j in range(i+1, len(gene_names)):
    #         intersection = gene_go_sets[gene_i] & gene_go_sets[gene_j]
    #         union = gene_go_sets[gene_i] | gene_go_sets[gene_j]
    #         jaccard = len(intersection) / len(union) if union else 0
    #         if jaccard >= threshold:
    #             edges.append((i, j, jaccard))

    GRAPH_DIR.mkdir(parents=True, exist_ok=True)

    # 保存节点表 (基因列表)
    nodes_df = pd.DataFrame({
        "node_id": range(len(gene_names)),
        "gene_name": gene_names,
    })
    nodes_df.to_csv(GRAPH_DIR / "genes.csv", index=False)
    print(f"[OK] 节点表: {GRAPH_DIR / 'genes.csv'}")

    # 保存配置
    config = pd.DataFrame([{
        "threshold": threshold,
        "max_neighbors": max_neighbors,
        "obo_file": str(obo_path),
        "status": "framework_ready_needs_gaf",
    }])
    config.to_csv(GRAPH_DIR / "build_config.csv", index=False)

    print()
    print("=" * 60)
    print("GO 相似度图构建框架已就绪")
    print("=" * 60)
    print("下一步:")
    print("  1. 下载对应物种 GAF 文件到 data/external/gene_ontology/")
    print("  2. 实现 GAF 解析和 Jaccard 计算")
    print("  3. 重新运行本脚本生成边表和 edge_index")

    return None


def main():
    parser = argparse.ArgumentParser(description="构建 GO 相似度图")
    parser.add_argument("--gene-list", default=None, help="基因列表文件 (每行一个基因)")
    parser.add_argument("--adata", default=None, help="从 AnnData 获取基因列表")
    parser.add_argument("--threshold", type=float, default=0.3, help="Jaccard 相似度阈值")
    parser.add_argument("--max-neighbors", type=int, default=10, help="每个节点最大邻居数")
    args = parser.parse_args()

    # 获取基因列表
    if args.gene_list:
        with open(args.gene_list) as f:
            gene_names = [line.strip() for line in f if line.strip()]
    elif args.adata:
        import anndata as ad
        adata = ad.read_h5ad(args.adata)
        gene_names = adata.var_names.values
    else:
        print("[ERROR] 请提供 --gene-list 或 --adata")
        return 1

    print(f"[INFO] 基因数: {len(gene_names)}")
    build_go_similarity_graph(gene_names, args.threshold, args.max_neighbors)
    return 0


if __name__ == "__main__":
    sys.exit(main())
