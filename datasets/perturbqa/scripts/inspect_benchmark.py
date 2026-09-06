#!/usr/bin/env python3
"""
检查 PerturbQA 基准数据。

支持的任务:
- de: differential expression
- direction: direction of change
- gene_set_enrichment: gene set enrichment

支持的细胞系:
- k562, rpe1, hepg2, jurkat, k562_set

输出:
- 数据集名称
- 训练/测试样本数量
- 一条实际数据
- pert、gene、label 字段含义
- 正负标签数量
- 不同扰动基因数量
"""
import sys
import argparse
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "benchmark"

TASK_DIRS = {
    "de": "de",
    "direction": "direction",
    "gse": "gene_set_enrichment",
    "gene_set_enrichment": "gene_set_enrichment",
}

CELL_LINES = ["k562", "rpe1", "hepg2", "jurkat", "k562_set"]


def load_jsonl(filepath):
    """加载 JSONL 文件。"""
    data = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def load_json(filepath):
    """加载 JSON 文件。"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def find_data_files(task_dir, cell_line):
    """查找数据文件。"""
    files = []
    for pattern in [f"*{cell_line}*", f"*{cell_line.upper()}*"]:
        files.extend(task_dir.glob(pattern))
    # 也列出所有文件
    all_files = list(task_dir.glob("*"))
    return files, all_files


def inspect_task(task, cell_line):
    """检查指定任务和细胞系的数据。"""
    task_dir_name = TASK_DIRS.get(task)
    if not task_dir_name:
        print(f"[ERROR] 未知任务: {task}")
        return 1

    task_dir = DATA_DIR / task_dir_name
    if not task_dir.exists():
        print(f"[ERROR] 目录不存在: {task_dir}")
        print("[ERROR] 请先运行: python scripts/download_data.py --all")
        return 1

    print("=" * 60)
    print(f"PerturbQA 基准数据检查")
    print(f"任务: {task}")
    print(f"细胞系: {cell_line}")
    print("=" * 60)
    print()

    # 列出目录中的文件
    all_files = [f for f in task_dir.iterdir() if f.is_file() and not f.name.startswith(".")]
    print(f"目录中的文件 ({len(all_files)}):")
    for f in sorted(all_files):
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name}: {size_kb:.1f} KB")
    print()

    if not all_files:
        print("[WARN] 目录为空。请先下载数据。")
        return 1

    # 尝试加载匹配的文件
    matched = [f for f in all_files if cell_line.lower() in f.name.lower()]
    if not matched:
        print(f"[WARN] 未找到匹配 {cell_line} 的文件。")
        print("[INFO] 显示第一个文件的内容作为示例。")
        matched = [all_files[0]]

    for filepath in matched[:3]:  # 最多检查3个文件
        print("-" * 60)
        print(f"文件: {filepath.name}")
        print("-" * 60)

        try:
            if filepath.suffix == ".jsonl":
                data = load_jsonl(filepath)
            elif filepath.suffix == ".json":
                data = load_json(filepath)
                if isinstance(data, list):
                    pass
                elif isinstance(data, dict):
                    # 可能是 train/test 分组
                    for key in data:
                        if isinstance(data[key], list):
                            print(f"  键 '{key}': {len(data[key])} 条")
                    print()
                    # 取第一个列表
                    data = next((v for v in data.values() if isinstance(v, list)), [])
                else:
                    data = [data]
            else:
                print(f"  [WARN] 不支持的格式: {filepath.suffix}")
                continue

            print(f"  样本数量: {len(data)}")
            print()

            if data:
                # 显示一条实际数据
                print("  一条实际数据:")
                sample = data[0]
                if isinstance(sample, dict):
                    for key, value in sample.items():
                        val_str = str(value)
                        if len(val_str) > 100:
                            val_str = val_str[:100] + "..."
                        print(f"    {key}: {val_str}")
                else:
                    print(f"    {sample}")
                print()

                # 字段含义
                print("  字段含义:")
                if isinstance(sample, dict):
                    for key in sample.keys():
                        key_lower = key.lower()
                        if "pert" in key_lower or "gene" in key_lower and "label" not in key_lower:
                            print(f"    {key}: 扰动基因名称")
                        elif "label" in key_lower or "target" in key_lower:
                            print(f"    {key}: 标签 (正/负 或 方向)")
                        elif "text" in key_lower or "input" in key_lower or "question" in key_lower:
                            print(f"    {key}: 输入文本/问题")
                        elif "output" in key_lower or "answer" in key_lower or "response" in key_lower:
                            print(f"    {key}: 输出/答案")
                        elif "cell" in key_lower:
                            print(f"    {key}: 细胞系")
                        else:
                            print(f"    {key}: (需根据实际数据判断)")
                print()

                # 统计
                if isinstance(sample, dict):
                    # 找标签字段
                    label_key = None
                    for key in sample.keys():
                        if "label" in key.lower() or "target" in key.lower():
                            label_key = key
                            break

                    if label_key:
                        labels = [d.get(label_key) for d in data if isinstance(d, dict)]
                        from collections import Counter
                        label_counts = Counter(labels)
                        print(f"  标签分布 ({label_key}):")
                        for label, count in label_counts.most_common():
                            print(f"    {label}: {count}")
                        print()

                    # 找扰动基因字段
                    pert_key = None
                    for key in sample.keys():
                        if "pert" in key.lower() or ("gene" in key.lower() and "label" not in key.lower() and "set" not in key.lower()):
                            pert_key = key
                            break

                    if pert_key:
                        perts = [d.get(pert_key) for d in data if isinstance(d, dict)]
                        unique_perts = set(str(p) for p in perts)
                        print(f"  不同扰动基因数量: {len(unique_perts)}")
                        print(f"  前10个: {list(unique_perts)[:10]}")
                        print()

        except Exception as e:
            print(f"  [ERROR] 加载失败: {e}")
        print()

    print("=" * 60)
    print("检查完成")
    print("=" * 60)
    return 0


def main():
    parser = argparse.ArgumentParser(description="检查 PerturbQA 基准数据")
    parser.add_argument("--task", default="de", choices=["de", "direction", "gse", "gene_set_enrichment"],
                        help="任务类型")
    parser.add_argument("--cell-line", default="k562", choices=CELL_LINES,
                        help="细胞系")
    args = parser.parse_args()

    return inspect_task(args.task, args.cell_line)


if __name__ == "__main__":
    sys.exit(main())
