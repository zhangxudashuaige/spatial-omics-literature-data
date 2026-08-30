#!/usr/bin/env python3
"""从本地 H5MU 生成固定种子的配对小样本；不自动授权再分发。"""
from __future__ import annotations

import argparse
from pathlib import Path

import mudata as md
import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--cells", type=int, default=200)
    parser.add_argument("--features", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20250625)
    parser.add_argument("--acknowledge-license", action="store_true")
    args = parser.parse_args()
    if not args.acknowledge_license:
        parser.error("必须先确认原数据许可，再传入 --acknowledge-license")
    mdata = md.read_h5mu(args.input)
    common = None
    for adata in mdata.mod.values():
        names = set(adata.obs_names.astype(str))
        common = names if common is None else common & names
    common_names = np.array(sorted(common or set()))
    if not len(common_names):
        raise ValueError("模态之间没有共有细胞 ID")
    rng = np.random.default_rng(args.seed)
    chosen = np.sort(rng.choice(common_names, size=min(args.cells, len(common_names)), replace=False))
    mods = {}
    for name, adata in mdata.mod.items():
        feature_count = adata.n_vars if name.lower() in {"adt", "protein"} else min(args.features, adata.n_vars)
        selected_features = np.arange(feature_count)
        mods[name] = adata[chosen, selected_features].copy()
    sample = md.MuData(mods)
    sample.uns["sample_notice"] = "固定随机抽样，仅用于读取/CI，不用于复现论文指标。"
    sample.uns["sample_seed"] = args.seed
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sample.write_h5mu(args.output)
    print(f"写入 {args.output}，modalities={list(sample.mod)}, n_obs={sample.n_obs}")


if __name__ == "__main__":
    main()
