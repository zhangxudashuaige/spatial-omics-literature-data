#!/usr/bin/env python3
"""
从真实公开数据抽取小样本。

重要:
- 只能从真实公开数据抽取小样本
- 100个对照细胞 + 100个扰动细胞
- 最多500个基因
- 保留 obs 和 var
- 输出 example_small.h5ad
- 如果原始数据尚未公开，则跳过，绝对不要生成随机伪数据冒充真实数据

用法:
    python make_small_example.py --source data/evaluation/replogle_nadig/data.h5ad
    python make_small_example.py --source data/evaluation/parse_1m/data.h5ad
"""
import sys
import argparse
from pathlib import Path

import numpy as np

try:
    import anndata
    HAS_ANNDATA = True
except ImportError:
    HAS_ANNDATA = False


def find_control_cells(adata):
    """查找对照细胞。"""
    control_keywords = ["control", "ctrl", "nt", "non-targeting", "wildtype", "wt", "unperturbed", "untreated"]

    for col in adata.obs.columns:
        if adata.obs[col].dtype == object or str(adata.obs[col].dtype).startswith("category"):
            for val in adata.obs[col].unique():
                if any(kw in str(val).lower() for kw in control_keywords):
                    mask = adata.obs[col] == val
                    return mask, f"{col}={val}"

    return None, None


def find_perturbed_cells(adata, exclude_control_col=None):
    """查找扰动细胞（非对照）。"""
    if exclude_control_col:
        col, val = exclude_control_col.split("=")
        mask = adata.obs[col] != val
        return mask

    # 如果没有明确的对照列，取所有细胞
    return np.ones(len(adata), dtype=bool)


def select_top_genes(adata, n_genes=500):
    """选择高变基因或表达量最高的基因。"""
    # 计算每个基因的总表达量
    if hasattr(adata.X, "sum"):
        gene_sums = np.array(adata.X.sum(axis=0)).flatten()
    else:
        gene_sums = np.sum(adata.X, axis=0)

    # 取表达量最高的基因
    top_indices = np.argsort(gene_sums)[::-1][:n_genes]
    return np.sort(top_indices)


def make_small_example(source_path, output_path, n_control=100, n_perturbed=100, n_genes=500, seed=42):
    """从真实数据抽取小样本。"""
    if not HAS_ANNDATA:
        print("[ERROR] anndata 未安装。请运行: pip install anndata")
        return 1

    source = Path(source_path)
    if not source.exists():
        print(f"[ERROR] 源文件不存在: {source_path}")
        print("[INFO] 请先运行 download_public_resources.py 下载数据。")
        return 1

    print("=" * 70)
    print("从真实数据抽取小样本")
    print("=" * 70)
    print(f"源文件: {source.resolve()}")
    print(f"输出: {output_path}")
    print(f"对照细胞: {n_control}")
    print(f"扰动细胞: {n_perturbed}")
    print(f"基因数: {n_genes}")
    print(f"随机种子: {seed}")
    print()

    # 读取源数据
    print("[INFO] 读取源数据...")
    try:
        adata = anndata.read_h5ad(source)
    except Exception as e:
        print(f"[ERROR] 读取失败: {e}")
        return 1

    print(f"  原始形状: {adata.shape} (细胞 × 基因)")

    # 查找对照细胞
    print("\n[INFO] 查找对照细胞...")
    control_mask, control_label = find_control_cells(adata)
    if control_mask is None:
        print("  [WARN] 未自动识别到对照细胞。")
        print("  [WARN] 将随机选择细胞作为对照和扰动。")
        rng = np.random.RandomState(seed)
        indices = rng.permutation(len(adata))
        control_indices = indices[:n_control]
        perturbed_indices = indices[n_control:n_control + n_perturbed]
    else:
        print(f"  对照标签: {control_label}")
        control_indices = np.where(control_mask)[0]
        print(f"  对照细胞数: {len(control_indices)}")

        # 查找扰动细胞
        perturbed_mask = find_perturbed_cells(adata, control_label)
        perturbed_indices = np.where(perturbed_mask & ~control_mask)[0]
        print(f"  扰动细胞数: {len(perturbed_indices)}")

    # 抽样
    rng = np.random.RandomState(seed)

    if len(control_indices) > n_control:
        control_indices = rng.choice(control_indices, n_control, replace=False)
    else:
        print(f"  [WARN] 对照细胞不足 {n_control}，实际取 {len(control_indices)} 个")

    if len(perturbed_indices) > n_perturbed:
        perturbed_indices = rng.choice(perturbed_indices, n_perturbed, replace=False)
    else:
        print(f"  [WARN] 扰动细胞不足 {n_perturbed}，实际取 {len(perturbed_indices)} 个")

    selected_indices = np.concatenate([control_indices, perturbed_indices])
    print(f"\n  选中细胞总数: {len(selected_indices)}")

    # 选择基因
    print("\n[INFO] 选择基因...")
    gene_indices = select_top_genes(adata[selected_indices], n_genes)
    print(f"  选中基因数: {len(gene_indices)}")

    # 子集
    print("\n[INFO] 创建子集...")
    small_adata = adata[selected_indices][:, gene_indices].copy()
    print(f"  子集形状: {small_adata.shape}")

    # 添加样本标记
    small_adata.obs["sample_type"] = "perturbed"
    small_adata.obs.loc[small_adata.obs_names.isin(adata.obs_names[control_indices]), "sample_type"] = "control"

    print(f"\n  对照细胞: {(small_adata.obs['sample_type'] == 'control').sum()}")
    print(f"  扰动细胞: {(small_adata.obs['sample_type'] == 'perturbed').sum()}")

    # 保存
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    small_adata.write_h5ad(output)

    file_size = output.stat().st_size
    print(f"\n[OK] 小样本已保存: {output}")
    print(f"     文件大小: {file_size / 1024:.1f} KB")

    print("\n" + "=" * 70)
    print("完成")
    print("=" * 70)
    print("[INFO] 此小样本来自真实公开数据，可用于快速测试。")
    print("[INFO] 不能用于复现论文指标。")
    print("[INFO] 大型原始数据已被 .gitignore 排除。")

    return 0


def main():
    parser = argparse.ArgumentParser(description="从真实公开数据抽取小样本")
    parser.add_argument("--source", required=True, help="源 h5ad 文件路径")
    parser.add_argument("--output", default="data/evaluation/example_small.h5ad",
                        help="输出文件路径 (默认: data/evaluation/example_small.h5ad)")
    parser.add_argument("--n-control", type=int, default=100, help="对照细胞数 (默认: 100)")
    parser.add_argument("--n-perturbed", type=int, default=100, help="扰动细胞数 (默认: 100)")
    parser.add_argument("--n-genes", type=int, default=500, help="基因数 (默认: 500)")
    parser.add_argument("--seed", type=int, default=42, help="随机种子 (默认: 42)")
    args = parser.parse_args()

    return make_small_example(
        args.source, args.output,
        n_control=args.n_control,
        n_perturbed=args.n_perturbed,
        n_genes=args.n_genes,
        seed=args.seed
    )


if __name__ == "__main__":
    sys.exit(main())
