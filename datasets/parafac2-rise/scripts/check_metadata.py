#!/usr/bin/env python3
"""检查元数据完整性：样本/供体/处理/批次字段。"""
import sys, argparse, json
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent

def check_metadata(json_file, dataset_name):
    print(f"\n=== {dataset_name} ===")
    if not Path(json_file).exists():
        print(f"[WARN] 元数据不存在: {json_file}")
        return
    with open(json_file) as f:
        data = json.load(f)
    samples = data.get("samples", [])
    print(f"样本数: {len(samples)}")

    # 收集所有字段
    all_chars = set()
    for s in samples:
        all_chars.update(s.get("characteristics", {}).keys())
    print(f"characteristics 字段: {sorted(all_chars)}")

    # 检查关键字段
    keywords = {
        "donor": ["donor", "subject", "patient", "individual"],
        "sample": ["sample", "specimen"],
        "treatment": ["treatment", "drug", "therapy", "condition"],
        "batch": ["batch", "lane", "run", "cohort"],
        "disease": ["disease", "status", "condition", "diagnosis"],
        "cell_type": ["cell_type", "celltype", "cluster"],
    }
    for field, kws in keywords.items():
        found = [c for c in all_chars if any(k in c.lower() for k in kws)]
        status = "✓" if found else "✗"
        print(f"  {status} {field}: {found if found else '未找到'}")

    # 供体统计
    donor_fields = [c for c in all_chars if any(k in c.lower() for k in ["donor", "subject", "patient"])]
    if donor_fields:
        donors = set()
        for s in samples:
            for df in donor_fields:
                if df in s.get("characteristics", {}):
                    donors.add(s["characteristics"][df])
        print(f"  供体数: {len(donors)}")

def main():
    chen_meta = BASE / "data" / "chen_popalign_pbmc" / "metadata" / "figshare_file_list.json"
    perez_meta = BASE / "data" / "perez_sle_pbmc" / "metadata" / "GSE174188_samples.json"

    check_metadata(str(perez_meta), "Perez SLE PBMC")
    check_metadata(str(chen_meta), "Chen PopAlign PBMC")

    print("\n=== 注意 ===")
    print("Perez SLE: 论文报告261供体/354样本，不能将重复样本当作独立供体。")
    print("Chen PopAlign: RISE预处理后参考规模29433细胞/9461基因/46条件，仅用于核对。")
    return 0

if __name__ == "__main__":
    sys.exit(main())
