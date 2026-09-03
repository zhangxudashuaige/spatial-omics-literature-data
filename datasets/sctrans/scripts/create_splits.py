#!/usr/bin/env python3
"""按标签分层建立固定种子的 80/20 cell-ID 划分。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import anndata as ad
import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("input", type=Path); parser.add_argument("--label-column", required=True); parser.add_argument("--output", required=True, type=Path); parser.add_argument("--seed", type=int, default=20260829); parser.add_argument("--train-fraction", type=float, default=0.8); args = parser.parse_args()
    a = ad.read_h5ad(args.input, backed="r")
    if args.label_column not in a.obs: raise SystemExit(f"missing label column: {args.label_column}")
    rng = np.random.default_rng(args.seed); train, test = [], []
    labels = a.obs[args.label_column].astype(str).to_numpy(); ids = a.obs_names.astype(str).to_numpy()
    for label in sorted(set(labels)):
        idx = np.flatnonzero(labels == label); rng.shuffle(idx); cut = int(round(len(idx) * args.train_fraction)); train.extend(ids[idx[:cut]]); test.extend(ids[idx[cut:]])
    result = {"source": str(args.input), "label_column": args.label_column, "seed": args.seed, "train_fraction": args.train_fraction, "train_cell_ids": train, "test_cell_ids": test}
    args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(result, indent=2), encoding="utf-8"); print(f"train={len(train)}, test={len(test)}")


if __name__ == "__main__": main()

