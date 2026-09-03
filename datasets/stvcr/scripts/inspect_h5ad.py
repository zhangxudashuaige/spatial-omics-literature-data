#!/usr/bin/env python3
"""分块检查 H5AD；不会把完整稀疏矩阵转成稠密矩阵。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy import sparse


def choose(columns, terms):
    lowered = {str(c).lower(): c for c in columns}
    for term in terms:
        if term in lowered:
            return lowered[term]
    for term in terms:
        for low, original in lowered.items():
            if term in low:
                return original
    return None


def inspect(path: Path) -> dict:
    import anndata as ad

    a = ad.read_h5ad(path, backed="r")
    cell_field = choose(a.obs.columns, ["cell_type", "celltype", "type", "annotation", "cluster", "tissue"])
    time_field = choose(a.obs.columns, ["time", "stage", "dpi"])
    spatial_keys = [str(k) for k in a.obsm.keys() if any(x in str(k).lower() for x in ("spatial", "coord", "align"))]
    total_counts, nonzero, finite = [], [], True
    for start in range(0, a.n_obs, 4096):
        block = a.X[start : min(start + 4096, a.n_obs)]
        if sparse.issparse(block):
            total_counts.extend(np.asarray(block.sum(axis=1)).ravel().tolist())
            nonzero.extend(np.asarray(block.getnnz(axis=1)).ravel().tolist())
            finite &= bool(np.isfinite(block.data).all())
        else:
            arr = np.asarray(block)
            total_counts.extend(arr.sum(axis=1).tolist())
            nonzero.extend(np.count_nonzero(arr, axis=1).tolist())
            finite &= bool(np.isfinite(arr).all())
    report = {
        "file": str(path), "size_bytes": path.stat().st_size, "shape": list(a.shape),
        "x_type": type(a.X).__name__, "x_dtype": str(a.X.dtype),
        "obs_columns": list(map(str, a.obs.columns)),
        "obs_non_null_fraction": {str(c): float(a.obs[c].notna().mean()) for c in a.obs.columns},
        "var_columns": list(map(str, a.var.columns)), "layers": list(map(str, a.layers.keys())),
        "obsm": {str(k): list(a.obsm[k].shape) for k in a.obsm.keys()}, "uns": list(map(str, a.uns.keys())),
        "spatial_coordinate_candidates": spatial_keys, "time_field": None if time_field is None else str(time_field),
        "time_values": [] if time_field is None else list(map(str, a.obs[time_field].dropna().unique())),
        "cell_type_field": None if cell_field is None else str(cell_field),
        "cell_type_counts": {} if cell_field is None else {str(k): int(v) for k, v in a.obs[cell_field].value_counts(dropna=False).items()},
        "nonzero_genes_per_cell": {"min": int(np.min(nonzero)), "median": float(np.median(nonzero)), "max": int(np.max(nonzero))},
        "total_expression_per_cell": {"min": float(np.min(total_counts)), "median": float(np.median(total_counts)), "max": float(np.max(total_counts))},
        "all_expression_values_finite": finite,
        "duplicate_gene_ids": int(a.var_names.duplicated().sum()), "duplicate_cell_ids": int(a.obs_names.duplicated().sum()),
    }
    return report


def create_sample(path: Path, output: Path, seed: int = 20260829) -> None:
    import anndata as ad
    rng = np.random.default_rng(seed)
    backed = ad.read_h5ad(path, backed="r")
    field = choose(backed.obs.columns, ["cell_type", "celltype", "type", "annotation", "cluster", "tissue"])
    if field is None:
        selected = rng.choice(backed.n_obs, size=min(100, backed.n_obs), replace=False)
    else:
        selected = np.concatenate([rng.choice(np.flatnonzero((backed.obs[field] == value).to_numpy()), size=min(10, int((backed.obs[field] == value).sum())), replace=False) for value in backed.obs[field].dropna().unique()])
    selected = np.sort(np.unique(selected))
    sub = backed[selected, :].to_memory()
    if sub.n_vars > 500:
        x = sub.X
        if sparse.issparse(x):
            mean = np.asarray(x.mean(axis=0)).ravel(); mean2 = np.asarray(x.power(2).mean(axis=0)).ravel()
        else:
            arr = np.asarray(x); mean = arr.mean(axis=0); mean2 = np.square(arr).mean(axis=0)
        genes = np.argsort(mean2 - mean * mean)[-500:]
        sub = sub[:, np.sort(genes)].copy()
    sub.uns["sample_notice"] = "Structure/CI sample only; not for reproducing paper results."
    sub.uns["sample_seed"] = seed
    output.parent.mkdir(parents=True, exist_ok=True)
    sub.write_h5ad(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--sample-output", type=Path)
    args = parser.parse_args()
    paths = [args.path] if args.path.is_file() else sorted(args.path.glob("*.h5ad"))
    reports = [inspect(p) for p in paths]
    text = json.dumps(reports, indent=2, ensure_ascii=False)
    if args.output: args.output.write_text(text, encoding="utf-8")
    print(text)
    if args.sample_output:
        if len(paths) != 1: raise SystemExit("--sample-output requires exactly one input H5AD")
        create_sample(paths[0], args.sample_output)


if __name__ == "__main__": main()
