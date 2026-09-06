#!/usr/bin/env python3
"""
验证下载文件的 MD5 校验值。

从 metadata/files.csv 或 metadata/checksums.csv 获取预期 MD5，
与实际计算的 MD5 比较。
"""
import sys
import argparse
import csv
import hashlib
from pathlib import Path

METADATA_DIR = Path(__file__).resolve().parent.parent / "metadata"


def compute_md5(filepath, chunk_size=8192):
    """计算文件的 MD5。"""
    md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            md5.update(chunk)
    return md5.hexdigest()


def get_expected_md5(filename):
    """从元数据文件获取预期 MD5。"""
    # 先查 files.csv
    files_csv = METADATA_DIR / "files.csv"
    if files_csv.exists():
        with open(files_csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["filename"] == filename and row.get("md5"):
                    return row["md5"], "files.csv"

    # 再查 checksums.csv
    checksums_csv = METADATA_DIR / "checksums.csv"
    if checksums_csv.exists():
        with open(checksums_csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["filename"] == filename and row.get("md5"):
                    return row["md5"], "checksums.csv"

    return None, None


def main():
    parser = argparse.ArgumentParser(description="验证文件 MD5")
    parser.add_argument("filepath", help="要验证的文件路径")
    parser.add_argument("--expected", default=None, help="预期 MD5 (不指定则从元数据查找)")
    args = parser.parse_args()

    filepath = Path(args.filepath)
    if not filepath.exists():
        print(f"[ERROR] 文件不存在: {filepath}")
        return 1

    print(f"[INFO] 文件: {filepath}")
    size_mb = filepath.stat().st_size / (1024 * 1024)
    print(f"[INFO] 大小: {size_mb:.2f} MB")

    # 计算实际 MD5
    print("[INFO] 计算 MD5...")
    actual_md5 = compute_md5(filepath)
    print(f"[INFO] 实际 MD5: {actual_md5}")

    # 获取预期 MD5
    expected_md5 = args.expected
    source = "命令行参数"
    if not expected_md5:
        expected_md5, source = get_expected_md5(filepath.name)

    if not expected_md5:
        print("[WARN] 未找到预期 MD5 值。")
        print("[WARN] 请从 Zenodo 页面获取官方 MD5，或运行 fetch_zenodo_manifest.py 更新元数据。")
        print(f"[INFO] 实际 MD5 已记录: {actual_md5}")
        return 2

    print(f"[INFO] 预期 MD5: {expected_md5} (来源: {source})")

    # 比较
    if actual_md5.lower() == expected_md5.lower():
        print("[OK] MD5 校验通过！文件完整。")
        return 0
    else:
        print("[FAIL] MD5 不匹配！文件可能损坏或不完整。")
        print(f"       预期: {expected_md5}")
        print(f"       实际: {actual_md5}")
        print("[INFO] 建议重新下载文件。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
