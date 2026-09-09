#!/usr/bin/env python3
"""检查 PRESAGE h5ad 文件：shape、X、layers、obs、var，避免大矩阵转稠密。"""
import sys, argparse
from pathlib import Path
import numpy as np

BASE = Path(__file__).resolve().parent.parent

def inspect_h5ad(filepath):
    try:
        import anndata
    except ImportError:
        print("[ERROR] anndata 未安装")
        return
    # backed模式避免加载大矩阵
    adata = anndata.read_h5ad(filepath, backed="r")
    print(f"文件: {Path(filepath).name}")
    print(f"形状: {adata.shape} (细胞 × 基因)")
    print(f"X dtype: {adata.X.dtype if hasattr(adata.X,'dtype') else 'unknown'}")
    from scipy.sparse import issparse
    print(f"X 稀疏: {issparse(adata.X)}")
    print(f"layers: {list(adata.layers.keys())}")
    print(f"obs 列: {list(adata.obs.columns)}")
    print(f"var 列: {list(adata.var.columns)}")
    print(f"obsm: {list(adata.obsm.keys())}")

    # 表达值类型（只取前1000细胞，不转稠密）
    subset = adata[:1000]
    vals = np.array(subset.X.todense()) if issparse(subset.X) else subset.X[:]
    has_neg = (vals < 0).any()
    is_int = np.all(vals == vals.astype(int)) if vals.size > 0 else False
    expr_type = "原始计数" if is_int and not has_neg else "归一化表达"
    print(f"表达类型: {expr_type}")

    # 扰动基因字段
    pert_cols = [c for c in adata.obs.columns if any(k in c.lower() for k in ["pert", "guide", "target", "condition"])]
    if pert_cols:
        print(f"\n扰动相关列: {pert_cols}")
        for col in pert_cols[:2]:
            counts = adata.obs[col].value_counts()
            print(f"\n  {col} (前10):")
            for val, cnt in counts.head(10).items():
                print(f"    {val}: {cnt} 细胞")
            # 非靶向对照
            nt = [v for v in counts.index if any(k in str(v).lower() for k in ["non-targeting", "nt_", "control", "ctrl"])]
            if nt:
                print(f"  非靶向对照: {nt} (共 {counts[nt].sum()} 细胞)")

    # 细胞类型/实验背景
    cell_cols = [c for c in adata.obs.columns if any(k in c.lower() for k in ["cell_type", "celltype", "cell_line", "background"])]
    if cell_cols:
        print(f"\n细胞类型列: {cell_cols}")
        for col in cell_cols[:1]:
            print(f"  {adata.obs[col].value_counts().to_string()}")

    # HVG
    if "hvg" in adata.var.columns:
        print(f"\nHVG基因数: {adata.var['hvg'].sum()} / {len(adata.var)}")
    print(f"\n基因数: {len(adata.var_names)}")
    print(f"基因重复: {adata.var_names.duplicated().sum()}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True)
    args = p.parse_args()
    f = Path(args.file)
    if not f.exists():
        print(f"[ERROR] 文件不存在: {f}")
        return 1
    inspect_h5ad(f)
    return 0

if __name__ == "__main__":
    sys.exit(main())
