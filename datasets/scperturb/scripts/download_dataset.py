#!/usr/bin/env python3
"""
从 Zenodo 下载指定的 scPerturb 数据集。

不默认下载全部 43 GB。首先只下载:
- AdamsonWeissman2016_GSM2406675_10X001.h5ad (~34.6 MB)

再根据磁盘空间选择是否下载:
- NormanWeissman2019_filtered.h5ad (~698.7 MB)
"""
import sys
import argparse
import csv
from pathlib import Path
from urllib.request import urlretrieve

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
METADATA_DIR = Path(__file__).resolve().parent.parent / "metadata"


def human_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def download_file(url, dest):
    """下载文件，带进度显示。"""
    print(f"[INFO] 下载: {url}")
    print(f"       保存到: {dest}")

    def report_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, downloaded * 100 / total_size)
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            print(f"\r  进度: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end="", flush=True)

    try:
        urlretrieve(url, str(dest), reporthook=report_hook)
        print()
        size_mb = dest.stat().st_size / (1024 * 1024)
        print(f"[OK] 下载完成 ({size_mb:.1f} MB)")
        return True
    except Exception as e:
        print()
        print(f"[ERROR] 下载失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="下载 scPerturb 数据集")
    parser.add_argument("--file", required=True, help="要下载的文件名 (如 AdamsonWeissman2016_GSM2406675_10X001.h5ad)")
    parser.add_argument("--record", default="13350497", help="Zenodo 记录 ID")
    parser.add_argument("--force", action="store_true", help="强制重新下载")
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 从 files.csv 查找下载链接
    files_csv = METADATA_DIR / "files.csv"
    url = None
    expected_size = 0

    if files_csv.exists():
        with open(files_csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["filename"] == args.file:
                    url = row.get("download_url", "")
                    expected_size = int(row.get("file_size_bytes", 0))
                    break

    if not url:
        # 构造 Zenodo 直接下载链接
        url = f"https://zenodo.org/records/{args.record}/files/{args.file}?download=1"
        print(f"[WARN] files.csv 中未找到 {args.file}，使用构造的链接")

    dest = DATA_DIR / args.file

    if dest.exists() and not args.force:
        size_mb = dest.stat().st_size / (1024 * 1024)
        print(f"[OK] 文件已存在: {dest} ({size_mb:.1f} MB)")
        print("[INFO] 使用 --force 重新下载")
        return 0

    if expected_size > 0:
        print(f"[INFO] 预期大小: {human_size(expected_size)}")

    # 大文件警告
    if expected_size > 500 * 1024 * 1024:
        print()
        print("[WARN] 这是一个大文件 (>500 MB)。")
        print("[WARN] 请确认磁盘空间充足。")
        print("[WARN] 下载的文件不会进入 Git (已被 .gitignore 排除)。")
        print()

    success = download_file(url, dest)

    if success:
        actual_size = dest.stat().st_size
        if expected_size > 0 and abs(actual_size - expected_size) > expected_size * 0.01:
            print(f"[WARN] 实际大小 ({human_size(actual_size)}) 与预期 ({human_size(expected_size)}) 不符")
        print()
        print("[INFO] 下一步: 运行 MD5 校验")
        print(f"       python scripts/verify_md5.py {dest}")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
