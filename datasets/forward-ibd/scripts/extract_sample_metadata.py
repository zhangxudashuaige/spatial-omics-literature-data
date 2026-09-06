#!/usr/bin/env python3
"""
提取样本元数据。

从 GEO SOFT 文件或 JSON 元数据中提取样本级信息，包括：
- GSM 编号
- 样本标题
- 组织来源
- 疾病状态
- 治疗信息
- 响应标签
- 其他 characteristics

用法:
    python extract_sample_metadata.py --gse GSE12251
    python extract_sample_metadata.py --all
"""
import sys
import argparse
import json
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
METADATA_DIR = BASE_DIR / "data" / "metadata"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def extract_from_json(accession):
    """从 JSON 元数据提取样本信息。"""
    meta_file = METADATA_DIR / f"{accession}_samples.json"
    if not meta_file.exists():
        print(f"[WARN] 元数据不存在: {meta_file.name}")
        return None

    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    samples = meta.get("samples", [])
    if not samples:
        print(f"[WARN] {accession} 无样本信息")
        return None

    # 构建 DataFrame
    rows = []
    all_char_keys = set()
    for s in samples:
        row = {
            "gsm": s.get("gsm", ""),
            "title": s.get("title", ""),
            "source": s.get("source", ""),
        }
        chars = s.get("characteristics", {})
        for k, v in chars.items():
            row[f"char_{k}"] = v
            all_char_keys.add(f"char_{k}")
        rows.append(row)

    df = pd.DataFrame(rows)
    print(f"\n--- {accession} 样本元数据 ---")
    print(f"样本数: {len(df)}")
    print(f"字段数: {len(df.columns)}")
    print(f"字段: {list(df.columns)}")
    print(f"\n前5行:")
    print(df.head().to_string())

    # 保存
    out_file = METADATA_DIR / f"{accession}_sample_metadata.csv"
    df.to_csv(out_file, index=False)
    print(f"\n[OK] 已保存: {out_file}")

    return df


def extract_from_soft(accession):
    """从 SOFT 文件提取样本信息。"""
    soft_file = METADATA_DIR / f"{accession}_soft.txt"
    if not soft_file.exists():
        print(f"[WARN] SOFT 文件不存在: {soft_file.name}")
        return None

    samples = []
    current = None
    with open(soft_file, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line.startswith("^SAMPLE ="):
                if current:
                    samples.append(current)
                gsm = line.split("=")[1].strip()
                current = {"gsm": gsm, "title": "", "source": "", "characteristics": {}}
            elif current and line.startswith("!Sample_title ="):
                current["title"] = line.split("=", 1)[1].strip()
            elif current and line.startswith("!Sample_source_name_ch1 ="):
                current["source"] = line.split("=", 1)[1].strip()
            elif current and line.startswith("!Sample_characteristics_ch1 ="):
                char = line.split("=", 1)[1].strip()
                if ":" in char:
                    k, v = char.split(":", 1)
                    current["characteristics"][k.strip()] = v.strip()
    if current:
        samples.append(current)

    if not samples:
        print(f"[WARN] {accession} 未解析到样本")
        return None

    # 保存为 JSON（供后续使用）
    meta_file = METADATA_DIR / f"{accession}_samples.json"
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump({"accession": accession, "samples": samples}, f, indent=2, ensure_ascii=False)

    # 构建 DataFrame
    rows = []
    for s in samples:
        row = {"gsm": s["gsm"], "title": s["title"], "source": s["source"]}
        for k, v in s["characteristics"].items():
            row[f"char_{k}"] = v
        rows.append(row)

    df = pd.DataFrame(rows)
    out_file = METADATA_DIR / f"{accession}_sample_metadata.csv"
    df.to_csv(out_file, index=False)
    print(f"[OK] {accession}: {len(df)} 个样本，已保存到 {out_file.name}")
    return df


def main():
    parser = argparse.ArgumentParser(description="提取样本元数据")
    parser.add_argument("--gse", help="单个 GSE 编号")
    parser.add_argument("--all", action="store_true", help="处理所有已下载的数据集")
    args = parser.parse_args()

    if not args.gse and not args.all:
        print("[ERROR] 请指定 --gse 或 --all")
        return 1

    datasets = []
    if args.gse:
        datasets.append(args.gse)
    if args.all:
        # 查找所有已下载的元数据
        for f in METADATA_DIR.glob("*_soft.txt"):
            gse = f.name.replace("_soft.txt", "")
            datasets.append(gse)
        for f in METADATA_DIR.glob("*_samples.json"):
            gse = f.name.replace("_samples.json", "")
            if gse not in datasets:
                datasets.append(gse)

    datasets = sorted(set(datasets))
    print(f"[INFO] 处理 {len(datasets)} 个数据集: {datasets}")

    results = {}
    for gse in datasets:
        # 优先从 JSON 提取，否则从 SOFT 提取
        json_file = METADATA_DIR / f"{gse}_samples.json"
        if json_file.exists():
            df = extract_from_json(gse)
        else:
            df = extract_from_soft(gse)
        results[gse] = len(df) if df is not None else 0

    print(f"\n{'='*60}")
    print("提取总结")
    print(f"{'='*60}")
    for gse, count in results.items():
        print(f"  {gse}: {count} 个样本")

    return 0


if __name__ == "__main__":
    sys.exit(main())
