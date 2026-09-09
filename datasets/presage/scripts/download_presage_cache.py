#!/usr/bin/env python3
"""下载 PRESAGE Zenodo 缓存包。"""
import sys, argparse, json
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen, urlretrieve

BASE = Path(__file__).resolve().parent.parent
ZENODO_RECORD = "15587986"

def human_size(b):
    for u in ["B","KB","MB","GB"]:
        if b < 1024: return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} TB"

def fetch_zenodo_files(record_id):
    url = f"https://zenodo.org/api/records/{record_id}"
    print(f"[INFO] 获取 Zenodo 文件列表: {url}")
    try:
        with urlopen(url, timeout=30) as r:
            data = json.loads(r.read())
        files = data.get("files", [])
        print(f"[OK] 找到 {len(files)} 个文件")
        total = sum(f.get("size", 0) for f in files)
        print(f"总大小: {human_size(total)}")
        for f in files:
            print(f"  {f.get('key')} ({human_size(f.get('size', 0))})")
            if f.get("checksum"):
                print(f"    checksum: {f['checksum']}")
        return files
    except Exception as e:
        print(f"[ERROR] {e}")
        return []

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--list-only", action="store_true")
    p.add_argument("--download", action="store_true")
    p.add_argument("--file", help="指定要下载的文件名")
    args = p.parse_args()

    out_dir = BASE / "data" / "raw" / "presage_cache"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = fetch_zenodo_files(ZENODO_RECORD)
    if not files:
        print("[WARN] 无法获取文件列表。")
        return 1

    # 保存清单
    manifest = out_dir / "zenodo_file_list.json"
    with open(manifest, "w") as f:
        json.dump({"record": ZENODO_RECORD, "fetched_at": datetime.now().isoformat(), "files": files}, f, indent=2)

    if args.list_only or not args.download:
        print("[INFO] 仅列出模式，跳过下载。")
        print("[INFO] 使用 --download 下载全部文件，或 --file <name> 下载指定文件。")
        return 0

    # 下载
    to_download = [f for f in files if not args.file or f["key"] == args.file]
    for f in to_download:
        dest = out_dir / f["key"]
        if dest.exists():
            print(f"[SKIP] 已存在: {f['key']}")
            continue
        print(f"[INFO] 下载: {f['key']} ({human_size(f.get('size', 0))})")
        try:
            urlretrieve(f["links"]["self"], str(dest))
            print(f"[OK] {dest.name} ({human_size(dest.stat().st_size)})")
        except Exception as e:
            print(f"[ERROR] {e}")
            if dest.exists(): dest.unlink()
    return 0

if __name__ == "__main__":
    sys.exit(main())
