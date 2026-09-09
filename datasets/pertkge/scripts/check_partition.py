#!/usr/bin/env python3
"""检查训练/测试划分：三元组重叠、实体覆盖、划分比例。"""
import sys, argparse
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent

def load_triplets(filepath):
    for sep in ["\t", " ", ","]:
        try:
            df = pd.read_csv(filepath, sep=sep, header=None)
            if df.shape[1] >= 2:
                return df
        except:
            continue
    return None

def check_partition(train_path, test_path):
    train = load_triplets(train_path)
    test = load_triplets(test_path)
    if train is None or test is None:
        print("[ERROR] 无法加载划分文件")
        return

    print(f"训练集: {len(train)} 三元组")
    print(f"测试集: {len(test)} 三元组")
    print(f"测试比例: {100*len(test)/(len(train)+len(test)):.1f}%")

    # 三元组重叠
    if train.shape[1] >= 3 and test.shape[1] >= 3:
        train_set = set(map(tuple, train.iloc[:, :3].values))
        test_set = set(map(tuple, test.iloc[:, :3].values))
        overlap = train_set & test_set
        print(f"\n三元组重叠: {len(overlap)}")
        if len(overlap) > 0:
            print(f"[WARN] 发现 {len(overlap)} 个重叠三元组！")
        else:
            print("[OK] 无重叠三元组")

        # 实体覆盖
        train_entities = set(train.iloc[:, 0]) | set(train.iloc[:, 2])
        test_entities = set(test.iloc[:, 0]) | set(test.iloc[:, 2])
        print(f"\n训练集实体数: {len(train_entities)}")
        print(f"测试集实体数: {len(test_entities)}")
        print(f"测试集中未见过的实体: {len(test_entities - train_entities)}")

        # 关系覆盖
        train_rels = set(train.iloc[:, 1])
        test_rels = set(test.iloc[:, 1])
        print(f"训练集关系数: {len(train_rels)}")
        print(f"测试集关系数: {len(test_rels)}")
        print(f"测试集中未见过的关系: {len(test_rels - train_rels)}")

    # 保存结果
    out = BASE / "results" / "triplet_stats.csv"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        f.write("metric,value\n")
        f.write(f"train_triplets,{len(train)}\n")
        f.write(f"test_triplets,{len(test)}\n")
        f.write(f"test_ratio,{100*len(test)/(len(train)+len(test)):.1f}%\n")
    print(f"\n[OK] 结果已保存: {out}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--train", help="训练集文件")
    p.add_argument("--test", help="测试集文件")
    args = p.parse_args()

    if args.train and args.test:
        check_partition(args.train, args.test)
    else:
        print("请指定 --train 和 --test 文件路径。")
        print("或先下载 PertKGE 数据包后自动查找。")
    return 0

if __name__ == "__main__":
    sys.exit(main())
