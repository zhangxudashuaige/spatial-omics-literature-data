#!/usr/bin/env python3
"""
检查 PerturbQA 模型输出。

展示:
- Summer 输入问题
- 检索到的扰动实验案例
- 模型原始输出
- 解析后的二分类或方向标签
- No-CoT 和 No-Retrieval 结果的区别
"""
import sys
import json
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent.parent / "data" / "model_outputs"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"


def load_jsonl(filepath):
    data = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def inspect_file(filepath, max_samples=3):
    """检查单个模型输出文件。"""
    print(f"文件: {filepath.name}")
    print(f"大小: {filepath.stat().st_size / 1024:.1f} KB")
    print()

    try:
        if filepath.suffix == ".jsonl":
            data = load_jsonl(filepath)
        elif filepath.suffix == ".json":
            data = load_json(filepath)
            if isinstance(data, dict):
                print(f"  顶层键: {list(data.keys())}")
                for key, val in data.items():
                    if isinstance(val, list):
                        print(f"    {key}: {len(val)} 条")
                    elif isinstance(val, (int, float, str)):
                        print(f"    {key}: {val}")
                print()
                # 取第一个列表
                data = next((v for v in data.values() if isinstance(v, list)), [])
            elif isinstance(data, list):
                pass
            else:
                data = [data]
        else:
            print(f"  [WARN] 不支持的格式: {filepath.suffix}")
            return

        print(f"  样本数量: {len(data)}")
        print()

        if data and isinstance(data[0], dict):
            print(f"  字段: {list(data[0].keys())}")
            print()

            for i, sample in enumerate(data[:max_samples]):
                print(f"  --- 样本 {i+1} ---")
                for key, value in sample.items():
                    val_str = str(value)
                    if len(val_str) > 200:
                        val_str = val_str[:200] + "..."
                    print(f"    {key}: {val_str}")
                print()

    except Exception as e:
        print(f"  [ERROR] 加载失败: {e}")
    print()


def main():
    print("=" * 60)
    print("PerturbQA 模型输出检查")
    print("=" * 60)
    print()

    # 列出 model_outputs 目录
    model_files = []
    if MODEL_DIR.exists():
        model_files = [f for f in MODEL_DIR.rglob("*") if f.is_file() and f.suffix in [".json", ".jsonl", ".csv"]]

    result_files = []
    if RESULTS_DIR.exists():
        result_files = [f for f in RESULTS_DIR.rglob("*") if f.is_file() and f.suffix in [".json", ".jsonl", ".csv"]]

    print(f"模型输出文件: {len(model_files)}")
    for f in sorted(model_files)[:15]:
        rel = f.relative_to(MODEL_DIR)
        print(f"  {rel}: {f.stat().st_size / 1024:.1f} KB")
    print()

    print(f"结果文件: {len(result_files)}")
    for f in sorted(result_files)[:15]:
        rel = f.relative_to(RESULTS_DIR)
        print(f"  {rel}: {f.stat().st_size / 1024:.1f} KB")
    print()

    if not model_files and not result_files:
        print("[WARN] 未找到模型输出文件。")
        print("[WARN] 请先运行: python scripts/download_data.py --all --extract")
        return 1

    # 检查 Summer 输出
    print("-" * 60)
    print("Summer 模型输出")
    print("-" * 60)
    summer_files = [f for f in model_files if "summer" in f.name.lower() and "enrichment" not in f.name.lower()]
    for f in summer_files[:2]:
        inspect_file(f)
    if not summer_files:
        print("  未找到 Summer 输出文件。")
        print()

    # 检查 No-CoT
    print("-" * 60)
    print("No-CoT 消融 (无 Chain-of-Thought)")
    print("-" * 60)
    nocot_files = [f for f in model_files if "nocot" in f.name.lower() or "no-cot" in f.name.lower()]
    for f in nocot_files[:1]:
        inspect_file(f)
    if not nocot_files:
        print("  未找到 No-CoT 文件。")
        print()

    # 检查 No-Retrieval
    print("-" * 60)
    print("No-Retrieval 消融 (无检索)")
    print("-" * 60)
    noret_files = [f for f in model_files if "noretrieve" in f.name.lower() or "no-retrieve" in f.name.lower()]
    for f in noret_files[:1]:
        inspect_file(f)
    if not noret_files:
        print("  未找到 No-Retrieval 文件。")
        print()

    # 结果对比
    print("-" * 60)
    print("模型对比说明")
    print("-" * 60)
    print("Summer (完整): 输入问题 + 检索扰动案例 + Chain-of-Thought 推理 → 输出")
    print("No-CoT: 移除 Chain-of-Thought，直接回答 → 测试推理链的作用")
    print("No-Retrieval: 移除检索案例，仅用问题回答 → 测试知识检索的作用")
    print()
    print("通过对比三者的性能，可以评估:")
    print("  - 检索案例对预测准确性的贡献")
    print("  - Chain-of-Thought 推理对答案质量的影响")
    print("  - 模型在不同任务 (DE/direction/GSE) 上的表现差异")
    print()

    print("=" * 60)
    print("检查完成")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
