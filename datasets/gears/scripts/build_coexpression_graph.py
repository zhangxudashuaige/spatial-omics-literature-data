#!/usr/bin/env python3
"""
构建基因共表达图 (co-expression graph)。

由训练集基因的 Pearson 相关性构建，保存:
- 节点表 (genes.csv)
- 边表 (edges.csv)
- edge_index (PyTorch tensor, .pt)
- edge_weight (PyTorch tensor, .pt)
- 构图阈值
- 每个节点保留的邻居数
- 图统计信息
"""
import sys
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import issparse

GRAPH_DIR = Path(__file__).resolve().parent.parent / "graphs" / "coexpression"


def build_coexpression_graph(adata, threshold=0.3, max_neighbors=10, n_top_genes=2000):
    """构建共表达图。"""
    print("[INFO] 构建共表达图...")
    print(f"       阈值: {threshold}")
    print(f"       最大邻居数: {max_neighbors}")
    print(f"       top 基因数: {n_top_genes}")

    # 选择高变基因
    import scanpy as sc
    adata_hvg = adata.copy()
    sc.pp.highly_variable_genes(adata_hvg, n_top_genes=min(n_top_genes, adata.n_vars))
    hvg_mask = adata_hvg.var["highly_variable"].values
    gene_names = adata.var_names[hvg_mask].values
    print(f"[INFO] 使用 {len(gene_names)} 个高变基因")

    # 获取表达矩阵
    X = adata.X[:, hvg_mask]
    if issparse(X):
        X = X.toarray()
    X = np.log1p(X)

    # 计算 Pearson 相关系数
    print("[INFO] 计算基因间 Pearson 相关系数...")
    corr = np.corrcoef(X.T)
    corr = np.nan_to_num(corr, nan=0.0)

    # 构建边
    print("[INFO] 构建边列表...")
    edges = []
    for i in range(len(gene_names)):
        # 获取与基因 i 相关性最高的邻居
        row = corr[i].copy()
        row[i] = -np.inf  # 排除自环
        top_indices = np.argsort(row)[::-1][:max_neighbors]

        for j in top_indices:
            if row[j] >= threshold:
                edges.append((i, j, row[j]))

    print(f"[INFO] 边数: {len(edges)}")

    # 去重 (无向图)
    edge_set = set()
    unique_edges = []
    for i, j, w in edges:
        key = (min(i, j), max(i, j))
        if key not in edge_set:
            edge_set.add(key)
            unique_edges.append((i, j, w))

    print(f"[INFO] 去重后边数: {len(unique_edges)}")

    # 保存
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)

    # 节点表
    nodes_df = pd.DataFrame({
        "node_id": range(len(gene_names)),
        "gene_name": gene_names,
    })
    nodes_df.to_csv(GRAPH_DIR / "genes.csv", index=False)
    print(f"[OK] 节点表: {GRAPH_DIR / 'genes.csv'}")

    # 边表
    edges_df = pd.DataFrame(unique_edges, columns=["source", "target", "weight"])
    edges_df.to_csv(GRAPH_DIR / "edges.csv", index=False)
    print(f"[OK] 边表: {GRAPH_DIR / 'edges.csv'}")

    # edge_index 和 edge_weight (PyTorch)
    try:
        import torch
        edge_index = torch.tensor(
            [[e[0] for e in unique_edges], [e[1] for e in unique_edges]],
            dtype=torch.long,
        )
        edge_weight = torch.tensor([e[2] for e in unique_edges], dtype=torch.float32)
        torch.save(edge_index, GRAPH_DIR / "edge_index.pt")
        torch.save(edge_weight, GRAPH_DIR / "edge_weight.pt")
        print(f"[OK] edge_index: {GRAPH_DIR / 'edge_index.pt'}")
        print(f"[OK] edge_weight: {GRAPH_DIR / 'edge_weight.pt'}")
    except ImportError:
        print("[WARN] PyTorch 未安装，跳过 .pt 保存")

    # 图统计
    stats = {
        "n_nodes": len(gene_names),
        "n_edges": len(unique_edges),
        "threshold": threshold,
        "max_neighbors": max_neighbors,
        "n_top_genes": n_top_genes,
        "avg_degree": 2 * len(unique_edges) / len(gene_names),
        "density": 2 * len(unique_edges) / (len(gene_names) * (len(gene_names) - 1)),
    }
    stats_df = pd.DataFrame([stats])
    stats_df.to_csv(GRAPH_DIR / "graph_stats.csv", index=False)
    print()
    print("=" * 60)
    print("图统计信息")
    print("=" * 60)
    for k, v in stats.items():
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")

    return stats


def main():
    parser = argparse.ArgumentParser(description="构建基因共表达图")
    parser.add_argument("--adata", required=True, help="AnnData 文件路径")
    parser.add_argument("--threshold", type=float, default=0.3, help="相关性阈值")
    parser.add_argument("--max-neighbors", type=int, default=10, help="每个节点最大邻居数")
    parser.add_argument("--n-top-genes", type=int, default=2000, help="高变基因数")
    args = parser.parse_args()

    import anndata as ad
    adata = ad.read_h5ad(args.adata)
    print(f"[INFO] 加载数据: {adata.shape}")

    build_coexpression_graph(adata, args.threshold, args.max_neighbors, args.n_top_genes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
