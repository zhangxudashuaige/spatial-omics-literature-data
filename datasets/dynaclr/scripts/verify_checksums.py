#!/usr/bin/env python3
"""校验文件 SHA256。"""
import sys, argparse, hashlib
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True)
    p.add_argument("--expected", help="期望的SHA256")
    args = p.parse_args()
    f = Path(args.file)
    if not f.exists():
        print(f"[ERROR] 文件不存在: {f}")
        return 1
    actual = sha256_file(f)
    print(f"文件: {f.name}")
    print(f"SHA256: {actual}")
    if args.expected:
        if actual == args.expected:
            print("[OK] 校验通过")
        else:
            print(f"[ERROR] 校验不匹配")
            print(f"  期望: {args.expected}")
            print(f"  实际: {actual}")
            return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
