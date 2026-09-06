#!/usr/bin/env python3
"""
检查 PerturbNet h5ad 文件结构。

展示:
- AnnData 形状: 细胞数 × 基因数
- X 矩阵类型和稀疏度
- obs 列名
- var 列名
- 扰动类别数量
- 每种扰动的细胞数量
- 对照组数量
- 细胞类型和剂量分布
- 前 5 个细胞、前 10 个基因的表达
- UMAP (如果已经存在)
- 扰动组与对照组的平均表达差异

如果文件不是 h5ad，先识别格式，再使用相应读取库，不通过修改扩展名强行读取。
"""
import sys
import argparse
from pathlib import Path

import numpy as np


def detect_format(filepath):
    """检测文件格式。"""
    ext = filepath.suffix.lower()
    format_map = {
        ".h5ad": "anndata",
        ".h5": "hdf5",
        ".h5seurat": "seurat_h5",
        ".rds": "r_rds",
        ".csv": "csv",
        ".tsv": "tsv",
        ".mtx": "matrix_market",
        ".npz": "numpy",
        ".npy": "numpy",
    }
    return format_map.get(ext, "unknown")


def inspect_h5ad(filepath):
    """检查 h5ad 文件。"""
    import anndata as ad
    from scipy.sparse import issparse

    adata = ad.read_h5ad(filepath)

    print(f"AnnData 形状: {adata.n_obs} 细胞 × {adata.n_vars} 基因")
    print()

    # X
    print("-" * 50)
    print("表达矩阵 (.X)")
    print("-" * 50)
    if adata.X is not None:
        sparse = issparse(adata.X)
        print(f"数据类型: {adata.X.dtype}")
        print(f"是否稀疏: {sparse}")
        if sparse:
            print(f"稀疏格式: {adata.X.format}")
            print(f"非零元素: {adata.X.nnz}")
    print()

    # obs
    print("-" * 50)
    print("obs 列名")
    print("-" * 50)
    for col in adata.obs.columns:
        print(f"  - {col}: {adata.obs[col].dtype} (unique: {adata.obs[col].nunique()})")
    print()

    # var
    print("-" * 50)
    print("var 列名")
    print("-" * 50)
    for col in adata.var.columns:
        print(f"  - {col}: {adata.var[col].dtype}")
    print()

    # 扰动统计
    print("-" * 50)
    print("扰动统计")
    print("-" * 50)
    perturb_col = None
    for col in ["perturbation", "condition", "perturb", "guide", "target", "drug"]:
        if col in adata.obs.columns:
            perturb_col = col
            break

    if perturb_col:
        counts = adata.obs[perturb_col].value_counts()
        print(f"扰动标签列: {perturb_col}")
        print(f"扰动类别数量: {len(counts)}")
        print()

        # 对照组
        ctrl_keywords = ["ctrl", "control", "unperturbed", "vehicle", "dmso", "untreated"]
        ctrl_count = sum(c for k, c in counts.items() if str(k).lower() in ctrl_keywords)
        print(f"对照组细胞数量: {ctrl_count}")
        print()

        print("每种扰动的细胞数量 (前30):")
        for cond, cnt in counts.head(30).items():
            print(f"  {cond}: {cnt}")
    else:
        print("未找到扰动标签列")
    print()

    # 细胞类型和剂量
    print("-" * 50)
    print("细胞类型和剂量分布")
    print("-" * 50)
    for col in ["cell_type", "CellType", "celltype", "cell_line", "cluster"]:
        if col in adata.obs.columns:
            print(f"细胞类型 ({col}):")
            print(adata.obs[col].value_counts().head(15))
            print()
            break
    for col in ["dose", "dosage", "concentration", "dose_value"]:
        if col in adata.obs.columns:
            print(f"剂量 ({col}):")
            print(adata.obs[col].value_counts().head(15))
            print()
            break

    # 前 5 个细胞、前 10 个基因的表达
    print("-" * 50)
    print("前 5 个细胞 × 前 10 个基因的表达")
    print("-" * 50)
    if adata.X is not None:
        subset = adata.X[:5, :10]
        if issparse(subset):
            subset = subset.toarray()
        genes = list(adata.var_names[:10])
        cells = list(adata.obs_names[:5])
        print(f"{'':15s}", end="")
        for g in genes:
            print(f"{g:>10s}", end="")
        print()
        for i, cell in enumerate(cells):
            print(f"{cell[:13]:15s}", end="")
            for j in range(10):
                print(f"{subset[i, j]:10.2f}", end="")
            print()
    print()

    # UMAP
    if "X_umap" in adata.obsm:
        print("-" * 50)
        print("UMAP")
        print("-" * 50)
        print(f"UMAP 形状: {adata.obsm['X_umap'].shape}")
        print(f"前 5 个细胞 UMAP 坐标:")
        print(adata.obsm["X_umap"][:5])
        print()
    else:
        print("[INFO] 不包含 UMAP。")
        print()

    # 扰动组与对照组的平均表达差异
    if perturb_col and ctrl_count > 0:
        print("-" * 50)
        print("扰动组与对照组的平均表达差异 (top 10 基因)")
        print("-" * 50)
        ctrl_mask = adata.obs[perturb_col].str.lower().isin(ctrl_keywords).values
        if ctrl_mask.sum() > 0:
            ctrl_mean = np.asarray(adata.X[ctrl_mask].mean(axis=0)).flatten() if issparse(adata.X) else adata.X[ctrl_mask].mean(axis=0)
            pert_mean = np.asarray(adata.X[~ctrl_mask].mean(axis=0)).flatten() if issparse(adata.X) else adata.X[~ctrl_mask].mean(axis=0)
            diff = pert_mean - ctrl_mean
            top_idx = np.argsort(np.abs(diff))[::-1][:10]
            print(f"{'基因':15s} {'对照均值':>10s} {'扰动均值':>10s} {'差异':>10s}")
            for idx in top_idx:
                print(f"{adata.var_names[idx]:15s} {ctrl_mean[idx]:10.2f} {pert_mean[idx]:10.2f} {diff[idx]:10.2f}")
        print()

    print("=" * 50)
    print("检查完成")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="检查 PerturbNet 数据文件")
    parser.add_argument("path", help="数据文件路径")
    args = parser.parse_args()

    filepath = Path(args.path)
    if not filepath.exists():
        print(f"[ERROR] 文件不存在: {filepath}")
        return 1

    print("=" * 50)
    print(f"文件检查: {filepath.name}")
    print("=" * 50)
    print(f"文件路径: {filepath.resolve()}")
    print(f"文件大小: {filepath.stat().st_size / (1024*1024):.2f} MB")

    fmt = detect_format(filepath)
    print(f"检测格式: {fmt}")
    print()

    if fmt == "anndata":
        inspect_h5ad(filepath)
    elif fmt == "unknown":
        print(f"[ERROR] 不支持的文件格式: {filepath.suffix}")
        print("[ERROR] 不通过修改扩展名强行读取。")
        print("[ERROR] 请使用相应的读取库。")
        return 1
    else:
        print(f"[INFO] 文件格式为 {fmt}。")
        print(f"[INFO] 请使用相应的读取库。")
        print(f"[INFO] h5ad 检查功能仅支持 .h5ad 格式。")

    return 0


if __name__ == "__main__":
    sys.exit(main())
