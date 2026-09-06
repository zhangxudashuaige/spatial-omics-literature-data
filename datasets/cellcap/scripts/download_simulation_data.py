#!/usr/bin/env python3
"""
下载 CellCap 模拟数据 (simulation_data.h5ad)。

优先从官方仓库获取；如果官方仓库未直接提供该文件，
则提示用户按官方教程中的下载指令操作，不伪造链接。
"""
import os
import sys
import subprocess
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

TARGET = RAW_DIR / "simulation_data.h5ad"

# 官方仓库中可能的位置（不保证存在，需实际检查）
OFFICIAL_REPO = "https://github.com/broadinstitute/CellCap"
POSSIBLE_PATHS = [
    "data/simulation_data.h5ad",
    "simulation_data.h5ad",
    "tutorials/data/simulation_data.h5ad",
]


def check_official_repo():
    """检查官方仓库是否包含 simulation_data.h5ad。"""
    print(f"[INFO] 检查官方仓库: {OFFICIAL_REPO}")
    print("[INFO] 可能的路径:")
    for p in POSSIBLE_PATHS:
        print(f"       - {p}")
    print("[INFO] 请手动确认官方仓库中该文件的实际位置和下载方式。")
    print("[INFO] 如果文件通过 Git LFS 管理，需要安装 git-lfs 后 clone。")
    return False


def download_with_gdown(url, output):
    """使用 gdown 下载 Google Drive 文件。"""
    try:
        import gdown
        gdown.download(url, str(output), quiet=False)
        return True
    except ImportError:
        print("[ERROR] gdown 未安装。请运行: pip install gdown")
        return False
    except Exception as e:
        print(f"[ERROR] 下载失败: {e}")
        return False


def main():
    if TARGET.exists():
        size_mb = TARGET.stat().st_size / (1024 * 1024)
        print(f"[OK] 文件已存在: {TARGET} ({size_mb:.1f} MB)")
        return 0

    print("=" * 60)
    print("CellCap 模拟数据下载")
    print("=" * 60)
    print()

    # 尝试检查官方仓库
    found = check_official_repo()

    if not found:
        print()
        print("[WARN] 无法自动确定 simulation_data.h5ad 的下载链接。")
        print("[WARN] 请按以下步骤手动获取:")
        print(f"       1. 访问官方仓库: {OFFICIAL_REPO}")
        print("       2. 查找教程文档中关于 simulation_data 的下载说明")
        print("       3. 将文件放置到: data/raw/simulation_data.h5ad")
        print("       4. 运行: python scripts/inspect_h5ad.py data/raw/simulation_data.h5ad")
        print()
        print("[INFO] 不伪造下载链接。以官方仓库当前页面为准。")
        return 1

    print(f"[OK] 下载完成: {TARGET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
