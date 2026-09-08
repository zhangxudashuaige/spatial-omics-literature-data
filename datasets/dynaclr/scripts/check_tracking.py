#!/usr/bin/env python3
"""检查追踪文件：轨迹ID、帧号、亲子关系、标签关联。"""
import sys, argparse
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent

def check_tracking_csv(filepath):
    df = pd.read_csv(filepath)
    print(f"形状: {df.shape}")
    print(f"列: {list(df.columns)}")

    # 检查必需字段
    required = ["track_id", "frame"]
    optional = ["parent_id", "x", "y", "z", "label", "division", "infection"]
    for col in required:
        if col in df.columns:
            print(f"  ✓ {col}: {df[col].nunique()} 个唯一值")
        else:
            print(f"  ✗ {col}: 缺失")
    for col in optional:
        if col in df.columns:
            print(f"  ~ {col}: 存在")

    # 轨迹统计
    if "track_id" in df.columns and "frame" in df.columns:
        track_lengths = df.groupby("track_id")["frame"].count()
        print(f"\n轨迹数: {df['track_id'].nunique()}")
        print(f"轨迹长度: min={track_lengths.min()}, max={track_lengths.max()}, mean={track_lengths.mean():.1f}")
        print(f"帧范围: {df['frame'].min()} - {df['frame'].max()}")

    # 分裂关系
    if "parent_id" in df.columns:
        parents = df[df["parent_id"].notna() & (df["parent_id"] != 0)]
        print(f"\n有父轨迹的记录: {len(parents)}")
        if len(parents) > 0:
            print(f"涉及的子轨迹数: {parents['track_id'].nunique()}")
            print(f"涉及的父轨迹数: {parents['parent_id'].nunique()}")

    # 标签
    label_cols = [c for c in df.columns if any(k in c.lower() for k in ["label", "division", "infection", "state", "phase"])]
    if label_cols:
        print(f"\n标签列: {label_cols}")
        for col in label_cols:
            print(f"  {col}: {df[col].value_counts().to_dict()}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True)
    args = p.parse_args()
    f = Path(args.file)
    if not f.exists():
        print(f"[ERROR] 文件不存在: {f}")
        return 1
    print(f"文件: {f.name} ({f.stat().st_size / 1024:.1f} KB)")
    if f.suffix == ".csv":
        check_tracking_csv(f)
    else:
        print(f"[WARN] 不支持的格式: {f.suffix}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
