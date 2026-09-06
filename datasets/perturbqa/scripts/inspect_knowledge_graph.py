#!/usr/bin/env python3
"""
检查 PerturbQA 生物知识图谱。

输出:
- 文件格式
- 节点数量
- 边数量
- 节点字段
- 边字段
- 5条真实关系示例
"""
import sys
import json
from pathlib import Path

KG_DIR = Path(__file__).resolve().parent.parent / "data" / "knowledge_graph"


def inspect_knowledge_graph():
    """检查知识图谱数据。"""
    print("=" * 60)
    print("PerturbQA 知识图谱检查")
    print("=" * 60)
    print()

    if not KG_DIR.exists():
        print(f"[ERROR] 目录不存在: {KG_DIR}")
        print("[ERROR] 请先运行: python scripts/download_data.py --file kg.zip --extract")
        return 1

    # 列出文件
    all_files = [f for f in KG_DIR.rglob("*") if f.is_file() and not f.name.startswith(".")]
    print(f"文件数量: {len(all_files)}")
    for f in sorted(all_files)[:20]:
        rel = f.relative_to(KG_DIR)
        size_kb = f.stat().st_size / 1024
        print(f"  {rel}: {size_kb:.1f} KB")
    if len(all_files) > 20:
        print(f"  ... 还有 {len(all_files) - 20} 个文件")
    print()

    if not all_files:
        print("[WARN] 目录为空。请先下载并解压 kg.zip。")
        return 1

    # 尝试加载节点和边文件
    nodes = None
    edges = None

    for f in all_files:
        name_lower = f.name.lower()
        if "node" in name_lower or "entity" in name_lower:
            if f.suffix == ".json":
                try:
                    with open(f, "r", encoding="utf-8") as fh:
                        data = json.load(fh)
                    if isinstance(data, list):
                        nodes = data
                        print(f"[INFO] 节点文件: {f.name} ({len(nodes)} 节点)")
                    elif isinstance(data, dict):
                        for key in data:
                            if isinstance(data[key], list):
                                nodes = data[key]
                                print(f"[INFO] 节点文件: {f.name}, 键 '{key}' ({len(nodes)} 节点)")
                                break
                except Exception as e:
                    print(f"[WARN] 加载节点文件失败: {e}")
            elif f.suffix in [".csv", ".tsv"]:
                try:
                    import pandas as pd
                    sep = "," if f.suffix == ".csv" else "\t"
                    df = pd.read_csv(f, sep=sep)
                    nodes = df.to_dict("records")
                    print(f"[INFO] 节点文件: {f.name} ({len(nodes)} 节点)")
                except Exception as e:
                    print(f"[WARN] 加载节点文件失败: {e}")

        if "edge" in name_lower or "relation" in name_lower or "triple" in name_lower:
            if f.suffix == ".json":
                try:
                    with open(f, "r", encoding="utf-8") as fh:
                        data = json.load(fh)
                    if isinstance(data, list):
                        edges = data
                        print(f"[INFO] 边文件: {f.name} ({len(edges)} 边)")
                    elif isinstance(data, dict):
                        for key in data:
                            if isinstance(data[key], list):
                                edges = data[key]
                                print(f"[INFO] 边文件: {f.name}, 键 '{key}' ({len(edges)} 边)")
                                break
                except Exception as e:
                    print(f"[WARN] 加载边文件失败: {e}")
            elif f.suffix in [".csv", ".tsv"]:
                try:
                    import pandas as pd
                    sep = "," if f.suffix == ".csv" else "\t"
                    df = pd.read_csv(f, sep=sep)
                    edges = df.to_dict("records")
                    print(f"[INFO] 边文件: {f.name} ({len(edges)} 边)")
                except Exception as e:
                    print(f"[WARN] 加载边文件失败: {e}")

    print()

    # 节点统计
    if nodes:
        print("-" * 60)
        print("节点信息")
        print("-" * 60)
        print(f"节点数量: {len(nodes)}")
        if isinstance(nodes[0], dict):
            print(f"节点字段: {list(nodes[0].keys())}")
            print()
            # 节点类型统计
            type_key = None
            for key in nodes[0].keys():
                if "type" in key.lower() or "kind" in key.lower() or "category" in key.lower():
                    type_key = key
                    break
            if type_key:
                from collections import Counter
                type_counts = Counter(n.get(type_key) for n in nodes)
                print(f"节点类型分布 ({type_key}):")
                for t, c in type_counts.most_common(15):
                    print(f"  {t}: {c}")
                print()
            print("前3个节点示例:")
            for n in nodes[:3]:
                print(f"  {n}")
        print()

    # 边统计
    if edges:
        print("-" * 60)
        print("边信息")
        print("-" * 60)
        print(f"边数量: {len(edges)}")
        if isinstance(edges[0], dict):
            print(f"边字段: {list(edges[0].keys())}")
            print()
            # 关系类型统计
            rel_key = None
            for key in edges[0].keys():
                if "relation" in key.lower() or "predicate" in key.lower() or "type" in key.lower() or "label" in key.lower():
                    rel_key = key
                    break
            if rel_key:
                from collections import Counter
                rel_counts = Counter(e.get(rel_key) for e in edges)
                print(f"关系类型分布 ({rel_key}):")
                for r, c in rel_counts.most_common(15):
                    print(f"  {r}: {c}")
                print()
            print("5条真实关系示例:")
            for e in edges[:5]:
                print(f"  {e}")
        print()

    if not nodes and not edges:
        print("[WARN] 未能自动识别节点和边文件。")
        print("[WARN] 请手动检查 data/knowledge_graph/ 目录中的文件。")
        print("[WARN] 文件格式可能与预期不同，以实际数据为准。")

    print("=" * 60)
    print("检查完成")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(inspect_knowledge_graph())
