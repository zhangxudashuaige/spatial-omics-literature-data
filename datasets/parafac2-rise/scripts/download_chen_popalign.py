#!/usr/bin/env python3
"""下载 Chen / PopAlign PBMC 药物扰动数据（figshare）。"""
import sys, argparse, json
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen, urlretrieve

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "data" / "chen_popalign_pbmc"
FIGSHARE_DOI = "10.6084/m9.figshare.11837097"

def human_size(b):
    for u in ["B","KB","MB","GB"]:
        if b < 1024: return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} TB"

def fetch_figshare_files(doi):
    """从 figshare API 获取文件列表。"""
    article_id = doi.split(".")[-1]
    url = f"https://api.figshare.com/v2/articles/{article_id}"
    print(f"[INFO] 获取 figshare 文件列表: {url}")
    try:
        with urlopen(url, timeout=30) as r:
            data = json.loads(r.read())
        files = data.get("files", [])
        print(f"[OK] 找到 {len(files)} 个文件")
        for f in files:
            print(f"  {f.get('name')} ({human_size(f.get('size', 0))})")
        return files
    except Exception as e:
        print(f"[ERROR] 获取失败: {e}")
        return []

def download_file(url, dest):
    if dest.exists():
        print(f"[SKIP] 已存在: {dest.name}")
        return True
    print(f"[INFO] 下载: {url}")
    try:
        urlretrieve(url, str(dest))
        print(f"[OK] {dest.name} ({human_size(dest.stat().st_size)})")
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        if dest.exists(): dest.unlink()
        return False

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--list-only", action="store_true")
    p.add_argument("--metadata-only", action="store_true")
    args = p.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "metadata").mkdir(exist_ok=True)

    files = fetch_figshare_files(FIGSHARE_DOI)
    if not files:
        print("[WARN] 无法获取文件列表，不推测下载链接。")
        return 1

    # 保存文件清单
    manifest = OUT / "metadata" / "figshare_file_list.json"
    with open(manifest, "w") as f:
        json.dump({"doi": FIGSHARE_DOI, "fetched_at": datetime.now().isoformat(), "files": files}, f, indent=2)
    print(f"[OK] 文件清单已保存: {manifest}")

    if args.list_only or args.metadata_only:
        print("[INFO] 仅列出/元数据模式，跳过下载。")
        return 0

    for f in files:
        dest = OUT / "processed" / f["name"]
        download_file(f["download_url"], dest)
    return 0

if __name__ == "__main__":
    sys.exit(main())
