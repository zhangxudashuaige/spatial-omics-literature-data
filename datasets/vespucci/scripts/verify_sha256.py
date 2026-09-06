#!/usr/bin/env python3
"""
验证文件 SHA256 校验值。

功能:
- 读取 checksums/ 目录中的 .sha256 文件
- 计算对应文件的实际 SHA256
- 比较并报告匹配/不匹配
- 列出所有已校验文件

用法:
    python verify_sha256.py
    python verify_sha256.py --file data/processed/GSE268779/matrix.mtx
"""
import sys
import os
import argparse
import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CHECKSUM_DIR = BASE_DIR / "checksums"


def compute_sha256(filepath, chunk_size=8192):
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            sha.update(chunk)
    return sha.hexdigest()


def human_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def find_checksum_files():
    """查找所有 .sha256 文件。"""
    if not CHECKSUM_DIR.exists():
        return []
    return list(CHECKSUM_DIR.glob("*.sha256"))


def parse_checksum_file(checksum_path):
    """解析 .sha256 文件，返回 (expected_hash, filename)。"""
    with open(checksum_path, "r") as f:
        line = f.readline().strip()
    parts = line.split(None, 1)
    if len(parts) == 2:
        return parts[0], parts[1].lstrip("*")
    return None, None


def find_data_file(filename):
    """在项目中查找数据文件。"""
    search_dirs = [
        BASE_DIR / "data" / "processed",
        BASE_DIR / "data" / "simulated",
        BASE_DIR / "data" / "external",
        BASE_DIR / "data" / "external" / "geo_metadata",
    ]
    for d in search_dirs:
        if d.exists():
            for f in d.rglob(filename):
                if f.is_file():
                    return f
    return None


def verify_all():
    """验证所有校验文件。"""
    checksum_files = find_checksum_files()

    print("=" * 70)
    print("SHA256 校验验证")
    print("=" * 70)
    print(f"校验目录: {CHECKSUM_DIR}")
    print(f"校验文件数: {len(checksum_files)}")
    print()

    if not checksum_files:
        print("[WARN] 未找到校验文件。")
        print("[INFO] 运行下载脚本后会自动生成校验文件。")
        return 0

    passed = 0
    failed = 0
    missing = 0

    for cs_file in sorted(checksum_files):
        expected_hash, filename = parse_checksum_file(cs_file)

        if not expected_hash or not filename:
            print(f"[WARN] 无法解析: {cs_file.name}")
            continue

        data_file = find_data_file(filename)

        if not data_file:
            print(f"[MISSING] {filename} (校验文件: {cs_file.name})")
            missing += 1
            continue

        actual_hash = compute_sha256(data_file)
        size = data_file.stat().st_size

        if actual_hash.lower() == expected_hash.lower():
            print(f"[PASS] {filename} ({human_size(size)})")
            print(f"       SHA256: {actual_hash[:32]}...")
            passed += 1
        else:
            print(f"[FAIL] {filename} ({human_size(size)})")
            print(f"       预期: {expected_hash}")
            print(f"       实际: {actual_hash}")
            failed += 1

    print()
    print("=" * 70)
    print("验证结果")
    print("=" * 70)
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"缺失: {missing}")
    print()

    if failed > 0:
        print("[WARN] 有文件校验失败，可能已损坏。建议重新下载。")
        return 1
    if missing > 0:
        print("[INFO] 有文件缺失（可能尚未下载）。")

    print("[OK] 所有已存在文件校验通过。")
    return 0


def verify_single(filepath):
    """验证单个文件。"""
    p = Path(filepath)
    if not p.exists():
        print(f"[ERROR] 文件不存在: {filepath}")
        return 1

    actual_hash = compute_sha256(p)
    size = p.stat().st_size

    print(f"文件: {p.name}")
    print(f"大小: {human_size(size)}")
    print(f"SHA256: {actual_hash}")
    print()

    # 检查是否有对应的校验文件
    cs_file = CHECKSUM_DIR / f"{p.name}.sha256"
    if cs_file.exists():
        expected_hash, _ = parse_checksum_file(cs_file)
        if expected_hash:
            if actual_hash.lower() == expected_hash.lower():
                print("[PASS] 与校验文件匹配")
                return 0
            else:
                print("[FAIL] 与校验文件不匹配!")
                print(f"  预期: {expected_hash}")
                return 1
    else:
        print("[INFO] 无对应校验文件。")
        print(f"[INFO] 可创建: {cs_file}")

    return 0


def main():
    parser = argparse.ArgumentParser(description="验证 SHA256 校验值")
    parser.add_argument("--file", default=None, help="验证单个文件")
    args = parser.parse_args()

    if args.file:
        return verify_single(args.file)
    else:
        return verify_all()


if __name__ == "__main__":
    sys.exit(main())
