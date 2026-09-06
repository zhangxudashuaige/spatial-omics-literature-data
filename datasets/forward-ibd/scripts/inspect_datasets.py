#!/usr/bin/env python3
"""
检查数据集信息。

输出每个数据集:
- 文件名
- 文件大小
- 表达矩阵形状
- 基因标识类型
- 样本数量
- 临床标签字段
- 缺失值
- 是否为原始计数或标准化表达

用法:
    python inspect_datasets.py
    python inspect_datasets.py --gse GSE12251
"""
import sys
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
METADATA_DIR = BASE_DIR / "data" / "metadata"
RESULTS_DIR = BASE_DIR / "results"


def human_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def inspect_series_matrix(filepath):
    """检查 GEO series matrix 文件。"""
    print(f"\n--- {filepath.name} ---")
    print(f"文件大小: {human_size(filepath.stat().st_size)}")

    # GEO series matrix 有头部注释，需要跳过
    # 找到 !series_matrix_table_begin 行
    skip_rows = 0
    with open(filepath, "r", errors="replace") as f:
        for i, line in enumerate(f):
            if "series_matrix_table_begin" in line:
                skip_rows = i + 1
                break

    print(f"跳过头部行数: {skip_rows}")

    try:
        df = pd.read_csv(filepath, sep="\t", skiprows=skip_rows, index_col=0, low_memory=False)
        # 最后一行可能是 !series_matrix_table_end
        if df.index[-1] and "series_matrix_table_end" in str(df.index[-1]):
            df = df.iloc[:-1]

        print(f"表达矩阵形状: {df.shape} (基因 × 样本)")
        print(f"基因数: {df.shape[0]}")
        print(f"样本数: {df.shape[1]}")
        print(f"基因标识类型: {df.index.name or 'ID_ref'}")
        print(f"前5个基因: {list(df.index[:5])}")
        print(f"前5个样本: {list(df.columns[:5])}")

        # 数据类型
        print(f"数据类型: {df.dtypes.iloc[0] if len(df.dtypes) > 0 else 'N/A'}")

        # 缺失值
        missing = df.isnull().sum().sum()
        total = df.size
        print(f"缺失值: {missing} / {total} ({100*missing/total:.2f}%)" if total > 0 else "缺失值: N/A")

        # 判断是否为原始计数或标准化表达
        values = df.values.flatten()
        values = values[~np.isnan(values)] if len(values) > 0 else values
        if len(values) > 0:
            has_negative = (values < 0).any()
            all_integers = np.all(values == values.astype(int))
            max_val = values.max()
            print(f"是否含负值: {has_negative}")
            print(f"是否全为整数: {all_integers}")
            print(f"最大值: {max_val:.2f}")
            if all_integers and not has_negative and max_val > 100:
                print("表达类型: 可能是原始计数")
            elif has_negative or max_val <= 20:
                print("表达类型: 可能是标准化表达（log2 或 z-score）")
            else:
                print("表达类型: 可能是标准化表达（非对数）")

        # 临床标签（从样本名推断）
        print(f"\n临床标签字段: 需从元数据获取（样本名可能包含响应信息）")
        print(f"样本名示例: {list(df.columns[:3])}")

        return {
            "file": filepath.name,
            "size": filepath.stat().st_size,
            "shape": f"{df.shape[0]}x{df.shape[1]}",
            "genes": df.shape[0],
            "samples": df.shape[1],
            "missing_pct": f"{100*missing/total:.2f}%" if total > 0 else "N/A",
        }
    except Exception as e:
        print(f"[ERROR] 读取失败: {e}")
        return None


def inspect_metadata(accession):
    """检查元数据。"""
    meta_file = METADATA_DIR / f"{accession}_samples.json"
    if not meta_file.exists():
        print(f"[WARN] 元数据不存在: {meta_file.name}")
        return None

    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    samples = meta.get("samples", [])
    print(f"\n--- {accession} 元数据 ---")
    print(f"样本数: {len(samples)}")
    print(f"下载日期: {meta.get('download_date', 'N/A')}")

    # 提取临床标签字段
    all_chars = set()
    for s in samples:
        all_chars.update(s.get("characteristics", {}).keys())
    print(f"临床标签字段: {sorted(all_chars)}")

    # 响应标签
    response_keywords = ["response", "responder", "outcome", "treatment", "therapy", "remission", "mucosal"]
    response_fields = [f for f in all_chars if any(kw in f.lower() for kw in response_keywords)]
    if response_fields:
        print(f"可能的响应标签: {response_fields}")
        for field in response_fields:
            values = set()
            for s in samples:
                if field in s.get("characteristics", {}):
                    values.add(s["characteristics"][field])
            print(f"  {field}: {sorted(values)}")
    else:
        print("未自动识别到响应标签字段")

    return meta


def main():
    parser = argparse.ArgumentParser(description="检查数据集")
    parser.add_argument("--gse", help="指定单个 GSE 编号")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # 查找已下载的处理后文件
    matrix_files = list(PROCESSED_DIR.glob("*_series_matrix.txt.gz"))
    print(f"找到 {len(matrix_files)} 个 series matrix 文件")

    summary = []

    if args.gse:
        # 检查指定数据集
        meta = inspect_metadata(args.gse)
        for f in matrix_files:
            if args.gse in f.name:
                result = inspect_series_matrix(f)
                if result:
                    summary.append(result)
    else:
        # 检查所有
        for f in sorted(matrix_files):
            result = inspect_series_matrix(f)
            if result:
                summary.append(result)
            gse = f.name.split("_")[0]
            inspect_metadata(gse)

    # 保存摘要
    if summary:
        summary_df = pd.DataFrame(summary)
        summary_file = RESULTS_DIR / "dataset_summary.csv"
        summary_df.to_csv(summary_file, index=False)
        print(f"\n[OK] 摘要已保存: {summary_file}")
        print(summary_df.to_string(index=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
