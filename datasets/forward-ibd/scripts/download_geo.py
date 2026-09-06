#!/usr/bin/env python3
"""
下载 GEO 数据（元数据和处理后文件）。

功能:
- 使用 GEOparse 或 GEO 官方 FTP/API 读取 GEO 数据
- 默认只下载元数据和 processed/supplementary 文件
- 不自动下载全部大型原始数据
- 支持按 GSE 编号选择
- 已存在文件不重复下载
- 下载后记录来源和日期

用法:
    python download_geo.py --gse GSE12251
    python download_geo.py --gse GSE12251 --metadata-only
    python download_geo.py --all-training
"""
import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen, urlretrieve

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
METADATA_DIR = BASE_DIR / "data" / "metadata"

GEO_URL = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"
GEO_FTP = "https://ftp.ncbi.nlm.nih.gov/geo"

# 训练队列
TRAINING_GSE = ["GSE12251", "GSE16879", "GSE14580", "GSE73661", "GSE207022", "GSE234736"]
# 验证队列
VALIDATION_GSE = ["GSE23597", "GSE115390", "GSE49858", "GSE59071", "GSE37283", "GSE83687", "GSE20881", "GSE193677"]
# 布尔网络队列
BOOLEAN_GSE = ["GSE83687", "GSE73661", "GSE6731"]


def human_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def fetch_geo_soft(accession):
    """从 GEO 获取 SOFT 格式元数据。"""
    url = f"{GEO_URL}?acc={accession}&targ=self&form=text&view=quick"
    print(f"[INFO] 获取 GEO 元数据: {accession}")
    try:
        with urlopen(url, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"[ERROR] 获取失败: {e}")
        return None


def parse_soft_samples(soft_content):
    """从 SOFT 内容解析样本列表。"""
    samples = []
    current = None
    for line in soft_content.split("\n"):
        if line.startswith("^SAMPLE ="):
            if current:
                samples.append(current)
            gsm = line.split("=")[1].strip()
            current = {"gsm": gsm, "title": "", "source": "", "characteristics": {}}
        elif current and line.startswith("!Sample_title ="):
            current["title"] = line.split("=", 1)[1].strip()
        elif current and line.startswith("!Sample_source_name_ch1 ="):
            current["source"] = line.split("=", 1)[1].strip()
        elif current and line.startswith("!Sample_characteristics_ch1 ="):
            char = line.split("=", 1)[1].strip()
            if ":" in char:
                k, v = char.split(":", 1)
                current["characteristics"][k.strip()] = v.strip()
    if current:
        samples.append(current)
    return samples


def download_file(url, dest):
    """下载文件。"""
    if dest.exists():
        size = dest.stat().st_size
        print(f"[SKIP] 已存在: {dest.name} ({human_size(size)})")
        return True
    print(f"[INFO] 下载: {url}")
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


def download_geo_dataset(accession, metadata_only=False):
    """下载单个 GEO 数据集。"""
    print(f"\n{'='*60}")
    print(f"数据集: {accession}")
    print(f"{'='*60}")

    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # 1. 下载元数据
    soft = fetch_geo_soft(accession)
    if not soft:
        print("[ERROR] 无法获取元数据，跳过。")
        return False

    soft_file = METADATA_DIR / f"{accession}_soft.txt"
    with open(soft_file, "w", encoding="utf-8") as f:
        f.write(soft)
    print(f"[OK] SOFT 元数据已保存: {soft_file.name}")

    # 解析样本
    samples = parse_soft_samples(soft)
    print(f"[INFO] 样本数: {len(samples)}")
    for s in samples[:5]:
        print(f"  {s['gsm']}: {s['title']}")
    if len(samples) > 5:
        print(f"  ... 还有 {len(samples) - 5} 个样本")

    # 保存样本元数据
    meta_file = METADATA_DIR / f"{accession}_samples.json"
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump({
            "accession": accession,
            "download_date": datetime.now().isoformat(),
            "source_url": f"{GEO_URL}?acc={accession}",
            "samples": samples,
        }, f, indent=2, ensure_ascii=False)
    print(f"[OK] 样本元数据已保存: {meta_file.name}")

    if metadata_only:
        print("[INFO] --metadata-only 模式，跳过处理后文件下载。")
        return True

    # 2. 尝试下载处理后矩阵（系列矩阵文件）
    series_matrix = f"{accession}_series_matrix.txt.gz"
    series_url = f"{GEO_FTP}/series/{accession[:-3]}nnn/{accession}/matrix/{series_matrix}"
    dest = PROCESSED_DIR / series_matrix
    download_file(series_url, dest)

    # 3. 尝试下载补充文件
    suppl_url = f"{GEO_URL}?acc={accession}&targ=self&form=text&view=quick"
    print("[INFO] 补充文件请从 GEO 页面手动确认后下载。")
    print(f"       页面: {GEO_URL}?acc={accession}")

    return True


def main():
    parser = argparse.ArgumentParser(description="下载 GEO 数据")
    parser.add_argument("--gse", help="单个 GSE 编号")
    parser.add_argument("--metadata-only", action="store_true", help="只下载元数据")
    parser.add_argument("--all-training", action="store_true", help="下载所有训练队列")
    parser.add_argument("--all-validation", action="store_true", help="下载所有验证队列")
    args = parser.parse_args()

    if not args.gse and not args.all_training and not args.all_validation:
        print("[ERROR] 请指定 --gse、--all-training 或 --all-validation")
        return 1

    datasets = []
    if args.gse:
        datasets.append(args.gse)
    if args.all_training:
        datasets.extend(TRAINING_GSE)
    if args.all_validation:
        datasets.extend(VALIDATION_GSE)

    # 去重
    datasets = list(dict.fromkeys(datasets))

    print(f"[INFO] 将下载 {len(datasets)} 个数据集: {datasets}")
    if args.metadata_only:
        print("[INFO] 模式: 仅元数据")

    results = {}
    for gse in datasets:
        success = download_geo_dataset(gse, metadata_only=args.metadata_only)
        results[gse] = "success" if success else "failed"

    print(f"\n{'='*60}")
    print("下载总结")
    print(f"{'='*60}")
    for gse, status in results.items():
        print(f"  {gse}: {status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
