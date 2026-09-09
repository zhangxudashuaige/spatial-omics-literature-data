#!/usr/bin/env python3
"""检查 KGE 三元组：列顺序、实体/关系映射、训练测试划分。"""
import sys, argparse
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent

def inspect_triplets(filepath):
    f = Path(filepath)
    if not f.exists():
        print(f"[ERROR] 文件不存在: {f}")
        return
    print(f"文件: {f.name} ({f.stat().st_size / 1024:.1f} KB)")

    # 尝试不同分隔符
    for sep in ["\t", " ", ","]:
        try:
            df = pd.read_csv(f, sep=sep, header=None, nrows=5)
            if df.shape[1] >= 2:
                print(f"分隔符: '{sep}'")
                print(f"列数: {df.shape[1]}")
                break
        except:
            continue
    else:
        print("[ERROR] 无法解析文件")
        return

    # 读取全部
    df = pd.read_csv(f, sep=sep, header=None)
    print(f"三元组数: {len(df)}")
    print(f"\n前5行:")
    print(df.head().to_string(index=False, header=False))

    # 统计实体和关系
    if df.shape[1] >= 3:
        heads = df.iloc[:, 0].nunique()
        relations = df.iloc[:, 1].nunique()
        tails = df.iloc[:, 2].nunique()
        print(f"\n头实体数: {heads}")
        print(f"关系数: {relations}")
        print(f"尾实体数: {tails}")
        print(f"\n关系类型分布:")
        print(df.iloc[:, 1].value_counts().to_string())
    elif df.shape[1] == 2:
        print(f"实体1数: {df.iloc[:, 0].nunique()}")
        print(f"实体2数: {df.iloc[:, 1].nunique()}")

    # 检查是否为编号映射
    if df.shape[1] == 2 and df.iloc[0, 1].isdigit():
        print("\n[INFO] 检测到可能是 entity2id 或 relation2id 映射文件")

def inspect_mapping(filepath, mapping_type="entity"):
    f = Path(filepath)
    if not f.exists():
        print(f"[ERROR] 文件不存在: {f}")
        return
    df = pd.read_csv(f, sep="\t", header=None)
    print(f"{mapping_type}映射: {len(df)} 条")
    print(f"前5条:")
    print(df.head().to_string(index=False, header=False))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", help="三元组文件路径")
    p.add_argument("--entity-map", help="实体映射文件")
    p.add_argument("--relation-map", help="关系映射文件")
    args = p.parse_args()

    if args.file:
        inspect_triplets(args.file)
    if args.entity_map:
        inspect_mapping(args.entity_map, "实体")
    if args.relation_map:
        inspect_mapping(args.relation_map, "关系")

    if not any([args.file, args.entity_map, args.relation_map]):
        # 自动查找
        data_dir = BASE / "data" / "raw" / "pertkge_package"
        if data_dir.exists():
            txt_files = list(data_dir.glob("*.txt"))
            print(f"找到 {len(txt_files)} 个txt文件:")
            for f in txt_files:
                print(f"  {f.name}")
        else:
            print("未找到数据包。请先下载 PertKGE 数据。")
            print("URL: https://drive.google.com/file/d/1jFo0dDAnUOzMoKHFqPRM4pd_loTFwmMa/view")
    return 0

if __name__ == "__main__":
    sys.exit(main())
