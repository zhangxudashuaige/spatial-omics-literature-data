#!/usr/bin/env python3
"""
检查 h5ad 文件的结构和内容。

输出:
- 文件大小
- AnnData 形状
- .X 的数据类型
- 是否为稀疏矩阵
- obs 字段
- var 字段
- layers
- obsm
- 扰动条件及细胞数量
- 每个细胞总计数和检测基因数摘要

用法:
    python scripts/inspect_h5ad.py path/to/file.h5ad
"""
import sys
import argparse
from pathlib import Path

import numpy as np
import anndata as ad


def human_size(size_bytes):
    """人类可读的文件大小。"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def inspect_file(path):
    """检查 h5ad 文件。"""
    p = Path(path)
    if not p.exists():
        print(f"[ERROR] 文件不存在: {path}")
        return 1

    print("=" * 70)
    print(f"AnnData 检查: {p.name}")
    print("=" * 70)
    print()

    # 文件大小
    file_size = p.stat().st_size
    print(f"文件路径: {p.resolve()}")
    print(f"文件大小: {human_size(file_size)} ({file_size} bytes)")
    print()

    # 加载
    print("[INFO] 加载 AnnData...")
    adata = ad.read_h5ad(p)
    print()

    # 形状
    print("-" * 70)
    print("基本信息")
    print("-" * 70)
    print(f"AnnData 形状: {adata.n_obs} 细胞 × {adata.n_vars} 基因")
    print(f"obs_names 示例: {list(adata.obs_names[:5])}")
    print(f"var_names 示例: {list(adata.var_names[:5])}")
    print()

    # X
    print("-" * 70)
    print("表达矩阵 (.X)")
    print("-" * 70)
    if adata.X is not None:
        from scipy.sparse import issparse
        sparse = issparse(adata.X)
        print(f"数据类型: {adata.X.dtype}")
        print(f"是否稀疏: {sparse}")
        if sparse:
            print(f"稀疏格式: {adata.X.format}")
            print(f"非零元素: {adata.X.nnz} ({100 * adata.X.nnz / (adata.n_obs * adata.n_vars):.2f}%)")
        # 前几个值
        if sparse:
            sample = adata.X.data[:10]
        else:
            sample = adata.X.flatten()[:10]
        print(f"前10个值: {sample}")
        print(f"最小值: {adata.X.min() if not sparse else adata.X.data.min()}")
        print(f"最大值: {adata.X.max() if not sparse else adata.X.data.max()}")
    else:
        print(".X 为空")
    print()

    # obs
    print("-" * 70)
    print("obs 字段 (细胞元数据)")
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
    print("var 字段 (基因元数据)")
    print("-" * 70)
    for col in adata.var.columns:
        dtype = adata.var[col].dtype
        n_unique = adata.var[col].nunique()
        print(f"  - {col}: dtype={dtype}, unique={n_unique}")
    print()

    # layers
    print("-" * 70)
    print("layers")
    print("-" * 70)
    for layer_name in adata.layers.keys():
        layer = adata.layers[layer_name]
        from scipy.sparse import issparse
        sparse = issparse(layer)
        print(f"  - {layer_name}: shape={layer.shape}, dtype={layer.dtype}, sparse={sparse}")
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

    # 扰动条件
    print("-" * 70)
    print("扰动条件及细胞数量")
    print("-" * 70)
    perturb_col = None
    for col in ["condition", "perturbation", "perturb", "guide", "target"]:
        if col in adata.obs.columns:
            perturb_col = col
            break

    if perturb_col:
        print(f"扰动标签列: {perturb_col}")
        counts = adata.obs[perturb_col].value_counts()
        print(f"总条件数: {len(counts)}")
        print()
        print("前30个条件:")
        for cond, cnt in counts.head(30).items():
            print(f"  {cond}: {cnt} 细胞")

        # 统计单扰动和组合扰动
        single = 0
        combo = 0
        ctrl = 0
        for cond in counts.index:
            if str(cond).lower() in ["ctrl", "control", ""]:
                ctrl += counts[cond]
            elif "+" in str(cond):
                combo += counts[cond]
            else:
                single += counts[cond]
        print()
        print(f"对照细胞: {ctrl}")
        print(f"单扰动细胞: {single}")
        print(f"组合扰动细胞: {combo}")
    else:
        print("未找到扰动标签列")
    print()

    # 细胞质量摘要
    print("-" * 70)
    print("每个细胞总计数和检测基因数摘要")
    print("-" * 70)
    from scipy.sparse import issparse
    if adata.X is not None:
        if issparse(adata.X):
            total_counts = np.asarray(adata.X.sum(axis=1)).flatten()
            n_genes = np.asarray((adata.X > 0).sum(axis=1)).flatten()
        else:
            total_counts = np.asarray(adata.X.sum(axis=1)).flatten()
            n_genes = np.asarray((adata.X > 0).sum(axis=1)).flatten()

        print(f"总计数 (UMI):")
        print(f"  mean={total_counts.mean():.1f}, median={np.median(total_counts):.1f}")
        print(f"  min={total_counts.min():.1f}, max={total_counts.max():.1f}")
        print(f"  std={total_counts.std():.1f}")
        print()
        print(f"检测基因数:")
        print(f"  mean={n_genes.mean():.1f}, median={np.median(n_genes):.1f}")
        print(f"  min={n_genes.min():.0f}, max={n_genes.max():.0f}")
        print(f"  std={n_genes.std():.1f}")
    print()

    print("=" * 70)
    print("检查完成")
    print("=" * 70)
    return 0


def main():
    parser = argparse.ArgumentParser(description="检查 h5ad 文件结构")
    parser.add_argument("path", help="h5ad 文件路径")
    args = parser.parse_args()
    return inspect_file(args.path)


if __name__ == "__main__":
    sys.exit(main())
