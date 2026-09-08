#!/usr/bin/env python3
"""检查扰动数据：矩阵形状、表达类型、细胞元数据、guide与靶基因关系、扰动细胞数。"""
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
    expr_type = "原始计数" if is_int and not has_neg else "归一化表达"
    print(f"表达类型: {expr_type}")

    # 扰动标签
    pert_cols = [c for c in adata.obs.columns if any(k in c.lower() for k in ["pert", "guide", "target", "condition", "drug"])]
    if pert_cols:
        print(f"\n扰动相关列: {pert_cols}")
        for col in pert_cols[:3]:
            counts = adata.obs[col].value_counts()
            print(f"\n  {col} (前10):")
            for val, cnt in counts.head(10).items():
                print(f"    {val}: {cnt} 细胞")
            # 对照组
            ctrl_keywords = ["control", "ctrl", "nt", "non-targeting", "vehicle", "dmso"]
            ctrls = [v for v in counts.index if any(k in str(v).lower() for k in ctrl_keywords)]
            if ctrls:
                print(f"  对照组: {ctrls} (共 {counts[ctrls].sum()} 细胞)")
    else:
        print("\n未自动识别到扰动列，请手动检查obs。")

    # guide与靶基因关系
    if "guide_id" in adata.obs.columns and "target_gene" in adata.obs.columns:
        guide_target = adata.obs[["guide_id", "target_gene"]].drop_duplicates()
        print(f"\nguide-靶基因对: {len(guide_target)}")
        print(guide_target.head(10).to_string(index=False))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True)
    args = p.parse_args()
    f = Path(args.file)
    if not f.exists():
        print(f"[ERROR] 文件不存在: {f}")
        return 1
    print(f"文件: {f.name} ({f.stat().st_size / 1024 / 1024:.1f} MB)")
    if f.suffix == ".h5ad":
        inspect_h5ad(f)
    elif f.suffix in [".csv", ".tsv"]:
        df = pd.read_csv(f, index_col=0)
        print(f"形状: {df.shape}")
        print(f"列: {list(df.columns[:10])}")
    else:
        print(f"[WARN] 不支持的格式: {f.suffix}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
