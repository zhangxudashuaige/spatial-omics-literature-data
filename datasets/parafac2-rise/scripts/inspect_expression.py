#!/usr/bin/env python3
"""检查表达矩阵：行列方向、细胞ID对应、基因ID完整性、表达值类型。"""
import sys, argparse
from pathlib import Path
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent.parent

def inspect_h5ad(filepath):
    try:
        import anndata
    except ImportError:
        print("[ERROR] anndata 未安装")
        return
    adata = anndata.read_h5ad(filepath)
    print(f"形状: {adata.shape} (细胞 × 基因)")
    print(f"X dtype: {adata.X.dtype if hasattr(adata.X,'dtype') else 'unknown'}")
    from scipy.sparse import issparse
    print(f"稀疏: {issparse(adata.X)}")
    print(f"obs 列: {list(adata.obs.columns)}")
    print(f"var 列: {list(adata.var.columns)}")
    # 表达值类型
    vals = np.array(adata.X[:1000].todense()) if issparse(adata.X) else adata.X[:1000]
    has_neg = (vals < 0).any()
    is_int = np.all(vals == vals.astype(int)) if vals.size > 0 else False
    print(f"含负值: {has_neg}, 全整数: {is_int}")
    print(f"表达类型: {'原始计数' if is_int and not has_neg else '归一化表达'}")
    # 基因重复
    print(f"基因重复: {adata.var_names.duplicated().sum()}")
    # 细胞ID对应
    print(f"细胞ID唯一: {adata.obs_names.is_unique}")

def inspect_csv(filepath):
    df = pd.read_csv(filepath, index_col=0)
    print(f"形状: {df.shape}")
    print(f"索引: {df.index.name or '未命名'} (前5: {list(df.index[:5])})")
    print(f"列: 前5 {list(df.columns[:5])}")
    print(f"dtype: {df.dtypes.iloc[0]}")
    vals = df.values.flatten()[:10000]
    has_neg = (vals < 0).any()
    is_int = np.all(vals == vals.astype(int))
    print(f"含负值: {has_neg}, 全整数: {is_int}")
    print(f"表达类型: {'原始计数' if is_int and not has_neg else '归一化表达'}")
    print(f"行重复: {df.index.duplicated().sum()}, 列重复: {df.columns.duplicated().sum()}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True)
    args = p.parse_args()
    f = Path(args.file)
    if not f.exists():
        print(f"[ERROR] 文件不存在: {f}")
        return 1
    print(f"文件: {f.name} ({f.stat().st_size / 1024:.1f} KB)")
    if f.suffix == ".h5ad":
        inspect_h5ad(f)
    elif f.suffix in [".csv", ".tsv", ".txt"]:
        inspect_csv(f)
    else:
        print(f"[WARN] 不支持的格式: {f.suffix}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
