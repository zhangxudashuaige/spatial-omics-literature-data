#!/usr/bin/env python3
"""检查 GraphSAGE 官方目录、文件前缀或 ZIP，不修改输入数据。"""

from __future__ import annotations

import argparse
import io
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path
from typing import BinaryIO, TextIO

import numpy as np


REQUIRED_SUFFIXES = ("-G.json", "-id_map.json", "-class_map.json")
OPTIONAL_SUFFIXES = ("-feats.npy", "-walks.txt")


def find_prefix_in_names(names: list[str]) -> str:
    graph_names = [name for name in names if name.endswith("-G.json")]
    if len(graph_names) != 1:
        raise ValueError(f"需要恰好一个 *-G.json，实际找到 {len(graph_names)} 个：{graph_names}")
    return graph_names[0][: -len("-G.json")]


def load_json_binary(handle: BinaryIO) -> object:
    return json.load(io.TextIOWrapper(handle, encoding="utf-8"))


def normalize_node_id(value: object) -> str:
    return str(value)


def summarize(graph: dict, id_map: dict, class_map: dict, feats: np.ndarray | None, walks: int | None) -> dict:
    nodes = graph.get("nodes", [])
    links = graph.get("links", graph.get("edges", []))
    split_counts = Counter()
    for node in nodes:
        if bool(node.get("test", False)):
            split_counts["test"] += 1
        elif bool(node.get("val", False)):
            split_counts["validation"] += 1
        else:
            split_counts["train"] += 1

    label_values = list(class_map.values())
    if not label_values:
        label_summary = {"entries": 0, "kind": "empty"}
    elif isinstance(label_values[0], list):
        lengths = sorted({len(value) for value in label_values})
        positive = sum(sum(1 for item in value if bool(item)) for value in label_values)
        label_summary = {
            "entries": len(label_values),
            "kind": "multi_label_vector",
            "vector_lengths": lengths,
            "positive_assignments": positive,
        }
    else:
        label_summary = {
            "entries": len(label_values),
            "kind": "single_label",
            "unique_labels": len({str(value) for value in label_values}),
        }

    graph_ids = {normalize_node_id(node.get("id")) for node in nodes}
    id_map_ids = {normalize_node_id(key) for key in id_map}
    class_map_ids = {normalize_node_id(key) for key in class_map}
    return {
        "nodes": len(nodes),
        "edges": len(links),
        "split": dict(split_counts),
        "id_map_entries": len(id_map),
        "class_map": label_summary,
        "feature_shape": list(feats.shape) if feats is not None else None,
        "feature_dtype": str(feats.dtype) if feats is not None else None,
        "walk_pairs": walks,
        "id_consistency": {
            "graph_minus_id_map": len(graph_ids - id_map_ids),
            "graph_minus_class_map": len(graph_ids - class_map_ids),
        },
    }


def inspect_zip(path: Path) -> tuple[str, dict]:
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if not name.endswith("/")]
        prefix = find_prefix_in_names(names)
        for suffix in REQUIRED_SUFFIXES:
            if prefix + suffix not in names:
                raise FileNotFoundError(prefix + suffix)
        with archive.open(prefix + "-G.json") as handle:
            graph = load_json_binary(handle)
        with archive.open(prefix + "-id_map.json") as handle:
            id_map = load_json_binary(handle)
        with archive.open(prefix + "-class_map.json") as handle:
            class_map = load_json_binary(handle)
        feats = None
        if prefix + "-feats.npy" in names:
            with archive.open(prefix + "-feats.npy") as handle:
                feats = np.load(io.BytesIO(handle.read()), allow_pickle=False)
        walks = None
        if prefix + "-walks.txt" in names:
            with archive.open(prefix + "-walks.txt") as handle:
                walks = sum(1 for line in handle if line.strip())
    return prefix, summarize(graph, id_map, class_map, feats, walks)


def inspect_directory_or_prefix(path: Path) -> tuple[str, dict]:
    if path.is_dir():
        graph_files = list(path.glob("*-G.json"))
        if len(graph_files) != 1:
            raise ValueError(f"需要恰好一个 *-G.json，实际找到 {len(graph_files)} 个")
        prefix_path = Path(str(graph_files[0])[: -len("-G.json")])
    else:
        prefix_path = Path(str(path)[: -len("-G.json")]) if str(path).endswith("-G.json") else path

    required = {suffix: Path(str(prefix_path) + suffix) for suffix in REQUIRED_SUFFIXES}
    for file_path in required.values():
        if not file_path.exists():
            raise FileNotFoundError(file_path)
    graph = json.loads(required["-G.json"].read_text(encoding="utf-8"))
    id_map = json.loads(required["-id_map.json"].read_text(encoding="utf-8"))
    class_map = json.loads(required["-class_map.json"].read_text(encoding="utf-8"))

    feats_path = Path(str(prefix_path) + "-feats.npy")
    feats = np.load(feats_path, mmap_mode="r", allow_pickle=False) if feats_path.exists() else None
    walks_path = Path(str(prefix_path) + "-walks.txt")
    walks = None
    if walks_path.exists():
        with walks_path.open("r", encoding="utf-8") as handle:
            walks = sum(1 for line in handle if line.strip())
    return str(prefix_path), summarize(graph, id_map, class_map, feats, walks)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="GraphSAGE 目录、train_prefix、*-G.json 或 ZIP")
    parser.add_argument("--json", action="store_true", help="只输出 JSON")
    args = parser.parse_args()
    source = args.input.resolve()
    if not source.exists():
        parser.error(f"输入不存在：{source}")

    prefix, result = inspect_zip(source) if source.suffix.lower() == ".zip" else inspect_directory_or_prefix(source)
    payload = {"source": str(source), "prefix": prefix, **result}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"来源：{source}")
        print(f"前缀：{prefix}")
        print(f"节点数：{result['nodes']:,}")
        print(f"边数：{result['edges']:,}")
        print(f"训练/验证/测试：{result['split']}")
        print(f"特征矩阵：{result['feature_shape']} ({result['feature_dtype']})")
        print(f"标签：{result['class_map']}")
        print(f"随机游走节点对：{result['walk_pairs']}")
        print(f"ID 一致性：{result['id_consistency']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
