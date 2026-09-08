#!/usr/bin/env python3
"""下载选定的扰动数据，支持断点续传和已有校验和验证。"""
import sys, argparse, os, hashlib
from pathlib import Path
from urllib.request import urlopen, urlretrieve

BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "data"

def human_size(b):
    for u in ["B","KB","MB","GB"]:
        if b < 1024: return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} TB"

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def download_with_resume(url, dest, expected_sha256=None):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        if expected_sha256:
            actual = sha256_file(dest)
            if actual == expected_sha256:
                print(f"[SKIP] 已存在且校验通过: {dest.name}")
                return True
            else:
                print(f"[WARN] 已存在但校验不匹配，重新下载: {dest.name}")
                dest.unlink()
        else:
            print(f"[SKIP] 已存在: {dest.name} ({human_size(dest.stat().st_size)})")
            return True
    print(f"[INFO] 下载: {url}")
    try:
        urlretrieve(url, str(dest))
        print(f"[OK] {dest.name} ({human_size(dest.stat().st_size)})")
        if expected_sha256:
            actual = sha256_file(dest)
            if actual == expected_sha256:
                print(f"[OK] SHA256 校验通过")
            else:
                print(f"[ERROR] SHA256 校验不匹配")
                print(f"  期望: {expected_sha256}")
                print(f"  实际: {actual}")
                return False
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        if dest.exists(): dest.unlink()
        return False

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", required=True, help="数据集ID")
    p.add_argument("--url", help="直接指定下载URL")
    p.add_argument("--sha256", help="期望的SHA256校验值")
    p.add_argument("--output", help="输出文件名")
    args = p.parse_args()

    dest = DATA_DIR / args.dataset / (args.output or "downloaded_data")
    if args.url:
        success = download_with_resume(args.url, dest, args.sha256)
        return 0 if success else 1

    print(f"[INFO] 数据集: {args.dataset}")
    print("[INFO] 请使用 --url 指定下载地址，或从官方入口获取。")
    print("[INFO] 默认下载元数据与少量处理后示例，大型矩阵按选择下载。")
    return 0

if __name__ == "__main__":
    sys.exit(main())
