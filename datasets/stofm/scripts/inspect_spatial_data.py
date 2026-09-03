#!/usr/bin/env python3
"""检查常见空间组学文件；不会将完整稀疏矩阵转为稠密矩阵。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
from scipy import sparse
from scipy.io import mmread

COORDINATE_KEYS = ("spatial", "X_spatial", "spatial_2d", "spatial_3d")


def inspect_h5ad(path: Path) -> dict:
    import anndata as ad
    obj = ad.read_h5ad(path, backed="r")
    block = obj.X[: min(1000, obj.n_obs)]
    nnz = int(block.nnz) if sparse.issparse(block) else int(np.count_nonzero(np.asarray(block)))
    obs_coordinate_pairs = [
        [x, y] for x, y in (("x", "y"), ("X", "Y"), ("pixel_col", "pixel_row"), ("pxl_col_in_fullres", "pxl_row_in_fullres"))
        if x in obj.obs.columns and y in obj.obs.columns
    ]
    report = {
        "format": "h5ad", "shape": list(obj.shape), "X_type": type(obj.X).__name__, "dtype": str(obj.X.dtype),
        "sampled_nonzero": nnz, "obs_columns": list(obj.obs.columns), "var_columns": list(obj.var.columns),
        "layers": list(obj.layers.keys()), "obsm": list(obj.obsm.keys()), "uns": list(obj.uns.keys()),
        "spatial_coordinate_fields": [k for k in obj.obsm.keys() if k in COORDINATE_KEYS or "spatial" in k.lower()],
        "obs_coordinate_pairs": obs_coordinate_pairs,
        "first_obs": obj.obs.head().reset_index().to_dict("records"), "first_var": obj.var.head().reset_index().to_dict("records"),
    }
    obj.file.close()
    return report


def h5_tree(path: Path) -> dict:
    rows = []
    with h5py.File(path, "r") as handle:
        handle.visititems(lambda name, obj: rows.append({"path": name, "shape": list(obj.shape), "dtype": str(obj.dtype)}) if isinstance(obj, h5py.Dataset) else None)
    return {"format": "hdf5_or_gef", "datasets": rows[:200], "dataset_count": len(rows)}


def table(path: Path) -> dict:
    sep = "\t" if path.suffix.lower() in {".tsv", ".gem"} or ".tsv" in path.name.lower() else ","
    frame = pd.read_csv(path, sep=sep, nrows=5, comment="#")
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        lines = sum(1 for line in handle if not line.startswith("#"))
    return {"format": "table", "rows_including_header": lines, "columns": list(frame.columns), "head": frame.to_dict("records")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    name = args.path.name.lower()
    if name.endswith(".h5ad"):
        report = inspect_h5ad(args.path)
    elif name.endswith((".h5", ".gef")):
        report = h5_tree(args.path)
    elif name.endswith((".csv", ".tsv", ".gem")):
        report = table(args.path)
    elif name.endswith(".mtx"):
        matrix = mmread(args.path)
        report = {"format": "mtx", "shape": list(matrix.shape), "dtype": str(matrix.dtype), "sparse_type": type(matrix).__name__, "nonzero": int(getattr(matrix, "nnz", np.count_nonzero(matrix)))}
    elif name.endswith(".npz"):
        loaded = np.load(args.path, allow_pickle=False)
        report = {"format": "npz", "arrays": {k: {"shape": list(loaded[k].shape), "dtype": str(loaded[k].dtype)} for k in loaded.files}}
    else:
        raise SystemExit("不支持该扩展名；GEF只做HDF5层级检查，深度解析需gefpy")
    report.update({"path": str(args.path), "size_bytes": args.path.stat().st_size})
    text = json.dumps(report, ensure_ascii=False, indent=2, default=str)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
