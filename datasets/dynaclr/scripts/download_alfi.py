#!/usr/bin/env python3
"""下载 ALFI 细胞周期数据（figshare）。"""
import sys, argparse, json
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen, urlretrieve

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "data" / "alfi_cellcycle"
FIGSHARE_DOI = "10.6084/m9.figshare.23798451"

def human_size(b):
    for u in ["B","KB","MB","GB"]:
        if b < 1024: return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} TB"

def fetch_figshare_files(doi):
    article_id = doi.split(".")[-1]
    url = f"https://api.figshare.com/v2/articles/{article_id}"
    print(f"[INFO] 获取 figshare 文件列表: {url}")
    try:
        with urlopen(url, timeout=30) as r:
            data = json.loads(r.read())
        files = data.get("files", [])
        print(f"[OK] 找到 {len(files)} 个文件")
        total_size = sum(f.get("size", 0) for f in files)
        print(f"总大小: {human_size(total_size)}")
        for f in files:
            print(f"  {f.get('name')} ({human_size(f.get('size', 0))})")
        return files
    except Exception as e:
        print(f"[ERROR] 获取失败: {e}")
        return []

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--list-only", action="store_true")
    p.add_argument("--metadata-only", action="store_true")
    args = p.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    files = fetch_figshare_files(FIGSHARE_DOI)
    if not files:
        print("[WARN] 无法获取文件列表，不推测下载链接。")
        return 1

    manifest = OUT / "alfi_file_list.json"
    with open(manifest, "w") as f:
        json.dump({"doi": FIGSHARE_DOI, "fetched_at": datetime.now().isoformat(), "files": files}, f, indent=2)
    print(f"[OK] 文件清单已保存: {manifest}")

    if args.list_only or args.metadata_only:
        print("[INFO] 仅列出/元数据模式，跳过下载。")
        return 0

    total_size = sum(f.get("size", 0) for f in files)
    if total_size > 30 * 1024**3:
        print(f"[WARN] 总大小 {human_size(total_size)} 超过30GB，请确认下载范围。")
        print("[INFO] 使用 --list-only 查看文件后，手动选择需要的文件。")
        return 0

    for f in files:
        dest = OUT / f["name"]
        if dest.exists():
            print(f"[SKIP] 已存在: {f['name']}")
            continue
        print(f"[INFO] 下载: {f['name']}")
        try:
            urlretrieve(f["download_url"], str(dest))
            print(f"[OK] {dest.name} ({human_size(dest.stat().st_size)})")
        except Exception as e:
            print(f"[ERROR] {e}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
