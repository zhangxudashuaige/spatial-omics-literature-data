#!/usr/bin/env python3
"""检查 HEIST 风格 H5AD 或分层 PyG/PT 样例，不把矩阵转成 dense。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


CELL_TYPE_KEYS = ("cell_type", "celltype", "cell_type_name", "annotation")
SLICE_KEYS = ("slice_id", "slice", "sample_id", "sample")
PATIENT_KEYS = ("patient_id", "patient", "donor_id", "donor")
CLINICAL_KEYS = ("pTR_label", "primary_outcome", "recurrence", "recurred", "response", "condition")
COORD_KEYS = ("spatial", "X_spatial", "spatial_2d", "spatial_3d")


def shape(value: Any) -> list[int] | None:
    current = getattr(value, "shape", None)
    return [int(item) for item in current] if current is not None else None


def unique_count(value: Any) -> int | None:
    if value is None:
        return None
    try:
        if hasattr(value, "nunique"):
            return int(value.nunique(dropna=True))
        import numpy as np

        array = value.detach().cpu().numpy() if hasattr(value, "detach") else value
        return int(np.unique(array).size)
    except Exception:
        return None


def sample_values(value: Any, limit: int = 20) -> list[str]:
    try:
        if hasattr(value, "dropna"):
            items = value.dropna().astype(str).unique().tolist()
        else:
            array = value.detach().cpu().numpy() if hasattr(value, "detach") else value
            items = list(dict.fromkeys(str(item) for item in array))
        return items[:limit]
    except Exception:
        return []


def find_obs_column(obs: Any, keys: tuple[str, ...]) -> str | None:
    lower = {str(column).lower(): str(column) for column in obs.columns}
    for key in keys:
        if key.lower() in lower:
            return lower[key.lower()]
    return None


def inspect_h5ad(path: Path) -> dict[str, Any]:
    try:
        import anndata
    except ImportError as exc:
        raise SystemExit("检查 H5AD 需要 anndata：pip install anndata") from exc

    adata = anndata.read_h5ad(path, backed="r")
    try:
        cell_key = find_obs_column(adata.obs, CELL_TYPE_KEYS)
        slice_key = find_obs_column(adata.obs, SLICE_KEYS)
        patient_key = find_obs_column(adata.obs, PATIENT_KEYS)
        coord_key = next((key for key in COORD_KEYS if key in adata.obsm), None)
        clinical = {}
        for requested in CLINICAL_KEYS:
            actual = find_obs_column(adata.obs, (requested,))
            if actual:
                clinical[actual] = sample_values(adata.obs[actual])
        return {
            "format": "h5ad",
            "path": str(path.resolve()),
            "expression_or_protein_shape": [int(adata.n_obs), int(adata.n_vars)],
            "x_type": type(adata.X).__name__,
            "coordinate_key": coord_key,
            "coordinate_shape": shape(adata.obsm[coord_key]) if coord_key else None,
            "cell_type_field": cell_key,
            "cell_type_count": unique_count(adata.obs[cell_key]) if cell_key else None,
            "slice_field": slice_key,
            "slice_count": unique_count(adata.obs[slice_key]) if slice_key else None,
            "patient_field": patient_key,
            "patient_count": unique_count(adata.obs[patient_key]) if patient_key else None,
            "clinical_labels": clinical,
            "obs_columns": [str(item) for item in adata.obs.columns],
            "obsm_keys": list(adata.obsm.keys()),
            "layers_keys": list(adata.layers.keys()),
            "spatial_graph": None,
            "coexpression_graphs": None,
        }
    finally:
        if getattr(adata, "file", None) is not None:
            adata.file.close()


def attr(obj: Any, names: tuple[str, ...]) -> tuple[str | None, Any]:
    for name in names:
        if hasattr(obj, name):
            return name, getattr(obj, name)
    return None, None


def graph_stats(graph: Any) -> dict[str, Any]:
    _, edge_index = attr(graph, ("edge_index",))
    nodes = getattr(graph, "num_nodes", None)
    if nodes is None:
        _, features = attr(graph, ("X", "x"))
        current_shape = shape(features)
        nodes = current_shape[0] if current_shape else None
    edge_shape = shape(edge_index)
    return {
        "nodes": int(nodes) if nodes is not None else None,
        "edges": edge_shape[1] if edge_shape and len(edge_shape) > 1 else None,
    }


def inspect_pt(path: Path, trust_pickle: bool) -> dict[str, Any]:
    if not trust_pickle:
        raise SystemExit(
            "拒绝读取 PT/PTH：torch.load 使用 pickle，可能执行任意代码。"
            "确认文件来自可信官方来源后追加 --trust-pickle。"
        )
    try:
        import torch
    except ImportError as exc:
        raise SystemExit("检查 PT 需要 torch 和创建对象时所用的 torch_geometric。") from exc

    loaded = torch.load(path, map_location="cpu", weights_only=False)
    graphs = loaded if isinstance(loaded, (list, tuple)) else [loaded]
    if not graphs:
        raise SystemExit("PT 文件中的列表为空")
    high = graphs[0]
    low = list(graphs[1:])
    coord_name, coordinates = attr(high, ("pos", "spatial", "X", "x"))
    cell_name, cell_types = attr(high, CELL_TYPE_KEYS + ("y",))
    slice_name, slices = attr(high, SLICE_KEYS)
    patient_name, patients = attr(high, PATIENT_KEYS)
    clinical = {}
    for key in CLINICAL_KEYS:
        if hasattr(high, key):
            clinical[key] = sample_values(getattr(high, key))
    low_stats = [graph_stats(graph) for graph in low]
    first_feature_shape = None
    if low:
        _, first_features = attr(low[0], ("X", "x"))
        first_feature_shape = shape(first_features)
    expression_shape = None
    if first_feature_shape:
        expression_shape = [len(low), first_feature_shape[0]]
    edge_counts = [item["edges"] for item in low_stats if item["edges"] is not None]
    node_counts = [item["nodes"] for item in low_stats if item["nodes"] is not None]
    return {
        "format": "pytorch_pickle",
        "path": str(path.resolve()),
        "object_type": type(loaded).__name__,
        "graph_count": len(graphs),
        "expression_or_protein_shape": expression_shape,
        "lower_graph_feature_shape": first_feature_shape,
        "coordinate_field": coord_name,
        "coordinate_shape": shape(coordinates),
        "cell_type_field": cell_name,
        "cell_type_count": unique_count(cell_types),
        "slice_field": slice_name,
        "slice_count": unique_count(slices),
        "patient_field": patient_name,
        "patient_count": unique_count(patients),
        "clinical_labels": clinical,
        "spatial_graph": graph_stats(high),
        "coexpression_graphs": {
            "count": len(low),
            "nodes_min": min(node_counts) if node_counts else None,
            "nodes_max": max(node_counts) if node_counts else None,
            "edges_min": min(edge_counts) if edge_counts else None,
            "edges_max": max(edge_counts) if edge_counts else None,
            "edges_total": sum(edge_counts) if edge_counts else None,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--trust-pickle", action="store_true")
    parser.add_argument("--output", type=Path, help="可选 JSON 输出路径")
    args = parser.parse_args()
    if not args.path.is_file():
        parser.error(f"文件不存在：{args.path}")
    suffix = args.path.suffix.lower()
    if suffix == ".h5ad":
        report = inspect_h5ad(args.path)
    elif suffix in {".pt", ".pth"}:
        report = inspect_pt(args.path, args.trust_pickle)
    else:
        parser.error("仅支持 .h5ad、.pt、.pth")
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
