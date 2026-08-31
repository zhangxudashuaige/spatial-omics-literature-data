#!/usr/bin/env python3
"""检查标准10x Space Ranger输出，并可绘制spot覆盖图。"""
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path

import h5py
import pandas as pd


def expression_barcodes(root: Path) -> set[str]:
    h5_candidates = [root / "filtered_feature_bc_matrix.h5"]
    h5_candidates += list(root.glob("*filtered_feature_bc_matrix.h5"))
    for path in h5_candidates:
        if path.exists():
            with h5py.File(path, "r") as handle:
                return {x.decode() for x in handle["matrix/barcodes"][:]}
    barcode = root / "filtered_feature_bc_matrix" / "barcodes.tsv.gz"
    if barcode.exists():
        with gzip.open(barcode, "rt") as handle:
            return {line.strip() for line in handle if line.strip()}
    raise FileNotFoundError("没有找到filtered H5或barcodes.tsv.gz")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--overlay", type=Path)
    args = parser.parse_args()
    spatial = args.root / "spatial"
    positions = spatial / "tissue_positions.csv"
    legacy = spatial / "tissue_positions_list.csv"
    if positions.exists():
        table = pd.read_csv(positions)
        id_col = "barcode"
    elif legacy.exists():
        table = pd.read_csv(legacy, header=None, names=["barcode", "in_tissue", "array_row", "array_col", "pxl_row_in_fullres", "pxl_col_in_fullres"])
        id_col = "barcode"
    else:
        raise FileNotFoundError("缺少tissue_positions.csv/list.csv")
    expr = expression_barcodes(args.root)
    coords = set(table[id_col].astype(str))
    files = {
        "filtered_feature_bc_matrix.h5": (args.root / "filtered_feature_bc_matrix.h5").exists(),
        "matrix.mtx.gz": (args.root / "filtered_feature_bc_matrix" / "matrix.mtx.gz").exists(),
        "features.tsv.gz": (args.root / "filtered_feature_bc_matrix" / "features.tsv.gz").exists(),
        "barcodes.tsv.gz": (args.root / "filtered_feature_bc_matrix" / "barcodes.tsv.gz").exists(),
        "tissue_positions": positions.exists() or legacy.exists(),
        "scalefactors_json.json": (spatial / "scalefactors_json.json").exists(),
        "tissue_hires_image.png": (spatial / "tissue_hires_image.png").exists(),
        "tissue_lowres_image.png": (spatial / "tissue_lowres_image.png").exists(),
    }
    report = {"files": files, "expression_barcodes": len(expr), "spatial_barcodes": len(coords), "matched": len(expr & coords), "expression_only": len(expr - coords), "spatial_only": len(coords - expr)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.overlay:
        import matplotlib.pyplot as plt
        from PIL import Image

        image_path = spatial / "tissue_hires_image.png"
        if not image_path.exists():
            raise FileNotFoundError(image_path)
        scales = json.loads((spatial / "scalefactors_json.json").read_text())
        scale = float(scales["tissue_hires_scalef"])
        image = Image.open(image_path)
        x = table["pxl_col_in_fullres"] * scale
        y = table["pxl_row_in_fullres"] * scale
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.imshow(image)
        ax.scatter(x, y, s=1, facecolors="none", edgecolors="red", linewidths=0.2)
        ax.set_axis_off()
        args.overlay.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(args.overlay, dpi=150, bbox_inches="tight")


if __name__ == "__main__":
    main()
