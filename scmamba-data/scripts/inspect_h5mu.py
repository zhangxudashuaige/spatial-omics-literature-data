#!/usr/bin/env python3
"""检查 MuData/H5MU，不把大型稀疏矩阵转为稠密矩阵。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import mudata as md
import numpy as np
from scipy import sparse


def matrix_summary(matrix) -> dict[str, object]:
    shape = list(matrix.shape)
    result: dict[str, object] = {"shape": shape, "type": type(matrix).__name__, "dtype": str(matrix.dtype)}
    if sparse.issparse(matrix):
        nnz = int(matrix.nnz)
        denom_rows = shape[0]
    else:
        raw_block = matrix[: min(1000, shape[0])]
        if sparse.issparse(raw_block):
            nnz = int(raw_block.nnz)
            result["nnz_note"] = "backed稀疏矩阵仅统计前1000行"
        else:
            block = np.asarray(raw_block)
            nnz = int(np.count_nonzero(block))
            result["nnz_note"] = "backed/稠密矩阵仅统计前1000行"
        denom_rows = min(shape[0], 1000)
    denom = max(1, denom_rows * shape[1])
    result.update({"nnz": nnz, "nonzero_fraction": nnz / denom})
    return result


def inspect(path: Path) -> dict[str, object]:
    mdata = md.read_h5mu(path, backed="r")
    report: dict[str, object] = {"file": str(path), "modalities": list(mdata.mod.keys()), "global_obs_columns": list(mdata.obs.columns)}
    mods: dict[str, object] = {}
    for name, adata in mdata.mod.items():
        mods[name] = {
            "shape": list(adata.shape),
            "X": matrix_summary(adata.X),
            "obs_columns": list(adata.obs.columns),
            "var_columns": list(adata.var.columns),
            "layers": list(adata.layers.keys()),
            "obsm": list(adata.obsm.keys()),
            "uns": list(adata.uns.keys()),
            "first_cells": adata.obs_names[:5].astype(str).tolist(),
            "first_features": adata.var_names[:5].astype(str).tolist(),
            "duplicate_cells": int(adata.obs_names.duplicated().sum()),
            "duplicate_features": int(adata.var_names.duplicated().sum()),
        }
    report["modality_details"] = mods
    names = list(mdata.mod)
    pairing: dict[str, object] = {}
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            a = mdata.mod[left].obs_names.astype(str)
            b = mdata.mod[right].obs_names.astype(str)
            pairing[f"{left}__{right}"] = {
                "same_count": len(a) == len(b),
                "same_order": len(a) == len(b) and bool(np.array_equal(a, b)),
                "intersection": len(set(a).intersection(b)),
                "left_only": len(set(a).difference(b)),
                "right_only": len(set(b).difference(a)),
            }
    report["pairing"] = pairing
    if getattr(mdata, "file", None):
        mdata.file.close()
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = inspect(args.path)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
