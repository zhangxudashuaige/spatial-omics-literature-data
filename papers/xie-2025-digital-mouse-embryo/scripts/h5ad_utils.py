"""H5AD 字段与坐标的保守自动识别工具。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np


FIELD_PATTERNS = {
    "cell_type": ("cell_type", "celltype", "annotation", "identity", "label"),
    "germ_layer": ("germ", "layer", "mesoderm", "endoderm", "ectoderm"),
    "section": ("section", "slice", "z_index", "serial"),
    "stage": ("stage", "development", "age", "timepoint"),
    "cluster": ("cluster", "leiden", "louvain", "community"),
}


def find_candidate_columns(columns: list[str]) -> dict[str, list[str]]:
    """按关键词返回候选列；结果只是候选，不代表已确认语义。"""
    result: dict[str, list[str]] = {}
    for role, patterns in FIELD_PATTERNS.items():
        result[role] = [
            col for col in columns if any(p in col.lower() for p in patterns)
        ]
    return result


def find_coordinate_candidates(adata: Any) -> list[dict[str, Any]]:
    """搜索 obsm 和 obs 中可能的二维/三维坐标。"""
    candidates: list[dict[str, Any]] = []
    for key in adata.obsm.keys():
        value = adata.obsm[key]
        shape = tuple(int(v) for v in getattr(value, "shape", ()))
        if len(shape) == 2 and shape[1] >= 2:
            candidates.append(
                {
                    "source": "obsm",
                    "key": str(key),
                    "dimensions": shape[1],
                    "shape": list(shape),
                }
            )

    lower = {str(c).lower(): str(c) for c in adata.obs.columns}
    groups = [
        ("x", "y"),
        ("x", "y", "z"),
        ("spatial_x", "spatial_y"),
        ("spatial_x", "spatial_y", "spatial_z"),
        ("x_3d", "y_3d", "z_3d"),
        ("3d_x", "3d_y", "3d_z"),
    ]
    for group in groups:
        if all(g in lower for g in group):
            cols = [lower[g] for g in group]
            candidates.append(
                {"source": "obs", "key": cols, "dimensions": len(cols)}
            )
    return candidates


def select_coordinates(adata: Any, dimensions: int = 2) -> tuple[np.ndarray, str]:
    """选择可用坐标，优先名称含 spatial/3d 的 obsm。"""
    candidates = find_coordinate_candidates(adata)
    eligible = [c for c in candidates if c["dimensions"] >= dimensions]
    if not eligible:
        raise KeyError(f"没有发现至少 {dimensions} 维的坐标候选")
    eligible.sort(
        key=lambda c: (
            0 if "spatial" in str(c["key"]).lower() else 1,
            0 if dimensions == 3 and "3d" in str(c["key"]).lower() else 1,
        )
    )
    chosen = eligible[0]
    if chosen["source"] == "obsm":
        array = np.asarray(adata.obsm[chosen["key"]])[:, :dimensions]
        label = f"obsm[{chosen['key']!r}]"
    else:
        cols = chosen["key"][:dimensions]
        array = adata.obs[cols].to_numpy()
        label = "obs[" + ", ".join(cols) + "]"
    return array, label


def choose_h5ad(project_root: Path) -> Path:
    """优先选择最小的真实 H5AD，否则选择本地合成测试对象。"""
    real_dir = project_root / "data" / "external" / "GSE278603" / "h5ad"
    real = sorted(real_dir.glob("*.h5ad"), key=lambda p: p.stat().st_size)
    if real:
        return real[0]
    synthetic = project_root / "data" / "processed" / "synthetic_test.h5ad"
    if synthetic.exists():
        return synthetic
    raise FileNotFoundError(
        "没有 H5AD。请先下载解压，或运行 create_sample_data.py --synthetic"
    )


def gene_vector(adata: Any, gene: str) -> np.ndarray:
    """安全读取一个基因向量，不把整个矩阵转成 dense。"""
    if gene not in adata.var_names:
        raise KeyError(f"基因 {gene} 不在 var_names 中")
    matrix = adata[:, gene].X
    if hasattr(matrix, "toarray"):
        matrix = matrix.toarray()
    return np.asarray(matrix).reshape(-1)
