#!/usr/bin/env python3
"""列出扰动数据的可用文件、大小和下载URL。"""
import sys, argparse, json
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen

BASE = Path(__file__).resolve().parent.parent
MANIFEST = BASE / "manifests" / "datasets.csv"

def human_size(b):
    for u in ["B","KB","MB","GB"]:
        if b < 1024: return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} TB"

def fetch_geo_files(gse):
    url = f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={gse}&targ=self&form=text&view=quick"
    try:
        with urlopen(url, timeout=30) as r:
            soft = r.read().decode("utf-8", errors="replace")
        samples = [l.split("=")[1].strip() for l in soft.split("\n") if l.startswith("^SAMPLE =")]
        return {"accession": gse, "sample_count": len(samples), "samples": samples}
    except Exception as e:
        return {"accession": gse, "error": str(e)}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", help="指定数据集ID")
    args = p.parse_args()

    import csv
    with open(MANIFEST) as f:
        reader = csv.DictReader(f)
        datasets = list(reader)

    print(f"=== 扰动数据清单 ({len(datasets)} 个) ===\n")
    for d in datasets:
        if args.dataset and d["dataset_id"] != args.dataset:
            continue
        print(f"[{d['dataset_id']}] {d['name']}")
        print(f"  编号: {d['accession']}")
        print(f"  物种/体系: {d['species']} / {d['system']}")
        print(f"  模态: {d['modality']}")
        print(f"  扰动类型: {d['perturbation_type']}")
        print(f"  入口: {d['primary_url']}")
        print(f"  访问条件: {d['access_condition']}")
        print(f"  核实状态: {d['verification_status']} ({d['verification_date']})")
        if d["existing_module"]:
            print(f"  已有模块: {d['existing_module']}")
        if d["accession"].startswith("GSE"):
            info = fetch_geo_files(d["accession"])
            if "sample_count" in info:
                print(f"  GEO样本数: {info['sample_count']}")
        print()

    # 保存结果
    out = BASE / "results" / "available_files.json"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        json.dump({"generated_at": datetime.now().isoformat(), "datasets": datasets}, f, indent=2, ensure_ascii=False)
    print(f"[OK] 清单已保存: {out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
