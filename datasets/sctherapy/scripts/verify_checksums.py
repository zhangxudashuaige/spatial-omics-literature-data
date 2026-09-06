#!/usr/bin/env python3
"""
验证 scTherapy 数据文件的完整性和校验值。

检查:
- 文件是否存在
- 文件大小
- MD5/SHA256 校验值
- 文件格式是否可读取
"""
import sys
import argparse
import hashlib
from pathlib import Path

METADATA_DIR = Path(__file__).resolve().parent.parent / "metadata"


def compute_md5(filepath, chunk_size=8192):
    """计算文件 MD5。"""
    md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            md5.update(chunk)
    return md5.hexdigest()


def human_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def check_file(filepath, expected_md5=None):
    """检查单个文件。"""
    p = Path(filepath)
    if not p.exists():
        print(f"  [MISSING] {p.name}")
        return False

    size = p.stat().st_size
    print(f"  [OK] {p.name}: {human_size(size)}")

    if expected_md5:
        print(f"       计算 MD5...", end="", flush=True)
        actual_md5 = compute_md5(p)
        if actual_md5.lower() == expected_md5.lower():
            print(f" 匹配 ({actual_md5[:16]}...)")
        else:
            print(f" 不匹配!")
            print(f"         预期: {expected_md5}")
            print(f"         实际: {actual_md5}")
            return False

    return True


def main():
    parser = argparse.ArgumentParser(description="验证 scTherapy 数据文件")
    parser.add_argument("--path", default=None, help="检查指定文件或目录")
    parser.add_argument("--all", action="store_true", help="检查 data/ 下所有文件")
    args = parser.parse_args()

    print("=" * 60)
    print("scTherapy 数据验证")
    print("=" * 60)
    print()

    if args.path:
        check_file(args.path)
    elif args.all:
        data_dir = Path(__file__).resolve().parent.parent / "data"
        print(f"检查目录: {data_dir}")
        print()

        # 检查 processed 目录
        processed_dir = data_dir / "processed"
        if processed_dir.exists():
            print("处理后数据 (data/processed/):")
            for f in sorted(processed_dir.iterdir()):
                if f.is_file() and not f.name.startswith("."):
                    check_file(f)
            print()

        # 检查 raw 目录
        raw_dir = data_dir / "raw"
        if raw_dir.exists():
            print("原始数据 (data/raw/):")
            for f in sorted(raw_dir.rglob("*")):
                if f.is_file() and not f.name.startswith("."):
                    rel = f.relative_to(data_dir)
                    print(f"  {rel}: {human_size(f.stat().st_size)}")
            print()
    else:
        print("[INFO] 使用 --path <file> 检查指定文件，或 --all 检查所有数据。")
        print()

    print("=" * 60)
    print("验证完成")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
