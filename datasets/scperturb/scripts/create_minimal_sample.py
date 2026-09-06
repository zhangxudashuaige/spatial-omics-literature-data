#!/usr/bin/env python3
"""
创建最小 AnnData 示例，用于测试 E-distance 计算流程。

6 个细胞 × 4 个基因:
- 2 个 control 细胞
- 2 个 GeneA 扰动细胞
- 1 个 GeneB 扰动细胞
- 1 个 GeneA+GeneB 组合扰动细胞

固定随机种子，单文件小于 10 MiB。
注明不能用于复现论文指标。
"""
import sys
from pathlib import Path

import numpy as np
import anndata as ad

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"
OUTPUT = EXAMPLES_DIR / "minimal_perturbation.h5ad"


def create_minimal_sample():
    """创建最小扰动示例。"""
    np.random.seed(42)

    n_cells = 6
    n_genes = 4
    gene_names = ["GeneA", "GeneB", "GeneC", "GeneD"]

    # 细胞标签
    perturbations = [
        "control", "control",
        "GeneA", "GeneA",
        "GeneB",
        "GeneA+GeneB",
    ]

    # 基础表达 (control)
    base_expression = np.array([
        [10, 5, 20, 15],
        [12, 4, 18, 14],
    ], dtype=np.float32)

    # GeneA 扰动: GeneA 上调, GeneC 下调
    genea_expression = np.array([
        [50, 6, 5, 16],
        [48, 5, 6, 15],
    ], dtype=np.float32)

    # GeneB 扰动: GeneB 上调
    geneb_expression = np.array([
        [11, 40, 19, 14],
    ], dtype=np.float32)

    # GeneA+GeneB 组合扰动
    combo_expression = np.array([
        [55, 45, 4, 13],
    ], dtype=np.float32)

    X = np.vstack([base_expression, genea_expression, geneb_expression, combo_expression])

    # obs
    obs = {
        "perturbation": perturbations,
        "cell_type": ["K562"] * n_cells,
        "batch": ["batch1"] * n_cells,
    }

    # var
    var = {
        "gene_name": gene_names,
        "is_perturbation_target": [True, True, False, False],
    }

    # multi-hot 扰动矩阵
    gene_to_idx = {"GeneA": 0, "GeneB": 1}
    X_target = np.zeros((n_cells, 2), dtype=np.float32)
    for i, pert in enumerate(perturbations):
        if pert == "control":
            continue
        for g in pert.split("+"):
            if g in gene_to_idx:
                X_target[i, gene_to_idx[g]] = 1.0

    adata = ad.AnnData(
        X=X,
        obs=obs,
        var=var,
    )
    adata.obsm["X_target"] = X_target
    adata.uns["target_genes"] = ["GeneA", "GeneB"]
    adata.uns["description"] = (
        "Minimal perturbation example for E-distance testing. "
        "6 cells x 4 genes. NOT for reproducing paper metrics."
    )
    adata.uns["seed"] = 42

    return adata


def main():
    EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)

    print("[INFO] 创建最小 AnnData 示例...")
    adata = create_minimal_sample()

    print(f"[OK] 形状: {adata.shape}")
    print(f"[OK] 扰动: {dict(adata.obs['perturbation'].value_counts())}")
    print(f"[OK] X_target: {adata.obsm['X_target'].shape}")

    adata.write_h5ad(OUTPUT)
    size_kb = OUTPUT.stat().st_size / 1024
    print(f"[OK] 已保存: {OUTPUT} ({size_kb:.1f} KB)")
    print()
    print("[WARN] 此示例仅用于测试 E-distance 计算流程。")
    print("[WARN] 不能用于复现论文指标。")

    return 0


if __name__ == "__main__":
    sys.exit(main())
