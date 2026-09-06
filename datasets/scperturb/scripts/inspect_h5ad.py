#!/usr/bin/env python3
"""
检查 scPerturb h5ad 文件的结构和内容。

输出:
- 文件路径和大小
- adata.shape
- .X 数据类型
- 是否为稀疏矩阵
- obs 所有字段
- var 所有字段
- layers
- obsm
- 对照细胞数量
- 扰动数量
- 每种扰动的细胞数
- 每个细胞 UMI 数
- 每个细胞检测到的基因数
- 是否存在批次、剂量、时间和细胞类型信息
"""
import sys
import argparse
from pathlib import Path

import numpy as np
import anndata as ad


def human_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def inspect_h5ad(path):
    """检查 h5ad 文件。"""
    p = Path(path)
    if not p.exists():
        print(f"[ERROR] 文件不存在: {path}")
        return 1

    print("=" * 70)
    print(f"scPerturb h5ad 检查: {p.name}")
    print("=" * 70)
    print(f"文件路径: {p.resolve()}")
    print(f"文件大小: {human_size(p.stat().st_size)}")
    print()

    adata = ad.read_h5ad(p)

    # 形状
    print(f"AnnData 形状: {adata.n_obs} 细胞 × {adata.n_vars} 基因")
    print()

    # X
    from scipy.sparse import issparse
    print("-" * 70)
    print("表达矩阵 (.X)")
    print("-" * 70)
    if adata.X is not None:
        sparse = issparse(adata.X)
        print(f"数据类型: {adata.X.dtype}")
        print(f"是否稀疏: {sparse}")
        if sparse:
            print(f"稀疏格式: {adata.X.format}")
            print(f"非零元素: {adata.X.nnz} ({100*adata.X.nnz/(adata.n_obs*adata.n_vars):.2f}%)")
    print()

    # obs
    print("-" * 70)
    print("obs 所有字段 (细胞元数据)")
    print("-" * 70)
    for col in adata.obs.columns:
        dtype = adata.obs[col].dtype
        n_unique = adata.obs[col].nunique()
        print(f"  - {col}: dtype={dtype}, unique={n_unique}")
        if n_unique <= 20:
            print(f"    值: {dict(adata.obs[col].value_counts().head(20))}")
    print()

    # var
    print("-" * 70)
    print("var 所有字段 (基因元数据)")
    print("-" * 70)
    for col in adata.var.columns:
        print(f"  - {col}: dtype={adata.var[col].dtype}, unique={adata.var[col].nunique()}")
    if not adata.var.columns.empty:
        print(f"  (基因名示例: {list(adata.var_names[:5])})")
    print()

    # layers
    print("-" * 70)
    print("layers")
    print("-" * 70)
    for layer_name in adata.layers.keys():
        layer = adata.layers[layer_name]
        print(f"  - {layer_name}: shape={layer.shape}, dtype={layer.dtype}")
    if not adata.layers:
        print("  (无)")
    print()

    # obsm
    print("-" * 70)
    print("obsm (多维注释)")
    print("-" * 70)
    for key in adata.obsm.keys():
        val = adata.obsm[key]
        print(f"  - {key}: shape={val.shape}, dtype={val.dtype if hasattr(val, 'dtype') else type(val)}")
    if not adata.obsm:
        print("  (无)")
    print()

    # 扰动统计
    print("-" * 70)
    print("扰动统计")
    print("-" * 70)

    perturb_col = None
    for col in ["perturbation", "condition", "guide", "target", "perturb", "drug"]:
        if col in adata.obs.columns:
            perturb_col = col
            break

    if perturb_col:
        print(f"扰动标签列: {perturb_col}")
        counts = adata.obs[perturb_col].value_counts()
        print(f"扰动数量: {len(counts)}")
        print()

        # 对照细胞
        ctrl_keywords = ["ctrl", "control", "unperturbed", "untreated", "vehicle", "dmso"]
        ctrl_count = 0
        for cond, cnt in counts.items():
            if str(cond).lower() in ctrl_keywords:
                ctrl_count += cnt
        print(f"对照细胞数量: {ctrl_count}")
        print()

        print("每种扰动的细胞数 (前30):")
        for cond, cnt in counts.head(30).items():
            print(f"  {cond}: {cnt}")
    else:
        print("未找到扰动标签列")
    print()

    # 细胞质量
    print("-" * 70)
    print("每个细胞 UMI 数和检测基因数")
    print("-" * 70)
    if adata.X is not None:
        if issparse(adata.X):
            umi_counts = np.asarray(adata.X.sum(axis=1)).flatten()
            n_genes_detected = np.asarray((adata.X > 0).sum(axis=1)).flatten()
        else:
            umi_counts = np.asarray(adata.X.sum(axis=1)).flatten()
            n_genes_detected = np.asarray((adata.X > 0).sum(axis=1)).flatten()

        print(f"UMI 数: mean={umi_counts.mean():.1f}, median={np.median(umi_counts):.1f}, "
              f"min={umi_counts.min():.0f}, max={umi_counts.max():.0f}")
        print(f"检测基因数: mean={n_genes_detected.mean():.1f}, median={np.median(n_genes_detected):.1f}, "
              f"min={n_genes_detected.min():.0f}, max={n_genes_detected.max():.0f}")
    print()

    # 批次、剂量、时间、细胞类型
    print("-" * 70)
    print("元数据字段检查")
    print("-" * 70)
    checks = {
        "批次": ["batch", "sample", "donor", "patient", "replicate"],
        "剂量": ["dose", "dosage", "concentration"],
        "时间": ["time", "timepoint", "hour", "day"],
        "细胞类型": ["cell_type", "celltype", "cluster", "cell_line", "tissue"],
    }
    for label, keywords in checks.items():
        found = [kw for kw in keywords if kw in adata.obs.columns]
        status = "是" if found else "否"
        detail = f" (字段: {found})" if found else ""
        print(f"  {label}信息: {status}{detail}")
    print()

    print("=" * 70)
    print("检查完成")
    print("=" * 70)
    return 0


def main():
    parser = argparse.ArgumentParser(description="检查 scPerturb h5ad 文件")
    parser.add_argument("path", help="h5ad 文件路径")
    args = parser.parse_args()
    return inspect_h5ad(args.path)


if __name__ == "__main__":
    sys.exit(main())
