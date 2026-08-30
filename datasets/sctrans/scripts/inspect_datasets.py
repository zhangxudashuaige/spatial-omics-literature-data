#!/usr/bin/env python3
"""检查 H5AD、10X MTX 和表格；使用分块/稀疏操作。"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
from pathlib import Path

import numpy as np
from scipy import io, sparse


def candidate(columns, words):
    for word in words:
        for column in columns:
            if word in str(column).lower(): return column
    return None


def summarize_matrix(x) -> dict:
    if sparse.issparse(x):
        finite = bool(np.isfinite(x.data).all()); sums = np.asarray(x.sum(axis=1)).ravel(); nnz = np.asarray(x.getnnz(axis=1)).ravel()
    else:
        arr = np.asarray(x); finite = bool(np.isfinite(arr).all()); sums = arr.sum(axis=1); nnz = np.count_nonzero(arr, axis=1)
    return {"shape": list(x.shape), "matrix_type": type(x).__name__, "dtype": str(x.dtype), "all_finite": finite, "total_expression": {"min": float(sums.min()), "median": float(np.median(sums)), "max": float(sums.max())}, "nonzero_genes": {"min": int(nnz.min()), "median": float(np.median(nnz)), "max": int(nnz.max())}}


def h5ad(path: Path) -> dict:
    import anndata as ad
    a = ad.read_h5ad(path, backed="r")
    label = candidate(a.obs.columns, ["cell_type", "celltype", "annotation", "label", "cluster"])
    donor = candidate(a.obs.columns, ["donor", "patient", "individual"])
    batch = candidate(a.obs.columns, ["batch", "sample", "library"])
    totals, nonzero, finite = [], [], True
    for start in range(0, a.n_obs, 4096):
        block = a.X[start:min(start + 4096, a.n_obs)]
        if sparse.issparse(block):
            totals.extend(np.asarray(block.sum(axis=1)).ravel()); nonzero.extend(np.asarray(block.getnnz(axis=1)).ravel()); finite &= bool(np.isfinite(block.data).all())
        else:
            block = np.asarray(block); totals.extend(block.sum(axis=1)); nonzero.extend(np.count_nonzero(block, axis=1)); finite &= bool(np.isfinite(block).all())
    result = {"shape": list(a.shape), "matrix_type": type(a.X).__name__, "dtype": str(a.X.dtype), "all_finite": finite, "total_expression": {"min": float(np.min(totals)), "median": float(np.median(totals)), "max": float(np.max(totals))}, "nonzero_genes": {"min": int(np.min(nonzero)), "median": float(np.median(nonzero)), "max": int(np.max(nonzero))}}
    result.update({"kind": "h5ad", "obs_columns": list(map(str, a.obs.columns)), "var_columns": list(map(str, a.var.columns)), "duplicate_genes": int(a.var_names.duplicated().sum()), "duplicate_cells": int(a.obs_names.duplicated().sum()), "cell_label_column": None if label is None else str(label), "cell_type_counts": {} if label is None else {str(k): int(v) for k, v in a.obs[label].value_counts().items()}, "donor_column": None if donor is None else str(donor), "donor_count": None if donor is None else int(a.obs[donor].nunique()), "batch_column": None if batch is None else str(batch), "batch_count": None if batch is None else int(a.obs[batch].nunique()), "layers": list(map(str, a.layers.keys())), "obsm": list(map(str, a.obsm.keys()))})
    return result


def mtx(path: Path) -> dict:
    matrix = io.mmread(path).tocsr()
    return {"kind": "matrix_market", **summarize_matrix(matrix)}


def table(path: Path) -> dict:
    opener = gzip.open if path.suffix == ".gz" else open
    delimiter = "\t" if ".txt" in path.name or ".tsv" in path.name else ","
    with opener(path, "rt", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.reader(handle, delimiter=delimiter); header = next(reader, []); preview = []; rows = 0; widths = set()
        for row in reader:
            rows += 1; widths.add(len(row))
            if len(preview) < 5: preview.append(row[:20])
    return {"kind": "table", "rows": rows, "columns_from_header": len(header), "observed_row_widths": sorted(widths), "column_names": header[:100], "head": preview}


def create_sample(path: Path, output: Path, seed: int = 20260829) -> None:
    import anndata as ad
    # pandas 3 may expose nullable StringArray columns. anndata requires an
    # explicit opt-in before writing them; without this, a valid input H5AD can
    # be inspected but its CI/sample subset unexpectedly fails at write time.
    ad.settings.allow_write_nullable_strings = True
    a = ad.read_h5ad(path, backed="r"); label = candidate(a.obs.columns, ["cell_type", "celltype", "annotation", "label", "cluster"]); rng = np.random.default_rng(seed)
    if label is None:
        cells = rng.choice(a.n_obs, min(100, a.n_obs), replace=False)
    else:
        values = a.obs[label].astype(str).to_numpy(); cells = np.concatenate([rng.choice(np.flatnonzero(values == value), min(10, int(np.sum(values == value))), replace=False) for value in sorted(set(values))])
    sub = a[np.sort(np.unique(cells)), :].to_memory()
    if sub.n_vars > 500:
        x = sub.X
        if sparse.issparse(x): mean = np.asarray(x.mean(0)).ravel(); mean2 = np.asarray(x.power(2).mean(0)).ravel()
        else: mean = np.asarray(x).mean(0); mean2 = np.square(np.asarray(x)).mean(0)
        sub = sub[:, np.sort(np.argsort(mean2 - mean * mean)[-500:])].copy()
    sub.uns["sample_notice"] = "Structure/CI sample only; not for reproducing SCTrans results."; sub.uns["sample_seed"] = seed
    output.parent.mkdir(parents=True, exist_ok=True); sub.write_h5ad(output)


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("path", type=Path); parser.add_argument("--output", type=Path); parser.add_argument("--create-samples", action="store_true"); parser.add_argument("--sample-dir", type=Path, default=Path(__file__).resolve().parents[1] / "sample"); args = parser.parse_args()
    files = [args.path] if args.path.is_file() else sorted(p for p in args.path.rglob("*") if p.is_file())
    report = {}
    for path in files:
        try:
            lower = path.name.lower()
            if lower.endswith(".h5ad"):
                value = h5ad(path)
                if args.create_samples: create_sample(path, args.sample_dir / f"{path.stem}.sample.h5ad")
            elif lower.endswith((".mtx", ".mtx.gz")): value = mtx(path)
            elif lower.endswith((".csv", ".tsv", ".txt", ".csv.gz", ".tsv.gz", ".txt.gz")): value = table(path)
            elif lower.endswith(".rds"): value = {"kind": "RDS", "status": "inspect_in_R_to_avoid_unsafe_or_lossy_conversion", "size_bytes": path.stat().st_size}
            else: continue
            report[str(path)] = value
        except Exception as exc: report[str(path)] = {"error": f"{type(exc).__name__}: {exc}"}
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output: args.output.write_text(rendered, encoding="utf-8")
    print(rendered)


if __name__ == "__main__": main()
