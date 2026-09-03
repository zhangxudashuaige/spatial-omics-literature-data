#!/usr/bin/env python3
"""检查表达、坐标、注释和图像之间的spot/cell ID对齐。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import h5py
import pandas as pd


def h5_barcodes(path: Path) -> list[str]:
    with h5py.File(path, "r") as handle:
        return [x.decode() for x in handle["matrix/barcodes"][:]]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expression-h5", type=Path, required=True)
    parser.add_argument("--coordinates", type=Path, required=True)
    parser.add_argument("--no-header", action="store_true")
    parser.add_argument("--id-column", default="barcode")
    parser.add_argument("--pixel-x", default="pixel_col")
    parser.add_argument("--pixel-y", default="pixel_row")
    parser.add_argument("--annotation", type=Path)
    parser.add_argument("--image", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    expr = pd.Index(h5_barcodes(args.expression_h5))
    if args.no_header:
        coords = pd.read_csv(args.coordinates, header=None, names=["barcode", "in_tissue", "array_row", "array_col", "pixel_row", "pixel_col"])
    else:
        coords = pd.read_csv(args.coordinates)
    coord = pd.Index(coords[args.id_column].astype(str))
    e_set, c_set = set(expr), set(coord)
    report: dict[str, object] = {
        "expression_ids": len(expr), "coordinate_ids": len(coord),
        "expression_duplicate_ids": int(expr.duplicated().sum()), "coordinate_duplicate_ids": int(coord.duplicated().sum()),
        "matched_ids": len(e_set & c_set), "expression_without_coordinates": len(e_set - c_set), "coordinates_without_expression": len(c_set - e_set),
        "expression_only_examples": sorted(e_set - c_set)[:20], "coordinate_only_examples": sorted(c_set - e_set)[:20],
    }
    if args.annotation:
        ann = pd.read_csv(args.annotation)
        ann_ids = set(ann[args.id_column].astype(str))
        report["annotation_ids"] = len(ann_ids)
        report["expression_without_annotation"] = len(e_set - ann_ids)
    if args.image:
        from PIL import Image

        with Image.open(args.image) as image:
            width, height = image.size
        valid = coords[args.pixel_x].between(0, width - 1) & coords[args.pixel_y].between(0, height - 1)
        report.update({"image_size": [width, height], "pixel_coordinates_in_bounds": int(valid.sum()), "pixel_coordinates_out_of_bounds": int((~valid).sum())})
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
