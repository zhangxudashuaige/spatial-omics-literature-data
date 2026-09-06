#!/usr/bin/env python3
"""
从 Zenodo 下载 PerturbQA 补充数据。

Zenodo 记录: https://doi.org/10.5281/zenodo.14915312

可用文件:
- kg.zip: 生物知识图谱
- gene_summary.zip: 基因自然语言摘要
- summer_outputs.zip: Summer 模型输出
- summer_enrichment.zip: Summer 富集分析结果
- llm-nocot.zip: 无 Chain-of-Thought 消融
- llm-noretrieve.zip: 无检索消融
- results.zip: 最终评价结果

注意: 以 Zenodo 当前页面为准，不自行猜测文件名。
"""
import sys
import argparse
import zipfile
from pathlib import Path
from urllib.request import urlretrieve

import requests

ZENODO_RECORD = "14915312"
ZENODO_API = f"https://zenodo.org/api/records/{ZENODO_RECORD}"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# 预期文件分类 (以 Zenodo 实际为准)
EXPECTED_FILES = {
    "kg.zip": "knowledge_graph",
    "gene_summary.zip": "gene_summaries",
    "summer_outputs.zip": "model_outputs",
    "summer_enrichment.zip": "model_outputs",
    "llm-nocot.zip": "model_outputs",
    "llm-noretrieve.zip": "model_outputs",
    "results.zip": "results",
}


def human_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def fetch_zenodo_files():
    """从 Zenodo API 获取文件清单。"""
    print(f"[INFO] 获取 Zenodo 记录: {ZENODO_RECORD}")
    print(f"       API: {ZENODO_API}")

    try:
        resp = requests.get(ZENODO_API, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[ERROR] API 请求失败: {e}")
        return []

    files = data.get("files", [])
    print(f"[OK] 获取到 {len(files)} 个文件")
    print()

    results = []
    for f in files:
        results.append({
            "filename": f.get("key", ""),
            "size": f.get("size", 0),
            "url": f.get("links", {}).get("self", ""),
            "checksum": f.get("checksum", "").replace("md5:", ""),
        })

    return results


def download_file(url, dest):
    """下载文件。"""
    print(f"[INFO] 下载: {url}")
    print(f"       保存到: {dest}")

    def report_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, downloaded * 100 / total_size)
            mb_dl = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            print(f"\r  进度: {percent:.1f}% ({mb_dl:.1f}/{mb_total:.1f} MB)", end="", flush=True)

    try:
        urlretrieve(url, str(dest), reporthook=report_hook)
        print()
        size_mb = dest.stat().st_size / (1024 * 1024)
        print(f"[OK] 下载完成 ({size_mb:.1f} MB)")
        return True
    except Exception as e:
        print()
        print(f"[ERROR] 下载失败: {e}")
        return False


def extract_zip(zip_path, dest_dir):
    """解压 zip 文件。"""
    print(f"[INFO] 解压: {zip_path.name} -> {dest_dir}")
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(dest_dir)
        print(f"[OK] 解压完成")
        return True
    except Exception as e:
        print(f"[ERROR] 解压失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="从 Zenodo 下载 PerturbQA 数据")
    parser.add_argument("--list", action="store_true", help="仅列出文件，不下载")
    parser.add_argument("--file", default=None, help="下载指定文件名")
    parser.add_argument("--all", action="store_true", help="下载所有文件")
    parser.add_argument("--extract", action="store_true", help="下载后自动解压")
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    files = fetch_zenodo_files()
    if not files:
        print("[ERROR] 未获取到文件。")
        return 1

    # 列出文件
    print("=" * 60)
    print("Zenodo 文件清单")
    print("=" * 60)
    total_size = 0
    for f in files:
        size_mb = f["size"] / (1024 * 1024)
        total_size += f["size"]
        category = EXPECTED_FILES.get(f["filename"], "unknown")
        print(f"  {f['filename']}: {size_mb:.1f} MB -> data/{category}/")
    print(f"  总计: {len(files)} 个文件, {human_size(total_size)}")
    print()

    # 检查与预期是否一致
    zenodo_names = {f["filename"] for f in files}
    expected_names = set(EXPECTED_FILES.keys())
    if zenodo_names != expected_names:
        print("[WARN] Zenodo 实际文件与预期不一致。")
        print("[WARN] 以 Zenodo 当前页面为准，不自行猜测。")
        missing = expected_names - zenodo_names
        extra = zenodo_names - expected_names
        if missing:
            print(f"  缺失的预期文件: {missing}")
        if extra:
            print(f"  额外的文件: {extra}")
        print()

    if args.list:
        return 0

    # 确定要下载的文件
    if args.all:
        to_download = files
    elif args.file:
        to_download = [f for f in files if f["filename"] == args.file]
        if not to_download:
            print(f"[ERROR] 未找到文件: {args.file}")
            return 1
    else:
        print("[INFO] 使用 --file <filename> 下载指定文件，或 --all 下载全部。")
        return 0

    # 下载
    for f in to_download:
        filename = f["filename"]
        category = EXPECTED_FILES.get(filename, "unknown")
        dest_dir = DATA_DIR / category
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / filename

        if dest.exists():
            print(f"[SKIP] 已存在: {dest}")
        else:
            download_file(f["url"], dest)

        if args.extract and dest.exists() and filename.endswith(".zip"):
            extract_dir = dest_dir / filename.replace(".zip", "")
            extract_zip(dest, extract_dir)

    print()
    print("[DONE] 下载完成。")
    print(f"[INFO] 文件保存在: {DATA_DIR}")
    print()
    print("[INFO] 下一步:")
    print("       python scripts/inspect_benchmark.py --task de --cell_line k562")
    print("       python scripts/inspect_knowledge_graph.py")
    print("       python scripts/inspect_model_outputs.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())
