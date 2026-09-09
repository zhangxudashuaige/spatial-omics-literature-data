#!/usr/bin/env python3
"""核验 PRESAGE 预处理：归一化对数表达减对照均值，按扰动求平均；HVG外补回被扰动基因。"""
import sys, argparse
from pathlib import Path
import numpy as np

BASE = Path(__file__).resolve().parent.parent

def verify_preprocessing(h5ad_path):
    try:
        import anndata
    except ImportError:
        print("[ERROR] anndata 未安装")
        return
    adata = anndata.read_h5ad(h5ad_path, backed="r")
    print(f"形状: {adata.shape}")

    # 检查表达值类型
    from scipy.sparse import issparse
    subset = adata[:1000]
    vals = np.array(subset.X.todense()) if issparse(subset.X) else subset.X[:]
    has_neg = (vals < 0).any()
    is_int = np.all(vals == vals.astype(int)) if vals.size > 0 else False
    print(f"表达类型: {'原始计数' if is_int and not has_neg else '归一化表达'}")
    print(f"含负值: {has_neg} (归一化对数表达可能含负值)")

    # 检查对照
    condition_cols = [c for c in adata.obs.columns if "condition" in c.lower()]
    pert_cols = [c for c in adata.obs.columns if any(k in c.lower() for k in ["pert", "guide", "target"])]
    print(f"\n条件列: {condition_cols}")
    print(f"扰动列: {pert_cols}")

    if condition_cols and pert_cols:
        cond_col = condition_cols[0]
        pert_col = pert_cols[0]
        ctrl_mask = adata.obs[cond_col].str.contains("control|ctrl", case=False, na=False)
        print(f"\n对照细胞数: {ctrl_mask.sum()}")
        print(f"扰动细胞数: {(~ctrl_mask).sum()}")
        print(f"扰动数: {adata[~ctrl_mask].obs[pert_col].nunique()}")

    # HVG检查
    if "hvg" in adata.var.columns:
        n_hvg = adata.var["hvg"].sum()
        print(f"\nHVG基因数: {n_hvg} / {len(adata.var)}")
        if n_hvg > 0 and n_hvg < len(adata.var):
            print("[INFO] 存在非HVG基因，可能是被补回的扰动基因")
            non_hvg = adata.var[~adata.var["hvg"]].index.tolist()
            print(f"非HVG基因(前10): {non_hvg[:10]}")
    else:
        print(f"\n基因数: {len(adata.var)}")
        print("[INFO] 无HVG标记，输出基因数可能不等于5000")

    print(f"\n=== 预处理核验结论 ===")
    print("预期预处理: 归一化对数表达 - 对照均值 -> 按扰动求平均")
    print("HVG之外可能补回被扰动基因，输出不一定只有5,000列")
    print("需手动验证: 对照均值是否已扣除，平均响应是否按扰动聚合")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True)
    args = p.parse_args()
    f = Path(args.file)
    if not f.exists():
        print(f"[ERROR] 文件不存在: {f}")
        return 1
    verify_preprocessing(f)
    return 0

if __name__ == "__main__":
    sys.exit(main())
