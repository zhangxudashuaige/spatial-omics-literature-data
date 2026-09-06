#!/usr/bin/env python3
"""
检查样本重叠。

特别检查:
- GSE12251 与 GSE23597 的重复样本
- GSE14580 与 GSE16879 的重复样本

检查方法:
1. 优先比较 GSM 编号
2. 必要时比较表达矩阵相关性
3. 必要时比较表达矩阵哈希

用法:
    python check_sample_overlap.py
    python check_sample_overlap.py --pair GSE12251 GSE23597
"""
import sys
import argparse
import json
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
METADATA_DIR = BASE_DIR / "data" / "metadata"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
RESULTS_DIR = BASE_DIR / "results"

# 需要特别检查的队列对
SPECIAL_PAIRS = [
    ("GSE12251", "GSE23597"),
    ("GSE14580", "GSE16879"),
]


def load_sample_gsm(accession):
    """加载数据集的 GSM 编号列表。"""
    # 优先从 JSON
    json_file = METADATA_DIR / f"{accession}_samples.json"
    if json_file.exists():
        with open(json_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
        return [s["gsm"] for s in meta.get("samples", [])]

    # 从 SOFT
    soft_file = METADATA_DIR / f"{accession}_soft.txt"
    if soft_file.exists():
        gsms = []
        with open(soft_file, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.startswith("^SAMPLE ="):
                    gsms.append(line.split("=")[1].strip())
        return gsms

    print(f"[WARN] {accession} 元数据不存在")
    return []


def check_gsm_overlap(gsm1, gsm2, name1, name2):
    """检查 GSM 编号重叠。"""
    set1 = set(gsm1)
    set2 = set(gsm2)
    overlap = set1 & set2

    print(f"\n--- GSM 编号重叠: {name1} vs {name2} ---")
    print(f"  {name1}: {len(gsm1)} 个样本 ({len(set1)} 唯一)")
    print(f"  {name2}: {len(gsm2)} 个样本 ({len(set2)} 唯一)")
    print(f"  重叠: {len(overlap)} 个样本")

    if overlap:
        print(f"  重叠的 GSM:")
        for gsm in sorted(overlap):
            print(f"    {gsm}")
    else:
        print("  无 GSM 编号重叠")

    return overlap


def load_expression_matrix(accession):
    """加载表达矩阵（用于相关性和哈希比较）。"""
    matrix_file = PROCESSED_DIR / f"{accession}_series_matrix.txt.gz"
    if not matrix_file.exists():
        print(f"[WARN] 表达矩阵不存在: {matrix_file.name}")
        return None

    # 跳过头部
    skip_rows = 0
    with open(matrix_file, "r", errors="replace") as f:
        for i, line in enumerate(f):
            if "series_matrix_table_begin" in line:
                skip_rows = i + 1
                break

    try:
        df = pd.read_csv(matrix_file, sep="\t", skiprows=skip_rows, index_col=0, low_memory=False)
        if df.index[-1] and "series_matrix_table_end" in str(df.index[-1]):
            df = df.iloc[:-1]
        return df
    except Exception as e:
        print(f"[ERROR] 读取表达矩阵失败: {e}")
        return None


def check_expression_hash(df1, df2, name1, name2):
    """比较表达矩阵列的哈希（检测完全相同的样本）。"""
    if df1 is None or df2 is None:
        return []

    # 对共同基因取交集
    common_genes = df1.index.intersection(df2.index)
    if len(common_genes) == 0:
        print("  无共同基因，无法比较")
        return []

    df1_common = df1.loc[common_genes]
    df2_common = df2.loc[common_genes]

    # 计算每列的哈希
    hash1 = {}
    for col in df1_common.columns:
        h = hashlib.md5(df1_common[col].values.tobytes()).hexdigest()
        hash1[h] = col

    hash2 = {}
    for col in df2_common.columns:
        h = hashlib.md5(df2_common[col].values.tobytes()).hexdigest()
        hash2[h] = col

    hash_overlap = set(hash1.keys()) & set(hash2.keys())
    print(f"\n--- 表达矩阵哈希重叠: {name1} vs {name2} ---")
    print(f"  共同基因数: {len(common_genes)}")
    print(f"  哈希完全相同的样本: {len(hash_overlap)}")

    if hash_overlap:
        for h in hash_overlap:
            print(f"    {hash1[h]} ({name1}) == {hash2[h]} ({name2})")

    return hash_overlap


def check_expression_correlation(df1, df2, name1, name2, threshold=0.99):
    """比较表达矩阵列的相关性（检测高度相似的样本）。"""
    if df1 is None or df2 is None:
        return []

    common_genes = df1.index.intersection(df2.index)
    if len(common_genes) == 0:
        return []

    df1_common = df1.loc[common_genes].fillna(0)
    df2_common = df2.loc[common_genes].fillna(0)

    # 计算相关性矩阵
    corr_matrix = np.corrcoef(df1_common.values.T, df2_common.values.T)
    n1 = df1_common.shape[1]
    corr_sub = corr_matrix[:n1, n1:]

    high_corr_pairs = []
    for i in range(n1):
        for j in range(corr_sub.shape[1]):
            if corr_sub[i, j] >= threshold:
                high_corr_pairs.append((
                    df1_common.columns[i],
                    df2_common.columns[j],
                    corr_sub[i, j]
                ))

    print(f"\n--- 表达矩阵高相关样本 (r>={threshold}): {name1} vs {name2} ---")
    print(f"  高相关样本对: {len(high_corr_pairs)}")
    for s1, s2, r in high_corr_pairs[:10]:
        print(f"    {s1} ({name1}) ~ {s2} ({name2}): r={r:.4f}")

    return high_corr_pairs


def check_pair(gse1, gse2):
    """检查一对数据集的样本重叠。"""
    print(f"\n{'='*60}")
    print(f"检查: {gse1} vs {gse2}")
    print(f"{'='*60}")

    # 1. GSM 编号比较
    gsm1 = load_sample_gsm(gse1)
    gsm2 = load_sample_gsm(gse2)
    gsm_overlap = check_gsm_overlap(gsm1, gsm2, gse1, gse2)

    # 2. 表达矩阵哈希比较
    df1 = load_expression_matrix(gse1)
    df2 = load_expression_matrix(gse2)
    hash_overlap = check_expression_hash(df1, df2, gse1, gse2)

    # 3. 表达矩阵相关性比较
    corr_pairs = check_expression_correlation(df1, df2, gse1, gse2)

    return {
        "pair": f"{gse1}_vs_{gse2}",
        "gsm_overlap": len(gsm_overlap),
        "hash_overlap": len(hash_overlap),
        "high_corr_pairs": len(corr_pairs),
        "gsm_overlap_list": sorted(gsm_overlap),
    }


def main():
    parser = argparse.ArgumentParser(description="检查样本重叠")
    parser.add_argument("--pair", nargs=2, metavar=("GSE1", "GSE2"), help="指定一对数据集")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    if args.pair:
        pairs = [tuple(args.pair)]
    else:
        pairs = SPECIAL_PAIRS

    results = []
    for gse1, gse2 in pairs:
        result = check_pair(gse1, gse2)
        results.append(result)

    # 保存结果
    results_df = pd.DataFrame(results)
    results_file = RESULTS_DIR / "sample_overlap_check.csv"
    results_df.to_csv(results_file, index=False)
    print(f"\n[OK] 重叠检查结果已保存: {results_file}")

    # 总结
    print(f"\n{'='*60}")
    print("重叠检查总结")
    print(f"{'='*60}")
    for r in results:
        status = "发现重叠!" if r["gsm_overlap"] > 0 or r["hash_overlap"] > 0 else "无重叠"
        print(f"  {r['pair']}: GSM重叠={r['gsm_overlap']}, 哈希重叠={r['hash_overlap']}, 高相关={r['high_corr_pairs']} [{status}]")

    return 0


if __name__ == "__main__":
    sys.exit(main())
