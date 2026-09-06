#!/usr/bin/env python3
"""
检查生物先验嵌入。

功能:
- 打印先验名称
- 打印基因数
- 打印嵌入维度
- 打印数据类型
- 打印前5个基因名称
- 打印一个真实嵌入向量的前10维
- 打印缺失基因比例

用法:
    python inspect_prior_embeddings.py --prior genept
    python inspect_prior_embeddings.py --file data/priors/genept/embeddings.h5
"""
import sys
import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def human_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def inspect_h5_embeddings(filepath, prior_name):
    """检查 H5 格式的嵌入。"""
    try:
        import h5py
    except ImportError:
        print("[ERROR] h5py 未安装。请运行: pip install h5py")
        return 1

    path = Path(filepath)
    if not path.exists():
        print(f"[ERROR] 文件不存在: {filepath}")
        return 1

    print("=" * 70)
    print(f"先验嵌入检查: {prior_name}")
    print("=" * 70)
    print(f"文件: {path.resolve()}")
    print(f"大小: {human_size(path.stat().st_size)}")
    print()

    with h5py.File(path, "r") as f:
        print("--- H5 文件结构 ---")
        def print_structure(name, obj):
            if isinstance(obj, h5py.Dataset):
                print(f"  Dataset: {name}, shape={obj.shape}, dtype={obj.dtype}")
            elif isinstance(obj, h5py.Group):
                print(f"  Group: {name}")
        f.visititems(print_structure)

        # 尝试读取嵌入
        print("\n--- 嵌入数据 ---")
        embeddings = None
        gene_names = None

        # 常见的 key 名称
        for key in ["embeddings", "X", "data", "features", "vectors"]:
            if key in f:
                embeddings = np.array(f[key])
                print(f"  从 '{key}' 读取嵌入: shape={embeddings.shape}, dtype={embeddings.dtype}")
                break

        for key in ["genes", "gene_names", "index", "labels", "ids"]:
            if key in f:
                gene_names = [g.decode() if isinstance(g, bytes) else str(g) for g in f[key]]
                print(f"  从 '{key}' 读取基因名: {len(gene_names)} 个")
                break

        if embeddings is not None:
            print(f"\n  基因数: {embeddings.shape[0]}")
            print(f"  嵌入维度: {embeddings.shape[1]}")
            print(f"  数据类型: {embeddings.dtype}")
            print(f"  前5个基因: {gene_names[:5] if gene_names else 'N/A'}")

            # 一个真实嵌入向量的前10维
            print(f"\n  第一个基因的嵌入向量前10维:")
            print(f"    {embeddings[0, :10]}")

            # 统计
            print(f"\n  嵌入统计:")
            print(f"    均值: {embeddings.mean():.6f}")
            print(f"    标准差: {embeddings.std():.6f}")
            print(f"    最小值: {embeddings.min():.6f}")
            print(f"    最大值: {embeddings.max():.6f}")

    print("\n" + "=" * 70)
    print("检查完成")
    print("=" * 70)
    return 0


def inspect_npy_embeddings(filepath, prior_name):
    """检查 NPY 格式的嵌入。"""
    path = Path(filepath)
    if not path.exists():
        print(f"[ERROR] 文件不存在: {filepath}")
        return 1

    print("=" * 70)
    print(f"先验嵌入检查: {prior_name}")
    print("=" * 70)
    print(f"文件: {path.resolve()}")
    print(f"大小: {human_size(path.stat().st_size)}")

    embeddings = np.load(path)
    print(f"\n嵌入形状: {embeddings.shape}")
    print(f"数据类型: {embeddings.dtype}")
    print(f"基因数: {embeddings.shape[0]}")
    print(f"嵌入维度: {embeddings.shape[1]}")
    print(f"第一个基因嵌入前10维: {embeddings[0, :10]}")

    return 0


def inspect_csv_embeddings(filepath, prior_name):
    """检查 CSV 格式的嵌入。"""
    path = Path(filepath)
    if not path.exists():
        print(f"[ERROR] 文件不存在: {filepath}")
        return 1

    print("=" * 70)
    print(f"先验嵌入检查: {prior_name}")
    print("=" * 70)
    print(f"文件: {path.resolve()}")
    print(f"大小: {human_size(path.stat().st_size)}")

    df = pd.read_csv(path, index_col=0)
    print(f"\n形状: {df.shape} (基因 × 维度)")
    print(f"基因数: {len(df)}")
    print(f"嵌入维度: {df.shape[1]}")
    print(f"前5个基因: {list(df.index[:5])}")
    print(f"第一个基因嵌入前10维: {df.iloc[0, :10].values}")

    return 0


def main():
    parser = argparse.ArgumentParser(description="检查生物先验嵌入")
    parser.add_argument("--prior", choices=["genept", "esm2", "string", "depmap", "cell_painting", "scgpt"],
                        help="先验名称")
    parser.add_argument("--file", help="直接指定文件路径")
    args = parser.parse_args()

    if not args.prior and not args.file:
        print("[ERROR] 请指定 --prior 或 --file")
        return 1

    base_dir = Path(__file__).resolve().parent.parent

    if args.file:
        filepath = Path(args.file)
        prior_name = args.prior or filepath.stem
    else:
        prior_dir = base_dir / "data" / "priors" / args.prior
        if not prior_dir.exists():
            print(f"[ERROR] 先验目录不存在: {prior_dir}")
            print(f"[INFO] 请先运行 download_public_resources.py 下载先验数据。")
            return 1

        # 查找文件
        filepath = None
        for ext in ["*.h5", "*.hdf5", "*.npy", "*.csv", "*.tsv", "*.parquet"]:
            files = list(prior_dir.glob(ext))
            if files:
                filepath = files[0]
                break

        if not filepath:
            print(f"[ERROR] 在 {prior_dir} 中未找到嵌入文件。")
            print(f"[INFO] 目录内容: {list(prior_dir.iterdir())}")
            return 1

        prior_name = args.prior

    # 根据扩展名选择检查方式
    suffix = filepath.suffix.lower()
    if suffix in [".h5", ".hdf5"]:
        return inspect_h5_embeddings(filepath, prior_name)
    elif suffix == ".npy":
        return inspect_npy_embeddings(filepath, prior_name)
    elif suffix in [".csv", ".tsv", ".parquet"]:
        return inspect_csv_embeddings(filepath, prior_name)
    else:
        print(f"[ERROR] 不支持的文件格式: {suffix}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
