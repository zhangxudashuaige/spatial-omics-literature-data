#!/usr/bin/env python3
"""
验证 PerturbNet 数据文件的校验值。
"""
import sys
import argparse
import hashlib
from pathlib import Path


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
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def main():
    parser = argparse.ArgumentParser(description="验证 PerturbNet 数据文件")
    parser.add_argument("--path", required=True, help="文件或目录路径")
    parser.add_argument("--expected", default=None, help="预期 SHA256")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"[ERROR] 不存在: {path}")
        return 1

    if path.is_file():
        files = [path]
    else:
        files = [f for f in path.rglob("*") if f.is_file() and not f.name.startswith(".")]

    print(f"检查 {len(files)} 个文件...")
    print()

    for f in sorted(files):
        size = f.stat().st_size
        sha = compute_sha256(f)
        rel = f.relative_to(path) if path.is_dir() else f.name
        print(f"  {rel}: {human_size(size)}")
        print(f"    SHA256: {sha}")
        if args.expected and f.name == path.name:
            if sha.lower() == args.expected.lower():
                print("    [OK] 校验匹配")
            else:
                print("    [FAIL] 校验不匹配")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
