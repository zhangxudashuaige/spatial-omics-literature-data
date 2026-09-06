#!/usr/bin/env python3
"""
将 Norman 2019 CRISPRa (GSE133344) 数据整理成 AnnData 文件。

输出: data/processed/norman_crispra.h5ad

要求:
- .X 或 .layers["counts"] 保存原始整数计数
- .obs 保存扰动标签
- .var 保存基因信息
- .obsm["X_target"] 保存 multi-hot 扰动矩阵
- .obsm["X_covar"] 保存协变量矩阵
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import anndata as ad
from scipy.sparse import csr_matrix

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = PROCESSED_DIR / "norman_crispra.h5ad"


def load_from_gears_processed():
    """
    优先使用 GEARS 官方预处理的 Norman 数据。
    GEARS 的 PertData 已经整理好了 Norman 数据，包含扰动标签。
    """
    try:
        from gears import PertData
        print("[INFO] 使用 GEARS PertData 加载 Norman 数据...")
        pert_data = PertData(str(RAW_DIR.parent))
        pert_data.load(data_name="norman")
        adata = pert_data.adata.copy()
        print(f"[OK] 加载成功: {adata.shape}")
        return adata
    except ImportError:
        print("[WARN] gears 未安装，尝试从原始文件构建...")
        return None
    except Exception as e:
        print(f"[WARN] GEARS 加载失败: {e}")
        return None


def build_from_raw():
    """
    从 GEO 原始补充文件构建 AnnData。
    需要: 计数矩阵、基因列表、细胞 barcode、扰动标签。
    """
    print("[INFO] 从原始文件构建 AnnData...")
    print("[WARN] 此功能需要原始文件已下载并解压。")
    print("[WARN] 请确保 data/raw/ 下包含计数矩阵和扰动标签文件。")
    print()

    # 查找可能的计数矩阵文件
    count_files = list(RAW_DIR.glob("*count*")) + list(RAW_DIR.glob("*matrix*"))
    if not count_files:
        print("[ERROR] 未找到计数矩阵文件。")
        print("[ERROR] 请先运行: python scripts/download_norman_geo.py")
        return None

    print(f"[INFO] 找到候选文件: {[f.name for f in count_files]}")
    print("[INFO] 请根据实际文件格式调整读取代码。")
    return None


def add_cellcap_inputs(adata):
    """
    为 AnnData 添加 CellCap 需要的输入矩阵:
    - .obsm["X_target"]: multi-hot 扰动矩阵
    - .obsm["X_covar"]: 协变量矩阵
    """
    print("[INFO] 构建 X_target (multi-hot 扰动矩阵)...")

    # 获取扰动基因列表
    if "condition" in adata.obs.columns:
        condition_col = "condition"
    elif "perturbation" in adata.obs.columns:
        condition_col = "perturbation"
    else:
        print("[WARN] 未找到扰动标签列 (condition/perturbation)")
        condition_col = None

    if condition_col:
        # 解析扰动条件，格式如 "A+B" 或 "ctrl"
        all_genes = set()
        conditions = adata.obs[condition_col].unique()
        for cond in conditions:
            if cond in ["ctrl", "control", ""]:
                continue
            genes = str(cond).split("+")
            all_genes.update(genes)

        gene_list = sorted(all_genes)
        gene_to_idx = {g: i for i, g in enumerate(gene_list)}
        print(f"[INFO] 扰动基因数: {len(gene_list)}")

        # 构建 multi-hot 矩阵
        X_target = np.zeros((adata.n_obs, len(gene_list)), dtype=np.float32)
        for i, cond in enumerate(adata.obs[condition_col]):
            if cond in ["ctrl", "control", ""]:
                continue
            for g in str(cond).split("+"):
                if g in gene_to_idx:
                    X_target[i, gene_to_idx[g]] = 1.0

        adata.obsm["X_target"] = X_target
        adata.uns["target_genes"] = gene_list
        print(f"[OK] X_target 形状: {X_target.shape}")

    # 构建协变量矩阵
    print("[INFO] 构建 X_covar (协变量矩阵)...")
    covar_features = []

    # 总计数
    if "n_counts" in adata.obs.columns:
        covar_features.append(adata.obs["n_counts"].values.astype(np.float32))
    elif adata.X is not None:
        totals = np.asarray(adata.X.sum(axis=1)).flatten()
        covar_features.append(totals.astype(np.float32))

    # 检测基因数
    if "n_genes" in adata.obs.columns:
        covar_features.append(adata.obs["n_genes"].values.astype(np.float32))
    elif adata.X is not None:
        from scipy.sparse import issparse
        if issparse(adata.X):
            n_genes = np.asarray((adata.X > 0).sum(axis=1)).flatten()
        else:
            n_genes = (adata.X > 0).sum(axis=1)
        covar_features.append(n_genes.astype(np.float32))

    if covar_features:
        X_covar = np.column_stack(covar_features)
        # 标准化
        X_covar = (X_covar - X_covar.mean(axis=0)) / (X_covar.std(axis=0) + 1e-8)
        adata.obsm["X_covar"] = X_covar.astype(np.float32)
        print(f"[OK] X_covar 形状: {X_covar.shape}")

    return adata


def ensure_counts_layer(adata):
    """确保 .layers['counts'] 包含原始整数计数。"""
    if "counts" in adata.layers:
        print("[OK] .layers['counts'] 已存在")
        return adata

    if adata.X is not None:
        # 检查 X 是否为整数计数
        X_data = adata.X
        from scipy.sparse import issparse
        if issparse(X_data):
            sample = X_data.data[:1000]
        else:
            sample = X_data.flatten()[:1000]

        is_integer = np.all(sample == sample.astype(int))
        if is_integer:
            adata.layers["counts"] = X_data.copy()
            print("[OK] .X 为整数计数，已复制到 .layers['counts']")
        else:
            print("[WARN] .X 不是整数计数，无法确定原始计数。")
            print("[WARN] 请从原始文件获取计数矩阵。")

    return adata


def main():
    print("=" * 60)
    print("Norman 2019 CRISPRa → AnnData 预处理")
    print("=" * 60)
    print()

    # 优先使用 GEARS 预处理数据
    adata = load_from_gears_processed()

    if adata is None:
        adata = build_from_raw()

    if adata is None:
        print("[ERROR] 无法加载数据。")
        print("[ERROR] 请安装 gears: pip install cell-gears")
        print("[ERROR] 或先从 GEO 下载原始数据。")
        return 1

    # 确保计数层
    adata = ensure_counts_layer(adata)

    # 添加 CellCap 输入
    adata = add_cellcap_inputs(adata)

    # 保存
    print(f"[INFO] 保存到: {OUTPUT}")
    adata.write_h5ad(OUTPUT)
    size_mb = OUTPUT.stat().st_size / (1024 * 1024)
    print(f"[OK] 保存完成 ({size_mb:.1f} MB)")

    # 打印摘要
    print()
    print("=" * 60)
    print("AnnData 摘要")
    print("=" * 60)
    print(f"形状: {adata.shape}")
    print(f"obs 字段: {list(adata.obs.columns)}")
    print(f"var 字段: {list(adata.var.columns)}")
    print(f"layers: {list(adata.layers.keys())}")
    print(f"obsm: {list(adata.obsm.keys())}")
    if "condition" in adata.obs.columns:
        print(f"扰动条件数: {adata.obs['condition'].nunique()}")
        print(f"前10个条件: {list(adata.obs['condition'].unique()[:10])}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
