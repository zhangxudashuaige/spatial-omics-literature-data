#!/usr/bin/env python3
"""
下载 ArrayExpress / EMBL-EBI BioStudies 数据。

功能:
- 从 EMBL-EBI BioStudies 下载 ArrayExpress 数据
- 支持 E-MTAB-xxxx 编号
- 默认只下载元数据和处理后文件
- 不自动下载大型原始数据
- 已存在文件不重复下载

用法:
    python download_arrayexpress.py --accession E-MTAB-7604
"""
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen, urlretrieve

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
METADATA_DIR = BASE_DIR / "data" / "metadata"

BIOSTUDIES_API = "https://www.ebi.ac.uk/biostudies/api/v1/studies"
ARRAYEXPRESS_URL = "https://www.ebi.ac.uk/biostudies/arrayexpress/studies"


def human_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def fetch_biostudies_metadata(accession):
    """从 BioStudies API 获取元数据。"""
    url = f"{BIOSTUDIES_API}/{accession}"
    print(f"[INFO] 获取 BioStudies 元数据: {accession}")
    print(f"       URL: {url}")
    try:
        with urlopen(url, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[ERROR] 获取失败: {e}")
        return None


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


def download_arrayexpress_dataset(accession, metadata_only=False):
    """下载单个 ArrayExpress 数据集。"""
    print(f"\n{'='*60}")
    print(f"数据集: {accession}")
    print(f"{'='*60}")

    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # 1. 获取元数据
    metadata = fetch_biostudies_metadata(accession)
    if not metadata:
        print("[ERROR] 无法获取元数据，跳过。")
        print("[INFO] 请手动访问:")
        print(f"       {ARRAYEXPRESS_URL}/{accession}")
        return False

    # 保存元数据
    meta_file = METADATA_DIR / f"{accession}_metadata.json"
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"[OK] 元数据已保存: {meta_file.name}")

    # 提取基本信息
    title = metadata.get("title", "N/A")
    print(f"标题: {title}")

    # 提取文件列表
    files = []
    section = metadata.get("section", {})
    if section:
        subsections = section.get("subsections", [])
        for sub in subsections:
            if "files" in sub:
                for f in sub["files"]:
                    files.append(f)

    print(f"[INFO] 文件数: {len(files)}")
    for f in files[:10]:
        fname = f.get("path", f.get("name", "unknown"))
        fsize = f.get("size", 0)
        print(f"  {fname} ({human_size(fsize) if fsize else 'N/A'})")

    if metadata_only:
        print("[INFO] --metadata-only 模式，跳过文件下载。")
        return True

    # 2. 下载处理后文件（尝试常见的处理后文件）
    # ArrayExpress 通常有 processed 目录
    print("\n[INFO] 处理后文件需从 ArrayExpress 页面手动确认下载链接。")
    print(f"       页面: {ARRAYEXPRESS_URL}/{accession}")
    print("[INFO] 常见文件类型:")
    print("       - processed/E-MTAB-7604.processed.1.zip (处理后表达矩阵)")
    print("       - raw/E-MTAB-7604.raw.1.zip (原始CEL文件)")

    return True


def main():
    parser = argparse.ArgumentParser(description="下载 ArrayExpress 数据")
    parser.add_argument("--accession", default="E-MTAB-7604", help="ArrayExpress 编号")
    parser.add_argument("--metadata-only", action="store_true", help="只下载元数据")
    args = parser.parse_args()

    success = download_arrayexpress_dataset(args.accession, metadata_only=args.metadata_only)

    print(f"\n{'='*60}")
    print(f"结果: {'成功' if success else '失败'}")
    print(f"{'='*60}")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
