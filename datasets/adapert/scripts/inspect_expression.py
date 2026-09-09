#!/usr/bin/env python3
"""检查表达矩阵：形状、X类型、稀疏性、obs/var、扰动标签、表达值类型。"""
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
    adata = anndata.read_h5ad(filepath)
    print(f"形状: {adata.shape} (细胞 × 基因)")
    print(f"X dtype: {adata.X.dtype if hasattr(adata.X,'dtype') else 'unknown'}")
    from scipy.sparse import issparse
    print(f"稀疏: {issparse(adata.X)}")
    print(f"obs 列: {list(adata.obs.columns)}")
    print(f"var 列: {list(adata.var.columns)}")
    print(f"layers: {list(adata.layers.keys())}")
    print(f"obsm: {list(adata.obsm.keys())}")

    # 表达值类型
    vals = np.array(adata.X[:1000].todense()) if issparse(adata.X) else adata.X[:1000]
    has_neg = (vals < 0).any()
    is_int = np.all(vals == vals.astype(int)) if vals.size > 0 else False
    expr_type = "原始计数" if is_int and not has_neg else "归一化表达"
    print(f"表达类型: {expr_type}")

    # 扰动标签
    pert_cols = [c for c in adata.obs.columns if any(k in c.lower() for k in ["pert", "guide", "target", "condition"])]
    if pert_cols:
        print(f"\n扰动相关列: {pert_cols}")
        for col in pert_cols[:2]:
            counts = adata.obs[col].value_counts()
            print(f"\n  {col} (前10):")
            for val, cnt in counts.head(10).items():
                print(f"    {val}: {cnt} 细胞")
            ctrl = [v for v in counts.index if any(k in str(v).lower() for k in ["control", "ctrl", "nt", "non-targeting"])]
            if ctrl:
                print(f"  对照组: {ctrl} (共 {counts[ctrl].sum()} 细胞)")

    # 一个扰动的平均表达变化
    if "perturbation" in adata.obs.columns and "condition" in adata.obs.columns:
        perts = adata.obs[adata.obs["condition"] == "perturbed"]["perturbation"].unique()
        if len(perts) > 0:
            p = perts[0]
            ctrl_mask = adata.obs["condition"] == "control"
            pert_mask = (adata.obs["condition"] == "perturbed") & (adata.obs["perturbation"] == p)
            if ctrl_mask.sum() > 0 and pert_mask.sum() > 0:
                ctrl_mean = np.array(adata[ctrl_mask].X.mean(axis=0)).flatten()
                pert_mean = np.array(adata[pert_mask].X.mean(axis=0)).flatten()
                diff = pert_mean - ctrl_mean
                print(f"\n扰动 {p}: {pert_mask.sum()} 细胞")
                print(f"  平均表达变化 top5 基因:")
                top_idx = np.argsort(np.abs(diff))[-5:][::-1]
                for idx in top_idx:
                    gene = adata.var_names[idx] if idx < len(adata.var_names) else f"gene_{idx}"
                    print(f"    {gene}: {diff[idx]:.4f}")

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
    else:
        print(f"[WARN] 不支持的格式: {f.suffix}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
