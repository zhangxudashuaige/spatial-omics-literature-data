#!/usr/bin/env python3
"""检查基因嵌入：ID类型、维度、来源、覆盖范围、缺失处理。"""
import sys, argparse
from pathlib import Path
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent.parent

def inspect_embedding(filepath):
    f = Path(filepath)
    print(f"文件: {f.name} ({f.stat().st_size / 1024 / 1024:.1f} MB)")

    if f.suffix == ".npy":
        arr = np.load(f, allow_pickle=True)
        if arr.dtype == object:
            d = arr.item()
            genes = list(d.keys())
            dim = d[genes[0]].shape if hasattr(d[genes[0]], 'shape') else (1,)
            print(f"基因数: {len(genes)}")
            print(f"嵌入维度: {dim}")
            print(f"前5个基因: {genes[:5]}")
            # ID类型
            sample = [str(g) for g in genes[:50]]
            if any(g.startswith("ENSG") for g in sample):
                id_type = "Ensembl"
            elif any(g.isdigit() for g in sample):
                id_type = "Entrez"
            else:
                id_type = "Gene Symbol"
            print(f"基因ID类型: {id_type}")
            # 一个真实嵌入
            print(f"\n基因 {genes[0]} 的嵌入前10维: {np.array(d[genes[0]]).flatten()[:10]}")
        else:
            print(f"数组形状: {arr.shape}")
            print(f"dtype: {arr.dtype}")
    elif f.suffix in [".tsv", ".csv"]:
        sep = "\t" if f.suffix == ".tsv" else ","
        df = pd.read_csv(f, sep=sep, header=None, nrows=5)
        print(f"形状(前5行): {df.shape}")
        print(f"列数: {df.shape[1]}")
        full = pd.read_csv(f, sep=sep, header=None)
        print(f"总行数: {len(full)}")
        print(f"嵌入维度: {full.shape[1] - 1}")
        print(f"前5个基因: {full.iloc[:5, 0].tolist()}")
    else:
        print(f"[WARN] 不支持的格式: {f.suffix}")

def check_coverage(embedding_path, expression_path):
    """检查嵌入对表达基因的覆盖。"""
    print("\n=== 覆盖检查 ===")
    # 加载嵌入基因
    emb_genes = set()
    f = Path(embedding_path)
    if f.suffix == ".npy":
        arr = np.load(f, allow_pickle=True)
        if arr.dtype == object:
            emb_genes = set(arr.item().keys())
    print(f"嵌入基因数: {len(emb_genes)}")

    # 加载表达基因
    try:
        import anndata
        adata = anndata.read_h5ad(expression_path, backed="r")
        expr_genes = set(adata.var_names.astype(str))
        print(f"表达基因数: {len(expr_genes)}")
        overlap = emb_genes & expr_genes
        missing = expr_genes - emb_genes
        print(f"交集: {len(overlap)} ({100*len(overlap)/len(expr_genes):.1f}%)")
        print(f"表达基因中缺失嵌入: {len(missing)} ({100*len(missing)/len(expr_genes):.1f}%)")
        if missing:
            print(f"前10个缺失基因: {sorted(list(missing))[:10]}")
    except Exception as e:
        print(f"[WARN] 无法加载表达矩阵: {e}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True, help="嵌入文件路径")
    p.add_argument("--expression", help="表达矩阵路径（用于覆盖检查）")
    args = p.parse_args()
    inspect_embedding(args.file)
    if args.expression:
        check_coverage(args.file, args.expression)
    return 0

if __name__ == "__main__":
    sys.exit(main())
