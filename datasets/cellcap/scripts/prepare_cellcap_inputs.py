#!/usr/bin/env python3
"""
准备 CellCap 模型需要的输入矩阵。

从 AnnData 中提取:
- X: 表达矩阵 (细胞 × 基因)
- X_target: multi-hot 扰动矩阵 (细胞 × 扰动基因)
- X_covar: 协变量矩阵 (细胞 × 协变量)

用法:
    python scripts/prepare_cellcap_inputs.py data/processed/norman_crispra.h5ad
"""
import sys
import argparse
from pathlib import Path

import numpy as np
import anndata as ad


def load_anndata(path):
    """加载 AnnData 文件。"""
    print(f"[INFO] 加载: {path}")
    adata = ad.read_h5ad(path)
    print(f"[OK] 形状: {adata.shape}")
    return adata


def get_expression_matrix(adata, layer=None):
    """获取表达矩阵。"""
    if layer and layer in adata.layers:
        X = adata.layers[layer]
        print(f"[INFO] 使用 layer['{layer}'] 作为 X")
    elif "counts" in adata.layers:
        X = adata.layers["counts"]
        print("[INFO] 使用 .layers['counts'] 作为 X")
    else:
        X = adata.X
        print("[INFO] 使用 .X 作为 X")
    return X


def get_target_matrix(adata):
    """获取或构建 multi-hot 扰动矩阵。"""
    if "X_target" in adata.obsm:
        X_target = adata.obsm["X_target"]
        print(f"[INFO] 使用已有的 .obsm['X_target']: {X_target.shape}")
        return X_target

    # 从 obs 构建
    condition_col = None
    for col in ["condition", "perturbation", "perturb", "guide"]:
        if col in adata.obs.columns:
            condition_col = col
            break

    if condition_col is None:
        print("[WARN] 未找到扰动标签列，X_target 将为零矩阵")
        return np.zeros((adata.n_obs, 1), dtype=np.float32)

    # 解析扰动基因
    all_genes = set()
    for cond in adata.obs[condition_col].unique():
        if str(cond).lower() in ["ctrl", "control", ""]:
            continue
        genes = str(cond).replace(" ", "").split("+")
        all_genes.update(genes)

    gene_list = sorted(all_genes)
    gene_to_idx = {g: i for i, g in enumerate(gene_list)}

    X_target = np.zeros((adata.n_obs, len(gene_list)), dtype=np.float32)
    for i, cond in enumerate(adata.obs[condition_col]):
        if str(cond).lower() in ["ctrl", "control", ""]:
            continue
        for g in str(cond).replace(" ", "").split("+"):
            if g in gene_to_idx:
                X_target[i, gene_to_idx[g]] = 1.0

    print(f"[INFO] 构建 X_target: {X_target.shape}, 扰动基因: {len(gene_list)}")
    return X_target


def get_covariate_matrix(adata):
    """获取或构建协变量矩阵。"""
    if "X_covar" in adata.obsm:
        X_covar = adata.obsm["X_covar"]
        print(f"[INFO] 使用已有的 .obsm['X_covar']: {X_covar.shape}")
        return X_covar

    features = []
    feature_names = []

    # 总计数
    if "n_counts" in adata.obs.columns:
        features.append(adata.obs["n_counts"].values.astype(np.float32))
        feature_names.append("n_counts")
    elif adata.X is not None:
        from scipy.sparse import issparse
        if issparse(adata.X):
            totals = np.asarray(adata.X.sum(axis=1)).flatten()
        else:
            totals = np.asarray(adata.X.sum(axis=1)).flatten()
        features.append(totals.astype(np.float32))
        feature_names.append("n_counts")

    # 检测基因数
    if "n_genes" in adata.obs.columns:
        features.append(adata.obs["n_genes"].values.astype(np.float32))
        feature_names.append("n_genes")
    elif adata.X is not None:
        from scipy.sparse import issparse
        if issparse(adata.X):
            n_genes = np.asarray((adata.X > 0).sum(axis=1)).flatten()
        else:
            n_genes = np.asarray((adata.X > 0).sum(axis=1)).flatten()
        features.append(n_genes.astype(np.float32))
        feature_names.append("n_genes")

    # 细胞周期 (如果有)
    for cc_col in ["S_score", "G2M_score", "phase"]:
        if cc_col in adata.obs.columns:
            if adata.obs[cc_col].dtype.kind in "fi":
                features.append(adata.obs[cc_col].values.astype(np.float32))
                feature_names.append(cc_col)

    if features:
        X_covar = np.column_stack(features)
        # 标准化
        mean = X_covar.mean(axis=0)
        std = X_covar.std(axis=0) + 1e-8
        X_covar = (X_covar - mean) / std
        print(f"[INFO] 构建 X_covar: {X_covar.shape}, 特征: {feature_names}")
        return X_covar.astype(np.float32)

    print("[WARN] 无法构建协变量矩阵，返回零矩阵")
    return np.zeros((adata.n_obs, 1), dtype=np.float32)


def main():
    parser = argparse.ArgumentParser(description="准备 CellCap 输入矩阵")
    parser.add_argument("h5ad_path", help="AnnData 文件路径")
    parser.add_argument("--layer", default=None, help="使用的表达层 (如 counts)")
    parser.add_argument("--output", default=None, help="输出 npz 路径")
    args = parser.parse_args()

    adata = load_anndata(args.h5ad_path)
    X = get_expression_matrix(adata, args.layer)
    X_target = get_target_matrix(adata)
    X_covar = get_covariate_matrix(adata)

    print()
    print("=" * 60)
    print("CellCap 输入矩阵摘要")
    print("=" * 60)
    print(f"X (表达):        {X.shape}, dtype={X.dtype if hasattr(X, 'dtype') else 'sparse'}")
    print(f"X_target (扰动): {X_target.shape}, 非零比例: {(X_target > 0).mean():.3f}")
    print(f"X_covar (协变量): {X_covar.shape}")

    # 保存为 npz
    if args.output:
        from scipy.sparse import issparse, save_npz
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        np.savez(
            out,
            X_target=X_target,
            X_covar=X_covar,
            gene_names=adata.var_names.values,
            cell_names=adata.obs_names.values,
        )
        if issparse(X):
            save_npz(str(out).replace(".npz", "_X.npz"), X.tocsr())
        print(f"[OK] 已保存到: {out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
