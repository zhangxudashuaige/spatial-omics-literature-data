#!/usr/bin/env python3
"""以内存安全方式检查常见单细胞、表格、NumPy、PyTorch 和图文件。"""
from __future__ import annotations

import argparse
import csv
import json
import pickletools
import zipfile
from pathlib import Path


def inspect_h5ad(path: Path) -> dict:
    import anndata as ad
    from scipy import sparse

    data = ad.read_h5ad(path, backed="r")
    return {
        "kind": "h5ad", "shape": list(data.shape), "x_type": type(data.X).__name__,
        "x_sparse": bool(sparse.issparse(data.X)), "x_dtype": str(data.X.dtype),
        "obs": list(data.obs.columns), "var": list(data.var.columns),
        "layers": list(data.layers.keys()), "obsm": list(data.obsm.keys()), "uns": list(data.uns.keys()),
    }


def inspect_numpy(path: Path) -> dict:
    import numpy as np
    value = np.load(path, mmap_mode="r", allow_pickle=False)
    if isinstance(value, np.lib.npyio.NpzFile):
        return {"kind": "npz", "arrays": {k: {"shape": list(value[k].shape), "dtype": str(value[k].dtype)} for k in value.files}}
    return {"kind": "npy", "shape": list(value.shape), "dtype": str(value.dtype)}


def inspect_table(path: Path) -> dict:
    opener = __import__("gzip").open if path.suffix == ".gz" else open
    delimiter = "\t" if ".tsv" in path.name or ".txt" in path.name else ","
    with opener(path, "rt", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.reader(handle, delimiter=delimiter)
        header = next(reader, [])
        preview, rows = [], 0
        for row in reader:
            rows += 1
            if len(preview) < 5:
                preview.append(row)
    return {"kind": "table", "rows": rows, "columns": len(header), "column_names": header, "head": preview}


def inspect_torch(path: Path) -> dict:
    import torch
    try:
        obj = torch.load(path, map_location="cpu", weights_only=True)
    except Exception as exc:
        return {"kind": "torch", "status": "not_safely_loadable_with_weights_only", "error": str(exc)}

    def describe(value):
        if torch.is_tensor(value):
            return {"shape": list(value.shape), "dtype": str(value.dtype)}
        if isinstance(value, dict):
            return {str(k): describe(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [describe(v) for v in value[:20]]
        return type(value).__name__
    return {"kind": "torch", "object": describe(obj)}


def inspect_one(path: Path) -> dict:
    lower = path.name.lower()
    if lower.endswith(".h5ad"):
        return inspect_h5ad(path)
    if lower.endswith((".npy", ".npz")):
        return inspect_numpy(path)
    if lower.endswith((".csv", ".tsv", ".txt", ".csv.gz", ".tsv.gz")):
        return inspect_table(path)
    if lower.endswith((".pt", ".pth")):
        return inspect_torch(path)
    if lower.endswith(".zip"):
        with zipfile.ZipFile(path) as zf:
            return {"kind": "zip", "members": len(zf.infolist()), "uncompressed_bytes": sum(x.file_size for x in zf.infolist())}
    if lower.endswith((".pkl", ".pickle")):
        with path.open("rb") as handle:
            ops = [op.name for op, _, _ in pickletools.genops(handle)]
        return {"kind": "pickle", "status": "not_deserialized_for_safety", "opcode_count": len(ops)}
    return {"kind": "unhandled", "size_bytes": path.stat().st_size}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    paths = [args.path] if args.path.is_file() else sorted(p for p in args.path.rglob("*") if p.is_file())
    report = {}
    for path in paths:
        try:
            report[str(path)] = inspect_one(path)
        except Exception as exc:
            report[str(path)] = {"error": f"{type(exc).__name__}: {exc}"}
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()

