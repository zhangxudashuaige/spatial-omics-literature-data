#!/usr/bin/env python3
"""下载 Perez SLE PBMC 疾病队列数据（GEO GSE174188）。"""
import sys, argparse, json
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen, urlretrieve

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "data" / "perez_sle_pbmc"
GSE = "GSE174188"
GEO_URL = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"

def human_size(b):
    for u in ["B","KB","MB","GB"]:
        if b < 1024: return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} TB"

def fetch_soft(gse):
    url = f"{GEO_URL}?acc={gse}&targ=self&form=text&view=quick"
    print(f"[INFO] 获取 GEO 元数据: {gse}")
    try:
        with urlopen(url, timeout=30) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def parse_samples(soft):
    samples, cur = [], None
    for line in soft.split("\n"):
        if line.startswith("^SAMPLE ="):
            if cur: samples.append(cur)
            cur = {"gsm": line.split("=")[1].strip(), "title": "", "characteristics": {}}
        elif cur and line.startswith("!Sample_title ="):
            cur["title"] = line.split("=", 1)[1].strip()
        elif cur and line.startswith("!Sample_characteristics_ch1 ="):
            c = line.split("=", 1)[1].strip()
            if ":" in c:
                k, v = c.split(":", 1)
                cur["characteristics"][k.strip()] = v.strip()
    if cur: samples.append(cur)
    return samples

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata-only", action="store_true")
    args = p.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "metadata").mkdir(exist_ok=True)
    (OUT / "processed").mkdir(exist_ok=True)

    soft = fetch_soft(GSE)
    if not soft:
        print("[ERROR] 无法获取元数据，停止。")
        return 1

    soft_file = OUT / "metadata" / f"{GSE}_soft.txt"
    with open(soft_file, "w") as f: f.write(soft)
    print(f"[OK] SOFT 元数据已保存")

    samples = parse_samples(soft)
    print(f"[INFO] 样本数: {len(samples)}")

    # 统计供体和样本
    donors = set()
    for s in samples:
        for k, v in s["characteristics"].items():
            if "donor" in k.lower() or "subject" in k.lower():
                donors.add(v)
    print(f"[INFO] 供体数(从元数据提取): {len(donors)}")
    print(f"[INFO] 论文报告: 261供体, 354样本")

    meta_file = OUT / "metadata" / f"{GSE}_samples.json"
    with open(meta_file, "w") as f:
        json.dump({"accession": GSE, "download_date": datetime.now().isoformat(), "samples": samples}, f, indent=2, ensure_ascii=False)
    print(f"[OK] 样本元数据已保存")

    if args.metadata_only:
        print("[INFO] 仅元数据模式，跳过表达矩阵下载。")
        return 0

    # 尝试下载系列矩阵
    series_url = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{GSE[:-3]}nnn/{GSE}/matrix/"
    print(f"[INFO] 系列矩阵目录: {series_url}")
    print("[INFO] 请手动确认文件列表后下载，不推测链接。")
    print("[INFO] 补充文件可能包含作者处理后的 h5ad/rds。")

    return 0

if __name__ == "__main__":
    sys.exit(main())
