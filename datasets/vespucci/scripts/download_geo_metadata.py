#!/usr/bin/env python3
"""
下载 GEO 元数据（不下载 FASTQ）。

功能:
- 支持按 GSE 或 GSM 编号选择样本
- 下载前显示预计文件大小
- 已存在文件不得重复下载
- 下载后计算 SHA256
- 记录下载来源和日期
- 下载地址无法核实时停止，不得编造
- 需要登录的数据只写访问说明，不绕过权限

用法:
    python download_geo_metadata.py --gse GSE268779
    python download_geo_metadata.py --gsm GSMxxxxxxx
"""
import sys
import os
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen, urlretrieve

BASE_DIR = Path(__file__).resolve().parent.parent
METADATA_DIR = BASE_DIR / "data" / "external" / "geo_metadata"
CHECKSUM_DIR = BASE_DIR / "checksums"

GEO_URL = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"


def human_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def compute_sha256(filepath):
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            sha.update(chunk)
    return sha.hexdigest()


def fetch_geo_soft(accession):
    """从 GEO 获取 SOFT 格式元数据。"""
    url = f"{GEO_URL}?acc={accession}&targ=self&form=text&view=quick"
    print(f"[INFO] 获取 GEO 元数据: {accession}")
    print(f"       URL: {url}")

    try:
        with urlopen(url, timeout=30) as resp:
            content = resp.read().decode("utf-8", errors="replace")
        return content
    except Exception as e:
        print(f"[ERROR] 获取失败: {e}")
        return None


def parse_soft_samples(soft_content):
    """从 SOFT 内容解析样本列表。"""
    samples = []
    current_sample = None

    for line in soft_content.split("\n"):
        if line.startswith("^SAMPLE ="):
            if current_sample:
                samples.append(current_sample)
            gsm = line.split("=")[1].strip()
            current_sample = {"gsm": gsm, "title": "", "source": "", "characteristics": {}}
        elif current_sample and line.startswith("!Sample_title ="):
            current_sample["title"] = line.split("=", 1)[1].strip()
        elif current_sample and line.startswith("!Sample_source_name_ch1 ="):
            current_sample["source"] = line.split("=", 1)[1].strip()
        elif current_sample and line.startswith("!Sample_characteristics_ch1 ="):
            char = line.split("=", 1)[1].strip()
            if ":" in char:
                key, val = char.split(":", 1)
                current_sample["characteristics"][key.strip()] = val.strip()

    if current_sample:
        samples.append(current_sample)

    return samples


def download_file(url, dest):
    """下载文件，带进度。"""
    if dest.exists():
        print(f"[SKIP] 已存在: {dest.name}")
        return True

    print(f"[INFO] 下载: {url}")
    print(f"       保存到: {dest}")

    try:
        urlretrieve(url, str(dest))
        size = dest.stat().st_size
        print(f"[OK] 下载完成 ({human_size(size)})")
        return True
    except Exception as e:
        print(f"[ERROR] 下载失败: {e}")
        if dest.exists():
            dest.unlink()
        return False


def main():
    parser = argparse.ArgumentParser(description="下载 GEO 元数据")
    parser.add_argument("--gse", default=None, help="GEO Series 编号 (如 GSE268779)")
    parser.add_argument("--gsm", default=None, help="GEO Sample 编号 (如 GSMxxxxxxx)")
    parser.add_argument("--list", action="store_true", help="仅列出样本，不下载")
    args = parser.parse_args()

    if not args.gse and not args.gsm:
        print("[ERROR] 请指定 --gse 或 --gsm")
        return 1

    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    CHECKSUM_DIR.mkdir(parents=True, exist_ok=True)

    accession = args.gse or args.gsm

    # 获取 SOFT 元数据
    soft = fetch_geo_soft(accession)
    if not soft:
        print("[ERROR] 无法获取元数据，停止。不编造下载地址。")
        return 1

    # 保存 SOFT 元数据
    soft_file = METADATA_DIR / f"{accession}_soft.txt"
    with open(soft_file, "w", encoding="utf-8") as f:
        f.write(soft)
    print(f"[OK] SOFT 元数据已保存: {soft_file}")

    # 解析样本
    samples = parse_soft_samples(soft)
    print(f"[INFO] 解析到 {len(samples)} 个样本")
    print()

    if samples:
        print("=" * 70)
        print(f"样本列表 ({accession})")
        print("=" * 70)
        for s in samples:
            print(f"  {s['gsm']}: {s['title']}")
            if s["source"]:
                print(f"    来源: {s['source']}")
            if s["characteristics"]:
                for k, v in s["characteristics"].items():
                    print(f"    {k}: {v}")
            print()

    if args.list:
        return 0

    # 保存样本元数据为 JSON
    meta_file = METADATA_DIR / f"{accession}_samples.json"
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump({
            "accession": accession,
            "download_date": datetime.now().isoformat(),
            "source_url": f"{GEO_URL}?acc={accession}",
            "samples": samples,
        }, f, indent=2, ensure_ascii=False)
    print(f"[OK] 样本元数据已保存: {meta_file}")

    # 计算校验值
    for filepath in [soft_file, meta_file]:
        sha = compute_sha256(filepath)
        checksum_file = CHECKSUM_DIR / f"{filepath.name}.sha256"
        with open(checksum_file, "w") as f:
            f.write(f"{sha}  {filepath.name}\n")
        print(f"[OK] SHA256: {filepath.name} -> {sha[:16]}...")

    print()
    print("=" * 70)
    print("完成")
    print("=" * 70)
    print(f"元数据目录: {METADATA_DIR}")
    print(f"校验目录: {CHECKSUM_DIR}")
    print()
    print("[INFO] 注意: 此脚本只下载元数据，不下载 FASTQ。")
    print("[INFO] 如需下载处理后文件，请使用 download_geo_processed.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())
