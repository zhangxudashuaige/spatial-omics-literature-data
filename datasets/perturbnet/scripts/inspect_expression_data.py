#!/usr/bin/env python3
"""
检查 PerturbNet 表达数据。

支持多种格式: h5ad, csv, tsv, mtx, npz, npy
展示表达矩阵的基本统计信息。
"""
import sys
import argparse
from pathlib import Path

import numpy as np


def inspect_expression(filepath):
    """检查表达数据文件。"""
    ext = filepath.suffix.lower()

    print("=" * 60)
    print(f"表达数据检查: {filepath.name}")
    print("=" * 60)
    print(f"文件大小: {filepath.stat().st_size / (1024*1024):.2f} MB")
    print(f"格式: {ext}")
    print()

    if ext == ".h5ad":
        import anndata as ad
        from scipy.sparse import issparse
        adata = ad.read_h5ad(filepath)
        X = adata.X
        print(f"形状: {adata.n_obs} 细胞 × {adata.n_vars} 基因")
        print(f"数据类型: {X.dtype}")
        print(f"稀疏: {issparse(X)}")
        if issparse(X):
            print(f"非零比例: {100 * X.nnz / (adata.n_obs * adata.n_vars):.2f}%")
            data = X.data
        else:
            data = X.flatten()
        print(f"表达值范围: [{data.min():.2f}, {data.max():.2f}]")
        print(f"表达值均值: {data.mean():.4f}")
        print(f"表达值中位数: {np.median(data):.4f}")
        print()

        # 细胞统计
        if issparse(X):
            cell_totals = np.asarray(X.sum(axis=1)).flatten()
            cell_genes = np.asarray((X > 0).sum(axis=1)).flatten()
        else:
            cell_totals = X.sum(axis=1)
            cell_genes = (X > 0).sum(axis=1)
        print(f"细胞总计数: mean={cell_totals.mean():.1f}, median={np.median(cell_totals):.1f}")
        print(f"细胞检测基因数: mean={cell_genes.mean():.1f}, median={np.median(cell_genes):.1f}")
        print()

        # 基因统计
        if issparse(X):
            gene_cells = np.asarray((X > 0).sum(axis=0)).flatten()
        else:
            gene_cells = (X > 0).sum(axis=0)
        print(f"基因表达细胞数: mean={gene_cells.mean():.1f}, median={np.median(gene_cells):.1f}")
        print(f"高表达基因 (前10):")
        top_genes = np.argsort(gene_cells)[::-1][:10]
        for idx in top_genes:
            print(f"  {adata.var_names[idx]}: {gene_cells[idx]} 细胞")

    elif ext in [".csv", ".tsv"]:
        import pandas as pd
        sep = "," if ext == ".csv" else "\t"
        df = pd.read_csv(filepath, sep=sep, index_col=0)
        print(f"形状: {df.shape[0]} × {df.shape[1]}")
        print(f"数据类型: {df.dtypes.value_counts().to_dict()}")
        print(f"表达值范围: [{df.values.min():.2f}, {df.values.max():.2f}]")
        print(f"前5行前5列:")
        print(df.iloc[:5, :5])

    elif ext == ".mtx":
        from scipy.io import mmread
        X = mmread(filepath)
        print(f"形状: {X.shape}")
        print(f"稀疏: {True}")
        print(f"非零元素: {X.nnz}")
        print(f"表达值范围: [{X.data.min():.2f}, {X.data.max():.2f}]")

    elif ext in [".npz", ".npy"]:
        data = np.load(filepath, allow_pickle=True)
        if ext == ".npz":
            print(f"数组列表: {list(data.keys())}")
            for key in data.keys():
                arr = data[key]
                print(f"  {key}: shape={arr.shape}, dtype={arr.dtype}")
        else:
            print(f"形状: {data.shape}")
            print(f"数据类型: {data.dtype}")
            print(f"值范围: [{data.min():.2f}, {data.max():.2f}]")

    else:
        print(f"[ERROR] 不支持的格式: {ext}")
        return 1

    print()
    print("=" * 60)
    print("检查完成")
    print("=" * 60)
    return 0


def main():
    parser = argparse.ArgumentParser(description="检查表达数据")
    parser.add_argument("path", help="表达数据文件路径")
    args = parser.parse_args()

    filepath = Path(args.path)
    if not filepath.exists():
        print(f"[ERROR] 文件不存在: {filepath}")
        return 1

    return inspect_expression(filepath)


if __name__ == "__main__":
    sys.exit(main())
