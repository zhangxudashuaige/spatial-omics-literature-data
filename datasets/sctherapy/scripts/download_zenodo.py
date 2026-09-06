#!/usr/bin/env python3
"""
从 Zenodo 下载 scTherapy 处理后的 Seurat 对象。

Zenodo 记录: https://doi.org/10.5281/zenodo.13340927

优先下载处理后 Seurat 对象，读取文件清单、大小和校验值。
不盲目下载全部 LINCS、PharmacoDB 和 SRA 原始数据。
"""
import sys
import argparse
from pathlib import Path
from urllib.request import urlretrieve

import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
ZENODO_RECORD = "13340927"
ZENODO_API = f"https://zenodo.org/api/records/{ZENODO_RECORD}"


def human_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def fetch_zenodo_files():
    """从 Zenodo API 获取文件清单。"""
    print(f"[INFO] 获取 Zenodo 记录: {ZENODO_RECORD}")
    print(f"       API: {ZENODO_API}")

    try:
        resp = requests.get(ZENODO_API, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[ERROR] API 请求失败: {e}")
        return []

    files = data.get("files", [])
    print(f"[OK] 获取到 {len(files)} 个文件")
    print()

    results = []
    for f in files:
        results.append({
            "filename": f.get("key", ""),
            "size": f.get("size", 0),
            "url": f.get("links", {}).get("self", ""),
            "checksum": f.get("checksum", "").replace("md5:", ""),
        })

    return results


def download_file(url, dest):
    """下载文件。"""
    print(f"[INFO] 下载: {url}")
    print(f"       保存到: {dest}")

    def report_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, downloaded * 100 / total_size)
            mb_dl = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            print(f"\r  进度: {percent:.1f}% ({mb_dl:.1f}/{mb_total:.1f} MB)", end="", flush=True)

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
    parser = argparse.ArgumentParser(description="下载 scTherapy Zenodo 处理后数据")
    parser.add_argument("--list", action="store_true", help="仅列出文件，不下载")
    parser.add_argument("--file", default=None, help="下载指定文件名")
    parser.add_argument("--all", action="store_true", help="下载所有文件 (警告: 可能很大)")
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    files = fetch_zenodo_files()
    if not files:
        print("[ERROR] 未获取到文件。")
        return 1

    # 列出文件
    print("=" * 70)
    print("Zenodo 文件清单")
    print("=" * 70)
    total_size = 0
    for f in files:
        size_mb = f["size"] / (1024 * 1024)
        total_size += f["size"]
        print(f"  {f['filename']}: {size_mb:.1f} MB (md5: {f['checksum'][:16]}...)")
    print(f"  总计: {human_size(total_size)}")
    print()

    if args.list:
        return 0

    # 确定要下载的文件
    if args.all:
        to_download = files
        print("[WARN] 下载所有文件，可能需要大量磁盘空间。")
    elif args.file:
        to_download = [f for f in files if f["filename"] == args.file]
        if not to_download:
            print(f"[ERROR] 未找到文件: {args.file}")
            return 1
    else:
        # 默认: 提示用户选择
        print("[INFO] 使用 --file <filename> 下载指定文件，或 --all 下载全部。")
        print("[INFO] 推荐优先下载 Seurat 对象 (.rds) 文件。")
        return 0

    # 下载
    for f in to_download:
        dest = DATA_DIR / f["filename"]
        if dest.exists():
            print(f"[SKIP] 已存在: {dest}")
            continue
        download_file(f["url"], dest)

    print()
    print("[DONE] 下载完成。")
    print(f"[INFO] 文件保存在: {DATA_DIR}")
    print("[INFO] 下一步: Rscript scripts/inspect_seurat.R <file.rds>")

    return 0


if __name__ == "__main__":
    sys.exit(main())
