#!/usr/bin/env python3
"""从10x H5和坐标表生成固定种子的本地H5AD小样本。"""
from __future__ import annotations

import argparse
from pathlib import Path

import anndata as ad
import h5py
import numpy as np
import pandas as pd
from scipy import sparse


def read_10x(path: Path) -> tuple[sparse.csr_matrix, list[str], list[str]]:
    with h5py.File(path, "r") as handle:
        group = handle["matrix"]
        shape = tuple(int(x) for x in group["shape"][:])
        matrix = sparse.csc_matrix((group["data"][:], group["indices"][:], group["indptr"][:]), shape=shape).T.tocsr()
        barcodes = [x.decode() for x in group["barcodes"][:]]
        genes = [x.decode() for x in group["features/name"][:]]
    return matrix, barcodes, genes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expression-h5", type=Path, required=True)
    parser.add_argument("--coordinates", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--spots", type=int, default=200)
    parser.add_argument("--genes", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20210728)
    parser.add_argument("--acknowledge-license", action="store_true")
    args = parser.parse_args()
    if not args.acknowledge_license:
        parser.error("先核实来源许可，再传入--acknowledge-license")
    matrix, barcodes, genes = read_10x(args.expression_h5)
    if not (100 <= args.spots <= 500 and 200 <= args.genes <= 1000):
        parser.error("spots必须为100–500，genes必须为200–1000")
    coords = pd.read_csv(args.coordinates, header=None, names=["barcode", "in_tissue", "array_row", "array_col", "pixel_row", "pixel_col"], index_col=0)
    common = np.array(sorted(set(barcodes) & set(coords.index.astype(str))))
    rng = np.random.default_rng(args.seed)
    chosen = np.sort(rng.choice(common, size=min(args.spots, len(common)), replace=False))
    barcode_index = pd.Index(barcodes).get_indexer(chosen)
    sub = matrix[barcode_index]
    detected = np.asarray((sub > 0).sum(axis=0)).ravel()
    gene_index = np.argsort(-detected, kind="stable")[: min(args.genes, len(genes))]
    obj = ad.AnnData(X=sub[:, gene_index], obs=coords.loc[chosen].copy(), var=pd.DataFrame(index=np.array(genes)[gene_index]))
    obj.uns["sample_notice"] = "固定随机抽样，仅用于程序检查，不用于复现SpaGCN论文指标。"
    obj.uns["source"] = str(args.expression_h5)
    obj.uns["seed"] = args.seed
    args.output.parent.mkdir(parents=True, exist_ok=True)
    obj.write_h5ad(args.output)
    coords.loc[chosen].to_csv(args.output.with_suffix(".coordinates.csv"))
    print(f"写入{args.output}，shape={obj.shape}，seed={args.seed}")


if __name__ == "__main__":
    main()
