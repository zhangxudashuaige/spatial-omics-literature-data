#!/usr/bin/env python3
"""
检查 Hugging Face 仓库 cyclopeta/PerturbNet_reproduce。

使用 Hugging Face API 列出:
- 文件路径
- 文件大小
- LFS 状态
- commit 版本
- 是否属于 data_paper、example_data、models 或 pretrained_model

将结果保存到 metadata/file_manifest.csv。
"""
import sys
import csv
from pathlib import Path

import requests

HF_REPO = "cyclopeta/PerturbNet_reproduce"
HF_API = f"https://huggingface.co/api/models/{HF_REPO}"
METADATA_DIR = Path(__file__).resolve().parent.parent / "metadata"


def categorize_path(path):
    """根据路径判断属于哪个目录类别。"""
    categories = ["data_paper", "example_data", "models", "pretrained_model"]
    for cat in categories:
        if path.startswith(cat + "/") or path == cat:
            return cat
    return "other"


def fetch_hf_files():
    """从 Hugging Face API 获取文件清单。"""
    print(f"[INFO] 获取 Hugging Face 仓库: {HF_REPO}")
    print(f"       API: {HF_API}")

    try:
        resp = requests.get(HF_API, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[ERROR] API 请求失败: {e}")
        return [], None

    commit_hash = data.get("sha", "unknown")
    siblings = data.get("siblings", [])
    print(f"[OK] commit: {commit_hash}")
    print(f"[OK] 文件数: {len(siblings)}")

    files = []
    for sib in siblings:
        path = sib.get("rfilename", "")
        files.append({
            "file_path": path,
            "category": categorize_path(path),
        })

    return files, commit_hash


def fetch_file_sizes(files):
    """获取每个文件的大小和 LFS 状态。"""
    print("[INFO] 获取文件大小和 LFS 状态...")

    results = []
    for i, f in enumerate(files):
        path = f["file_path"]
        url = f"https://huggingface.co/{HF_REPO}/resolve/main/{path}"

        try:
            resp = requests.head(url, timeout=15, allow_redirects=True)
            size = int(resp.headers.get("Content-Length", 0))
            # LFS 文件通常有 x-linked-size 或通过 Content-Length 判断
            is_lfs = size > 10 * 1024 * 1024  # >10MB 可能是 LFS
        except Exception:
            size = 0
            is_lfs = False

        results.append({
            "file_path": path,
            "file_size_bytes": size,
            "lfs": is_lfs,
            "category": f["category"],
        })

        if (i + 1) % 10 == 0:
            print(f"  已处理 {i+1}/{len(files)} 个文件")

    return results


def main():
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    files, commit_hash = fetch_hf_files()
    if not files:
        print("[ERROR] 未获取到文件。")
        return 1

    # 获取文件大小
    files_with_size = fetch_file_sizes(files)

    # 按类别统计
    print()
    print("=" * 60)
    print("按类别统计")
    print("=" * 60)
    categories = {}
    for f in files_with_size:
        cat = f["category"]
        if cat not in categories:
            categories[cat] = {"count": 0, "size": 0}
        categories[cat]["count"] += 1
        categories[cat]["size"] += f["file_size_bytes"]

    for cat, info in sorted(categories.items()):
        size_mb = info["size"] / (1024 * 1024)
        print(f"  {cat}: {info['count']} 个文件, {size_mb:.1f} MB")

    total_size = sum(f["file_size_bytes"] for f in files_with_size)
    print(f"  总计: {len(files_with_size)} 个文件, {total_size / (1024*1024):.1f} MB")
    print()

    # 保存到 file_manifest.csv
    output = METADATA_DIR / "file_manifest.csv"
    fieldnames = ["file_path", "file_size_bytes", "lfs", "commit_hash",
                  "category", "download_status", "local_path", "notes"]

    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for file_info in files_with_size:
            writer.writerow({
                "file_path": file_info["file_path"],
                "file_size_bytes": file_info["file_size_bytes"],
                "lfs": file_info["lfs"],
                "commit_hash": commit_hash,
                "category": file_info["category"],
                "download_status": "pending",
                "local_path": f"data/{file_info['category']}/{Path(file_info['file_path']).name}",
                "notes": "",
            })

    print(f"[OK] 已保存到: {output}")
    print()
    print("[INFO] 第一阶段下载 (example_data):")
    print("       python scripts/download_huggingface.py --phase 1")
    print("[INFO] 第二阶段下载 (data_paper, models, pretrained_model):")
    print("       python scripts/download_huggingface.py --phase 2")

    return 0


if __name__ == "__main__":
    sys.exit(main())
