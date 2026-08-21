#!/usr/bin/env python3
"""安全检查 FASTQ、XML、文本矩阵、HDF5/GEF/H5AD 和坐标/注释文件。"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


COORD_NAMES = {
    "x": ["x", "xcoord", "x_coord", "spatial_x", "x_position"],
    "y": ["y", "ycoord", "y_coord", "spatial_y", "y_position"],
    "z": ["z", "zcoord", "z_coord", "spatial_z", "z_position"],
    "slice": ["slice_id", "section_id", "slice", "section"],
}
GENE_NAMES = ["gene", "geneid", "gene_id", "gene_name", "symbol"]
COUNT_NAMES = ["count", "counts", "midcounts", "umi", "umis", "expression"]
ANNOT_NAMES = ["cluster", "cell_type", "celltype", "tissue", "organ", "annotation"]


def opener(path: Path, mode: str = "rt"):
    return gzip.open(path, mode, encoding=None if "b" in mode else "utf-8-sig", errors=None if "b" in mode else "replace") if path.suffix == ".gz" else path.open(mode, encoding=None if "b" in mode else "utf-8-sig", errors=None if "b" in mode else "replace")


def inspect_fastq(path: Path, reads: int) -> dict[str, Any]:
    lengths: list[int] = []
    valid = 0
    with opener(path) as handle:
        for _ in range(reads):
            record = [handle.readline().rstrip("\n\r") for _ in range(4)]
            if not record[0]:
                break
            if record[0].startswith("@") and record[2].startswith("+"):
                valid += 1
                lengths.append(len(record[1]))
    return {"format": "FASTQ", "sampled_reads": valid, "read_lengths": lengths, "sequences_emitted": False}


def inspect_xml(path: Path) -> dict[str, Any]:
    root = ET.parse(path).getroot()
    items = []
    for elem in root.iter():
        if elem is root:
            continue
        text = (elem.text or "").strip()
        if (text or elem.attrib) and len(items) < 100:
            items.append({"tag": elem.tag, "value": text, "attributes": dict(elem.attrib)})
    return {"format": "XML", "root": root.tag, "root_attributes": dict(root.attrib), "values": items}


def delimiter_for(path: Path) -> str:
    name = path.name.lower()
    if ".tsv" in name or ".gem" in name:
        return "\t"
    with opener(path) as handle:
        sample = handle.read(8192)
    try:
        return csv.Sniffer().sniff(sample, delimiters=",\t").delimiter
    except csv.Error:
        return ","


def inspect_table(path: Path, max_rows: int) -> dict[str, Any]:
    delimiter = delimiter_for(path)
    with opener(path) as handle:
        reader = csv.reader(handle, delimiter=delimiter)
        header = next(reader, [])
        preview = []
        row_count = 0
        for row in reader:
            row_count += 1
            if len(preview) < max_rows:
                # 只报告结构，避免把人类数据值写进 JSON。
                preview.append({"column_count": len(row), "nonempty_count": sum(bool(value) for value in row)})
    normalized = {name.strip().lower(): name for name in header}
    candidates = {
        key: next((normalized[name] for name in names if name in normalized), None)
        for key, names in COORD_NAMES.items()
    }
    candidates["gene"] = next((normalized[name] for name in GENE_NAMES if name in normalized), None)
    candidates["count"] = next((normalized[name] for name in COUNT_NAMES if name in normalized), None)
    candidates["annotation"] = [normalized[name] for name in ANNOT_NAMES if name in normalized]
    return {
        "format": "delimited_text", "delimiter": repr(delimiter), "columns": header,
        "data_rows": row_count, "sampled_row_structure": preview, "field_candidates": candidates,
    }


def inspect_hdf5(path: Path) -> dict[str, Any]:
    import h5py

    items: list[dict[str, Any]] = []
    with h5py.File(path, "r") as handle:
        def visitor(name: str, obj: Any) -> None:
            if len(items) >= 500:
                return
            item: dict[str, Any] = {"name": name, "kind": type(obj).__name__}
            if isinstance(obj, h5py.Dataset):
                item.update({"shape": list(obj.shape), "dtype": str(obj.dtype)})
            items.append(item)
        handle.visititems(visitor)
    return {"format": "HDF5", "objects": items, "truncated": len(items) >= 500}


def inspect_h5ad(path: Path) -> dict[str, Any]:
    import anndata as ad
    from scipy import sparse

    data = ad.read_h5ad(path, backed="r")
    try:
        x = data.X
        result = {
            "format": "H5AD", "shape": list(data.shape), "x_type": type(x).__name__,
            "x_dtype": str(getattr(x, "dtype", "unknown")), "x_sparse": bool(sparse.issparse(x)),
            "obs_columns": list(data.obs.columns), "var_columns": list(data.var.columns),
            "obsm_keys": list(data.obsm.keys()), "uns_keys": list(data.uns.keys()),
            "layers_keys": list(data.layers.keys()), "raw_present": data.raw is not None,
            "obs_names_example": [str(value) for value in data.obs_names[:5]],
            "var_names_example": [str(value) for value in data.var_names[:5]],
        }
        return result
    finally:
        if getattr(data, "file", None) is not None:
            data.file.close()


def inspect(path: Path, reads: int, rows: int) -> dict[str, Any]:
    lower = path.name.lower()
    base = {"path": str(path.resolve()), "size_bytes": path.stat().st_size}
    if lower.endswith((".fastq", ".fq", ".fastq.gz", ".fq.gz")):
        details = inspect_fastq(path, reads)
    elif lower.endswith(".xml"):
        details = inspect_xml(path)
    elif lower.endswith(".h5ad"):
        details = inspect_h5ad(path)
    elif lower.endswith((".h5", ".hdf5", ".gef")):
        details = inspect_hdf5(path)
    elif lower.endswith((".csv", ".tsv", ".txt", ".gem", ".csv.gz", ".tsv.gz", ".gem.gz")):
        details = inspect_table(path, rows)
    else:
        raise ValueError(f"暂不支持的格式：{path.name}")
    return {**base, **details}


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--fastq-reads", type=int, default=20)
    parser.add_argument("--preview-rows", type=int, default=5)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    results = []
    for path in args.files:
        if not path.is_file():
            raise SystemExit(f"文件不存在：{path}")
        results.append(inspect(path, args.fastq_reads, args.preview_rows))
    output = json.dumps(results, ensure_ascii=False, indent=2)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(output, encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
