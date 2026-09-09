#!/usr/bin/env python3
"""检查三类资源ID对应：表达基因、STRING节点、GenePT嵌入键。"""
import sys, argparse
from pathlib import Path
import pandas as pd
import numpy as np

BASE = Path(__file__).resolve().parent.parent

def load_expression_genes(h5ad_path):
    try:
        import anndata
        adata = anndata.read_h5ad(h5ad_path, backed="r")
        return set(adata.var_names.astype(str))
    except Exception as e:
        print(f"[WARN] 无法加载表达基因: {e}")
        return set()

def load_string_nodes(edge_path):
    try:
        df = pd.read_csv(edge_path, sep="\t", comment="#", header=None)
        nodes = set(df.iloc[:, 0].astype(str)) | set(df.iloc[:, 1].astype(str))
        return nodes
    except Exception as e:
        print(f"[WARN] 无法加载STRING节点: {e}")
        return set()

def load_genept_keys(embedding_path):
    try:
        if embedding_path.endswith(".npy"):
            arr = np.load(embedding_path, allow_pickle=True)
            return set(arr.item().keys()) if arr.dtype == object else set()
        elif embedding_path.endswith(".tsv") or embedding_path.endswith(".csv"):
            df = pd.read_csv(embedding_path, sep="\t" if embedding_path.endswith(".tsv") else ",")
            return set(df.iloc[:, 0].astype(str))
    except Exception as e:
        print(f"[WARN] 无法加载GenePT键: {e}")
    return set()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--expression", help="表达矩阵h5ad路径")
    p.add_argument("--string", help="STRING边文件路径")
    p.add_argument("--genept", help="GenePT嵌入文件路径")
    args = p.parse_args()

    expr_genes = load_expression_genes(args.expression) if args.expression else set()
    string_nodes = load_string_nodes(args.string) if args.string else set()
    genept_keys = load_genept_keys(args.genept) if args.genept else set()

    print("=== 三类资源ID统计 ===")
    print(f"表达基因数: {len(expr_genes)}")
    print(f"STRING节点数: {len(string_nodes)}")
    print(f"GenePT键数: {len(genept_keys)}")

    # 交集
    all_three = expr_genes & string_nodes & genept_keys
    expr_string = expr_genes & string_nodes
    expr_genept = expr_genes & genept_keys
    string_genept = string_nodes & genept_keys

    print(f"\n=== 交集统计 ===")
    print(f"三者交集: {len(all_three)}")
    print(f"表达 ∩ STRING: {len(expr_string)}")
    print(f"表达 ∩ GenePT: {len(expr_genept)}")
    print(f"STRING ∩ GenePT: {len(string_genept)}")

    # 缺失
    if expr_genes:
        missing_string = expr_genes - string_nodes
        missing_genept = expr_genes - genept_keys
        print(f"\n=== 表达基因中的缺失 ===")
        print(f"不在STRING中: {len(missing_string)} ({100*len(missing_string)/len(expr_genes):.1f}%)")
        print(f"不在GenePT中: {len(missing_genept)} ({100*len(missing_genept)/len(expr_genes):.1f}%)")
        if missing_string:
            print(f"  前10个: {sorted(list(missing_string))[:10]}")

    # 保存结果
    out = BASE / "results" / "gene_intersection_summary.csv"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        f.write("metric,count\n")
        f.write(f"expression_genes,{len(expr_genes)}\n")
        f.write(f"string_nodes,{len(string_nodes)}\n")
        f.write(f"genept_keys,{len(genept_keys)}\n")
        f.write(f"all_three_intersection,{len(all_three)}\n")
        f.write(f"expression_string_intersection,{len(expr_string)}\n")
        f.write(f"expression_genept_intersection,{len(expr_genept)}\n")
        f.write(f"string_genept_intersection,{len(string_genept)}\n")
    print(f"\n[OK] 结果已保存: {out}")
    print("\n注意: 不静默丢弃无法匹配的基因。说明哪些基因用于表达输出，哪些只作为图节点。")

if __name__ == "__main__":
    sys.exit(main())
