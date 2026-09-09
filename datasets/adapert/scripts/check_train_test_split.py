#!/usr/bin/env python3
"""检查训练/测试划分：扰动级划分，防止同一扰动细胞随机分到训练和测试。"""
import sys, argparse
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent

def check_split(adata_path, split_col="split", pert_col="perturbation"):
    try:
        import anndata
    except ImportError:
        print("[ERROR] anndata 未安装")
        return
    adata = anndata.read_h5ad(adata_path, backed="r")
    print(f"形状: {adata.shape}")

    if split_col not in adata.obs.columns:
        print(f"[WARN] 未找到划分列 '{split_col}'")
        print(f"可用列: {list(adata.obs.columns)}")
        return

    if pert_col not in adata.obs.columns:
        print(f"[WARN] 未找到扰动列 '{pert_col}'")
        return

    splits = adata.obs[split_col].unique()
    print(f"划分: {list(splits)}")

    # 检查同一扰动是否出现在多个划分中
    pert_split = adata.obs.groupby(pert_col)[split_col].nunique()
    leaked = pert_split[pert_split > 1]
    if len(leaked) > 0:
        print(f"\n[ERROR] 发现数据泄漏: {len(leaked)} 个扰动出现在多个划分中")
        print(f"  前10个: {list(leaked.index[:10])}")
    else:
        print(f"\n[OK] 无数据泄漏: 每个扰动只出现在一个划分中")

    # 各划分扰动数
    for s in splits:
        mask = adata.obs[split_col] == s
        perts = adata.obs[mask][pert_col].nunique()
        print(f"  {s}: {mask.sum()} 细胞, {perts} 个扰动")

    # 检查是否为官方划分
    print(f"\n划分来源: {'官方' if 'official' in str(adata.uns.get('split_source', '')) else '需确认'}")
    print("注意: 如果找不到官方划分，自建划分必须明确标注为自建，不能声称复现论文数值。")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True)
    p.add_argument("--split-col", default="split")
    p.add_argument("--pert-col", default="perturbation")
    args = p.parse_args()
    f = Path(args.file)
    if not f.exists():
        print(f"[ERROR] 文件不存在: {f}")
        return 1
    check_split(f, args.split_col, args.pert_col)
    return 0

if __name__ == "__main__":
    sys.exit(main())
