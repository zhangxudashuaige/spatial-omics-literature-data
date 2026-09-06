#!/usr/bin/env python3
"""
检查 h5ad 数据文件。

功能:
- 打印 AnnData 形状
- 打印 X 的数据类型和稀疏格式
- 打印 obs 列名
- 打印 var 列名
- 打印前5个扰动标签
- 打印前5个细胞类型
- 打印对照细胞数量
- 打印各扰动细胞数量
- 检查是否已经 CP10K/log1p 归一化

用法:
    python inspect_h5ad.py --file data/evaluation/replogle_nadig/example.h5ad
"""
import sys
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import anndata
    HAS_ANNDATA = True
except ImportError:
    HAS_ANNDATA = False


def human_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def is_normalized(adata):
    """检查是否已经归一化。"""
    X = adata.X
    # 检查是否有整数计数（未归一化）
    if hasattr(X, "dtype"):
        if np.issubdtype(X.dtype, np.integer):
            return False, "整数计数（未归一化）"

    # 检查最大值
    try:
        if hasattr(X, "max"):
            max_val = float(X.max())
        else:
            max_val = float(np.max(X))
        if max_val <= 100:
            return True, f"最大值 {max_val:.2f}，可能已 log1p 归一化"
        elif max_val <= 10000:
            return True, f"最大值 {max_val:.2f}，可能已 CP10K 归一化"
        else:
            return False, f"最大值 {max_val:.2f}，可能是原始计数"
    except Exception:
        return None, "无法判断"


def inspect_h5ad(filepath):
    """检查 h5ad 文件。"""
    path = Path(filepath)

    if not path.exists():
        print(f"[ERROR] 文件不存在: {filepath}")
        return 1

    if not HAS_ANNDATA:
        print("[ERROR] anndata 未安装。请运行: pip install anndata")
        return 1

    # 文件大小
    file_size = path.stat().st_size
    print("=" * 70)
    print("h5ad 文件检查")
    print("=" * 70)
    print(f"文件路径: {path.resolve()}")
    print(f"文件大小: {human_size(file_size)}")
    print()

    # 读取
    try:
        adata = anndata.read_h5ad(path)
    except Exception as e:
        print(f"[ERROR] 读取失败: {e}")
        return 1

    # 基本信息
    print("--- 基本信息 ---")
    print(f"AnnData 形状: {adata.shape} (细胞 × 基因)")
    print(f"X 数据类型: {adata.X.dtype if hasattr(adata.X, 'dtype') else 'unknown'}")

    # 稀疏性
    from scipy.sparse import issparse
    print(f"是否稀疏矩阵: {issparse(adata.X)}")
    if issparse(adata.X):
        print(f"稀疏格式: {adata.X.format}")
        print(f"非零元素: {adata.X.nnz}")
        print(f"稀疏度: {100 * (1 - adata.X.nnz / (adata.shape[0] * adata.shape[1])):.2f}%")

    # 归一化检查
    norm, norm_msg = is_normalized(adata)
    print(f"归一化状态: {norm_msg}")

    # obs
    print(f"\n--- obs (细胞元数据) ---")
    print(f"列数: {len(adata.obs.columns)}")
    print(f"列名: {list(adata.obs.columns)}")
    if len(adata.obs) > 0:
        print(f"前5行:")
        print(adata.obs.head().to_string())

    # var
    print(f"\n--- var (基因元数据) ---")
    print(f"列数: {len(adata.var.columns)}")
    print(f"列名: {list(adata.var.columns)}")
    if len(adata.var) > 0:
        print(f"前5个基因: {list(adata.var_names[:5])}")

    # layers
    print(f"\n--- layers ---")
    print(f"layers: {list(adata.layers.keys())}")
    for layer_name in adata.layers:
        layer = adata.layers[layer_name]
        print(f"  {layer_name}: shape={layer.shape}, dtype={layer.dtype if hasattr(layer, 'dtype') else 'unknown'}")

    # obsm
    print(f"\n--- obsm ---")
    print(f"obsm: {list(adata.obsm.keys())}")
    for key in adata.obsm:
        val = adata.obsm[key]
        print(f"  {key}: shape={val.shape}")

    # 扰动标签
    print(f"\n--- 扰动标签 ---")
    perturbation_cols = [c for c in adata.obs.columns
                         if any(kw in c.lower() for kw in ["perturb", "condition", "guide", "target", "gene"])]
    if perturbation_cols:
        for col in perturbation_cols:
            print(f"\n列: {col}")
            print(f"  唯一值数: {adata.obs[col].nunique()}")
            print(f"  前5个值: {list(adata.obs[col].unique()[:5])}")
            # 细胞数量统计
            counts = adata.obs[col].value_counts()
            print(f"  前10个扰动的细胞数:")
            for val, cnt in counts.head(10).items():
                print(f"    {val}: {cnt}")
    else:
        print("  未找到明显的扰动列。请检查 obs 列名。")

    # 细胞类型
    print(f"\n--- 细胞类型 ---")
    celltype_cols = [c for c in adata.obs.columns
                      if any(kw in c.lower() for kw in ["cell_type", "celltype", "cell type", "cluster", "label"])]
    if celltype_cols:
        for col in celltype_cols:
            print(f"\n列: {col}")
            print(f"  唯一值数: {adata.obs[col].nunique()}")
            print(f"  前5个值: {list(adata.obs[col].unique()[:5])}")
    else:
        print("  未找到明显的细胞类型列。")

    # 对照细胞
    print(f"\n--- 对照细胞 ---")
    control_keywords = ["control", "ctrl", "nt", "non-targeting", "wildtype", "wt", "unperturbed"]
    control_count = 0
    for col in adata.obs.columns:
        if adata.obs[col].dtype == object or str(adata.obs[col].dtype).startswith("category"):
            for val in adata.obs[col].unique():
                if any(kw in str(val).lower() for kw in control_keywords):
                    cnt = (adata.obs[col] == val).sum()
                    print(f"  对照: {col}={val}, 细胞数: {cnt}")
                    control_count += cnt
    if control_count == 0:
        print("  未自动识别到对照细胞。请手动检查 obs。")

    print("\n" + "=" * 70)
    print("检查完成")
    print("=" * 70)

    return 0


def main():
    parser = argparse.ArgumentParser(description="检查 h5ad 数据文件")
    parser.add_argument("--file", required=True, help="h5ad 文件路径")
    args = parser.parse_args()

    return inspect_h5ad(args.file)


if __name__ == "__main__":
    sys.exit(main())
