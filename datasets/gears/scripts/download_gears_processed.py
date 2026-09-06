#!/usr/bin/env python3
"""
下载 GEARS 官方预处理的数据。

使用 GEARS 的 PertData 加载器自动下载并预处理:
- norman (Norman 2019, GSE133344)
- adamson (Adamson 2016, GSE90546)
- dixit (Dixit 2016, GSE90063)

Replogle 数据名称以官方当前支持为准，不自行猜测。
"""
import sys
import argparse
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def download_dataset(name):
    """使用 GEARS PertData 下载并加载数据集。"""
    try:
        from gears import PertData
    except ImportError:
        print("[ERROR] gears 未安装。请运行: pip install cell-gears")
        return False

    print(f"[INFO] 下载/加载 GEARS 预处理数据: {name}")
    print(f"[INFO] 数据目录: {DATA_DIR}")

    try:
        pert_data = PertData(str(DATA_DIR))
        pert_data.load(data_name=name)
        adata = pert_data.adata
        print(f"[OK] 加载成功: {name}")
        print(f"     形状: {adata.shape}")
        print(f"     obs 字段: {list(adata.obs.columns)}")
        print(f"     条件数: {adata.obs['condition'].nunique() if 'condition' in adata.obs else 'N/A'}")
        return True
    except Exception as e:
        print(f"[ERROR] 加载失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="下载 GEARS 官方预处理数据")
    parser.add_argument("--dataset", default="norman",
                        choices=["norman", "adamson", "dixit", "all"],
                        help="要下载的数据集")
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if args.dataset == "all":
        datasets = ["norman", "adamson", "dixit"]
    else:
        datasets = [args.dataset]

    results = {}
    for name in datasets:
        print()
        print("=" * 60)
        results[name] = download_dataset(name)

    print()
    print("=" * 60)
    print("下载总结")
    print("=" * 60)
    for name, ok in results.items():
        status = "成功" if ok else "失败"
        print(f"  {name}: {status}")

    print()
    print("[INFO] Replogle 数据: 请检查 GEARS 官方当前支持的数据集名称。")
    print("[INFO] 不自行猜测不存在的数据集名称。")

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
