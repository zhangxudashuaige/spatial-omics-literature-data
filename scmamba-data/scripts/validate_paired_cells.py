#!/usr/bin/env python3
"""验证 H5MU 两个模态的细胞配对关系。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import mudata as md
import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--modality-a", default="rna")
    parser.add_argument("--modality-b", default="atac")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    mdata = md.read_h5mu(args.path, backed="r")
    for name in (args.modality_a, args.modality_b):
        if name not in mdata.mod:
            raise KeyError(f"缺少模态 {name}；实际为 {list(mdata.mod)}")
    left = mdata.mod[args.modality_a].obs_names.astype(str)
    right = mdata.mod[args.modality_b].obs_names.astype(str)
    ls, rs = set(left), set(right)
    report = {
        "file": str(args.path), "modality_a": args.modality_a, "modality_b": args.modality_b,
        "cells_a": len(left), "cells_b": len(right), "equal_count": len(left) == len(right),
        "exact_order_match": len(left) == len(right) and bool(np.array_equal(left, right)),
        "intersection": len(ls & rs), "a_only": len(ls - rs), "b_only": len(rs - ls),
        "duplicate_a": int(left.duplicated().sum()), "duplicate_b": int(right.duplicated().sum()),
        "paired_success": len(left) == len(right) and bool(np.array_equal(left, right)),
    }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    if getattr(mdata, "file", None):
        mdata.file.close()


if __name__ == "__main__":
    main()
