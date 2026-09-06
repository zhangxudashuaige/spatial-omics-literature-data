#!/usr/bin/env python3
"""
从 Zenodo API 获取完整文件清单，保存到 metadata/files.csv。

支持两个 Zenodo 记录:
- RNA和蛋白质: https://zenodo.org/records/13350497
- ATAC: https://zenodo.org/records/7058382
"""
import sys
import argparse
import csv
from pathlib import Path

import requests

METADATA_DIR = Path(__file__).resolve().parent.parent / "metadata"

ZENODO_API = "https://zenodo.org/api/records/{record_id}"


def fetch_zenodo_files(record_id):
    """从 Zenodo API 获取文件清单。"""
    url = ZENODO_API.format(record_id=record_id)
    print(f"[INFO] 获取 Zenodo 记录: {record_id}")
    print(f"       API: {url}")

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[ERROR] API 请求失败: {e}")
        return []

    files = data.get("files", [])
    print(f"[OK] 获取到 {len(files)} 个文件")

    results = []
    for f in files:
        results.append({
            "filename": f.get("key", ""),
            "file_size_bytes": f.get("size", 0),
            "download_url": f.get("links", {}).get("self", ""),
            "md5": f.get("checksum", "").replace("md5:", ""),
            "zenodo_record": record_id,
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="从 Zenodo API 获取文件清单")
    parser.add_argument("--record", default="13350497", help="Zenodo 记录 ID (默认 13350497 RNA+蛋白质)")
    parser.add_argument("--all", action="store_true", help="获取所有记录 (13350497 和 7058382)")
    parser.add_argument("--output", default=None, help="输出 CSV 路径")
    args = parser.parse_args()

    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    if args.all:
        record_ids = ["13350497", "7058382"]
    else:
        record_ids = [args.record]

    all_files = []
    for rid in record_ids:
        files = fetch_zenodo_files(rid)
        all_files.extend(files)
        print()

    if not all_files:
        print("[ERROR] 未获取到任何文件。")
        return 1

    # 保存
    output = Path(args.output) if args.output else METADATA_DIR / "files.csv"
    fieldnames = ["filename", "data_type", "file_size_bytes", "download_url",
                  "md5", "zenodo_version", "local_path", "download_status"]

    # 读取现有文件以保留 data_type 等列
    existing = {}
    if output.exists():
        with open(output, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing[row["filename"]] = row

    rows = []
    for f in all_files:
        fname = f["filename"]
        row = existing.get(fname, {})
        row.update({
            "filename": fname,
            "file_size_bytes": f["file_size_bytes"],
            "download_url": f["download_url"],
            "md5": f["md5"],
            "zenodo_version": f["zenodo_record"],
            "local_path": row.get("local_path", f"data/raw/{fname}"),
            "download_status": row.get("download_status", "pending"),
            "data_type": row.get("data_type", ""),
        })
        rows.append(row)

    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] 已保存 {len(rows)} 个文件到: {output}")
    print()
    print("文件大小总览:")
    total = sum(r["file_size_bytes"] for r in rows)
    print(f"  总计: {total / (1024**3):.2f} GB ({len(rows)} 个文件)")
    for r in sorted(rows, key=lambda x: x["file_size_bytes"], reverse=True)[:10]:
        size_mb = r["file_size_bytes"] / (1024 * 1024)
        print(f"  {r['filename']}: {size_mb:.1f} MB")

    return 0


if __name__ == "__main__":
    sys.exit(main())
