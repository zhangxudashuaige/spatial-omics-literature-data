#!/usr/bin/env python3
"""检查常见空间表达文件，不整体稠密化大矩阵。"""
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
from scipy import sparse
from scipy.io import mmread


def inspect_10x_h5(path: Path) -> dict[str, object]:
    with h5py.File(path, "r") as handle:
        matrix = handle["matrix"]
        internal_shape = [int(x) for x in matrix["shape"][:]]
        return {
            "format": "10x_h5",
            "h5_internal_shape_gene_by_barcode": internal_shape,
            "analysis_shape_spot_by_gene": internal_shape[::-1],
            "data_dtype": str(matrix["data"].dtype),
            "nonzero_entries": int(matrix["data"].shape[0]),
            "nonzero_fraction": int(matrix["data"].shape[0]) / max(1, internal_shape[0] * internal_shape[1]),
            "barcodes": int(matrix["barcodes"].shape[0]),
            "features": int(matrix["features/name"].shape[0]),
            "feature_fields": list(matrix["features"].keys()),
            "first_barcodes": [x.decode() for x in matrix["barcodes"][:5]],
            "first_features": [x.decode() for x in matrix["features/name"][:5]],
        }


def inspect_h5ad(path: Path) -> dict[str, object]:
    import anndata as ad

    obj = ad.read_h5ad(path, backed="r")
    block = obj.X[: min(500, obj.n_obs)]
    nnz = int(block.nnz) if sparse.issparse(block) else int(np.count_nonzero(np.asarray(block)))
    report = {
        "format": "h5ad", "shape_spot_by_gene": list(obj.shape), "X_type": type(obj.X).__name__, "dtype": str(obj.X.dtype),
        "obs_columns": list(obj.obs.columns), "var_columns": list(obj.var.columns), "obsm": list(obj.obsm.keys()), "layers": list(obj.layers.keys()),
        "first_ids": obj.obs_names[:5].astype(str).tolist(), "sampled_nonzero": nnz,
    }
    obj.file.close()
    return report


def inspect_table(path: Path) -> dict[str, object]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", errors="replace") as handle:
        first_line = handle.readline().rstrip("\r\n")
    sep = "\t" if "\t" in first_line else ","
    tokens = first_line.split(sep)
    is_visium_positions = len(tokens) == 6 and tokens[0].endswith("-1") and all(token.lstrip("-").isdigit() for token in tokens[1:])
    names = ["barcode", "in_tissue", "array_row", "array_col", "pixel_row", "pixel_col"] if is_visium_positions else None
    table = pd.read_csv(path, sep=sep, nrows=5, header=None if names else "infer", names=names)
    with (gzip.open(path, "rt", encoding="utf-8", errors="replace") if path.suffix == ".gz" else path.open(encoding="utf-8", errors="replace")) as handle:
        lines = sum(1 for _ in handle)
    return {
        "format": "table", "delimiter": "tab" if sep == "\t" else "comma",
        "header_detected": not is_visium_positions, "rows": lines if is_visium_positions else max(0, lines - 1),
        "columns": list(table.columns), "head": table.to_dict(orient="records")
    }


def inspect_mtx(path: Path) -> dict[str, object]:
    matrix = mmread(path)
    return {"format": "matrix_market", "shape": list(matrix.shape), "type": type(matrix).__name__, "dtype": str(matrix.dtype), "nnz": int(getattr(matrix, "nnz", np.count_nonzero(matrix)))}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    name = args.path.name.lower()
    if name.endswith(".h5ad"):
        report = inspect_h5ad(args.path)
    elif name.endswith(".h5"):
        report = inspect_10x_h5(args.path)
    elif ".mtx" in name:
        report = inspect_mtx(args.path)
    elif any(token in name for token in (".csv", ".tsv", ".txt")):
        report = inspect_table(args.path)
    else:
        raise SystemExit("暂不支持该格式")
    report.update({"path": str(args.path), "size_bytes": args.path.stat().st_size})
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
