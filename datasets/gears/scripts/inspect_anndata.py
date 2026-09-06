#!/usr/bin/env python3
"""
检查 AnnData 数据结构，用于 GEARS 数据验证。

输出:
- adata.shape
- .X 数据类型和稀疏性
- obs 字段
- var 字段
- 所有扰动条件
- 对照细胞数量
- 单扰动数量
- 组合扰动数量
- 每种扰动的细胞数量
- 基因名称是否完整
- condition 和 cell_type 字段是否满足 GEARS 要求
"""
import sys
import argparse
from pathlib import Path

import numpy as np
import anndata as ad


def inspect_anndata(path):
    """检查 AnnData 文件。"""
    p = Path(path)
    if not p.exists():
        print(f"[ERROR] 文件不存在: {path}")
        return 1

    print("=" * 70)
    print(f"AnnData 检查: {p.name}")
    print("=" * 70)
    print(f"文件大小: {p.stat().st_size / (1024*1024):.1f} MB")
    print()

    adata = ad.read_h5ad(p)

    # 形状
    print(f"形状: {adata.n_obs} 细胞 × {adata.n_vars} 基因")
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
            print(f"非零元素: {adata.X.nnz}")
    print()

    # obs
    print("-" * 70)
    print("obs 字段")
    print("-" * 70)
    for col in adata.obs.columns:
        print(f"  - {col}: dtype={adata.obs[col].dtype}, unique={adata.obs[col].nunique()}")
    print()

    # var
    print("-" * 70)
    print("var 字段")
    print("-" * 70)
    for col in adata.var.columns:
        print(f"  - {col}: dtype={adata.var[col].dtype}, unique={adata.var[col].nunique()}")
    print()

    # 基因名称完整性
    print("-" * 70)
    print("基因名称检查")
    print("-" * 70)
    gene_names = adata.var_names
    n_empty = sum(1 for g in gene_names if not g or str(g).strip() == "")
    n_duplicate = gene_names.duplicated().sum()
    print(f"基因总数: {len(gene_names)}")
    print(f"空名称: {n_empty}")
    print(f"重复名称: {n_duplicate}")
    print(f"名称完整: {'是' if n_empty == 0 and n_duplicate == 0 else '否'}")
    print(f"前10个基因: {list(gene_names[:10])}")
    print()

    # 扰动条件
    print("-" * 70)
    print("扰动条件统计")
    print("-" * 70)

    has_condition = "condition" in adata.obs.columns
    has_cell_type = "cell_type" in adata.obs.columns

    print(f"condition 字段存在: {'是' if has_condition else '否'}")
    print(f"cell_type 字段存在: {'是' if has_cell_type else '否'}")
    print()

    if has_condition:
        conditions = adata.obs["condition"].value_counts()
        print(f"总条件数: {len(conditions)}")
        print()

        # 分类统计
        ctrl_count = 0
        single_count = 0
        combo_count = 0
        single_conditions = []
        combo_conditions = []

        for cond, cnt in conditions.items():
            cond_str = str(cond)
            if cond_str.lower() in ["ctrl", "control", ""]:
                ctrl_count += cnt
            elif "+" in cond_str:
                combo_count += cnt
                combo_conditions.append((cond, cnt))
            else:
                single_count += cnt
                single_conditions.append((cond, cnt))

        print(f"对照细胞: {ctrl_count}")
        print(f"单扰动细胞: {single_count} ({len(single_conditions)} 种)")
        print(f"组合扰动细胞: {combo_count} ({len(combo_conditions)} 种)")
        print()

        print("前20种扰动 (细胞数):")
        for cond, cnt in conditions.head(20).items():
            print(f"  {cond}: {cnt}")
    else:
        print("[WARN] 缺少 condition 字段，GEARS 无法直接使用。")
    print()

    # GEARS 要求检查
    print("-" * 70)
    print("GEARS 兼容性检查")
    print("-" * 70)
    gears_ready = True
    if not has_condition:
        print("  [FAIL] 缺少 condition 字段")
        gears_ready = False
    else:
        print("  [OK] condition 字段存在")

    if not has_cell_type:
        print("  [WARN] 缺少 cell_type 字段 (部分 GEARS 功能需要)")
    else:
        print("  [OK] cell_type 字段存在")

    if adata.X is None:
        print("  [FAIL] .X 为空")
        gears_ready = False
    else:
        print("  [OK] .X 存在")

    print()
    print(f"GEARS 可直接使用: {'是' if gears_ready else '否'}")
    print()

    print("=" * 70)
    print("检查完成")
    print("=" * 70)
    return 0


def main():
    parser = argparse.ArgumentParser(description="检查 AnnData 结构")
    parser.add_argument("path", help="h5ad 文件路径")
    args = parser.parse_args()
    return inspect_anndata(args.path)


if __name__ == "__main__":
    sys.exit(main())
