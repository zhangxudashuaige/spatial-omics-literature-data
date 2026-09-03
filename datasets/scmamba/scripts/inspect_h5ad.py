#!/usr/bin/env python3
"""检查 H5AD 的结构、元数据和稀疏度。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import anndata as ad
import numpy as np
from scipy import sparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    obj = ad.read_h5ad(args.path, backed="r")
    matrix = obj.X
    if sparse.issparse(matrix):
        nnz = int(matrix.nnz)
        fraction = nnz / max(1, matrix.shape[0] * matrix.shape[1])
        note = "full sparse matrix"
    else:
        raw_sample = matrix[: min(1000, obj.n_obs)]
        if sparse.issparse(raw_sample):
            nnz = int(raw_sample.nnz)
            fraction = nnz / max(1, raw_sample.shape[0] * raw_sample.shape[1])
            note = "backed sparse, first <=1000 rows"
        else:
            sample = np.asarray(raw_sample)
            nnz = int(np.count_nonzero(sample))
            fraction = nnz / max(1, sample.size)
            note = "dense/backed, first <=1000 rows"
    columns = set(obj.obs.columns)
    report = {
        "file": str(args.path), "shape": list(obj.shape), "X_type": type(matrix).__name__, "dtype": str(matrix.dtype),
        "obs_columns": list(obj.obs.columns), "var_columns": list(obj.var.columns), "layers": list(obj.layers.keys()),
        "obsm": list(obj.obsm.keys()), "uns": list(obj.uns.keys()), "first_cells": obj.obs_names[:5].astype(str).tolist(),
        "first_features": obj.var_names[:5].astype(str).tolist(), "nonzero_fraction": fraction, "nonzero_scope": note,
        "semantic_columns": {key: key in columns for key in ("cell_type", "batch", "donor", "modality")},
    }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    obj.file.close()


if __name__ == "__main__":
    main()
