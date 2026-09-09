#!/usr/bin/env python3
"""下载 AdaPert 资源（默认仅下载元数据和小样例，不下载完整单细胞矩阵）。"""
import sys, argparse, json
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen, urlretrieve

BASE = Path(__file__).resolve().parent.parent

RESOURCES = {
    "string_v115": {
        "url": "https://string-db.org/cgi/download.pl?species_text=Homo+sapiens",
        "desc": "STRING v11.5 人类蛋白关联数据",
        "local": "data/raw/string",
    },
    "genept": {
        "url": "https://zenodo.org/records/10833191",
        "desc": "GenePT 预计算语义嵌入",
        "local": "data/raw/genept",
    },
    "replogle_supp": {
        "url": "https://plus.figshare.com/articles/dataset/21632564",
        "desc": "Replogle 补充资源（不等于完整单细胞计数）",
        "local": "data/raw/supplementary",
    },
}

def human_size(b):
    for u in ["B","KB","MB","GB"]:
        if b < 1024: return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} TB"

def list_resources():
    print("=== AdaPert 资源清单 ===\n")
    for key, info in RESOURCES.items():
        print(f"[{key}] {info['desc']}")
        print(f"  URL: {info['url']}")
        print(f"  本地: {info['local']}")
        print()
    print("注意:")
    print("  - K562/RPE1 完整单细胞数据从 https://gwps.wi.mit.edu/ 获取")
    print("  - JURKAT/HEPG2 原始编号未核实，标为待确认")
    print("  - 补充资源不等于完整单细胞计数数据")
    print("  - 不默认下载全部 FASTQ")

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
        return files
    except Exception as e:
        print(f"[ERROR] {e}")
        return []

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--list-only", action="store_true")
    p.add_argument("--resource", choices=list(RESOURCES.keys()))
    p.add_argument("--metadata-only", action="store_true")
    args = p.parse_args()

    if args.list_only or not args.resource:
        list_resources()
        return 0

    info = RESOURCES[args.resource]
    out_dir = BASE / info["local"]
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] 资源: {info['desc']}")
    print(f"[INFO] URL: {info['url']}")

    if args.resource == "genept":
        files = fetch_zenodo_files("10833191")
        manifest = out_dir / "genept_file_list.json"
        with open(manifest, "w") as f:
            json.dump({"record": "10833191", "fetched_at": datetime.now().isoformat(), "files": files}, f, indent=2)
        if args.metadata_only:
            print("[INFO] 仅元数据模式，跳过下载。")
            return 0

    if args.metadata_only:
        print("[INFO] 仅元数据模式，跳过下载。")
        print("[INFO] 请手动访问上述URL获取文件。")
        return 0

    print("[INFO] 大型文件下载需手动确认。不默认下载完整单细胞矩阵。")
    return 0

if __name__ == "__main__":
    sys.exit(main())
