#!/usr/bin/env python3
"""显式统一多个 H5AD 的基因 ID，并取交集；不会假装这是论文未披露流程。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import anndata as ad


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("inputs", nargs="+", type=Path); parser.add_argument("--output-dir", required=True, type=Path); parser.add_argument("--case", choices=["keep", "upper"], default="keep"); args = parser.parse_args()
    # Needed when source metadata uses pandas nullable string columns.
    ad.settings.allow_write_nullable_strings = True
    objects = [ad.read_h5ad(path) for path in args.inputs]
    for obj in objects:
        names = obj.var_names.astype(str)
        obj.var_names = names.str.upper() if args.case == "upper" else names
        if obj.var_names.duplicated().any():
            raise SystemExit("duplicate genes detected; choose and document an aggregation rule before alignment")
    common = sorted(set.intersection(*(set(obj.var_names) for obj in objects)))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for index, (source, obj) in enumerate(zip(args.inputs, objects), start=1):
        output = args.output_dir / f"{index:02d}_{source.stem}.common_genes.h5ad"; obj[:, common].copy().write_h5ad(output); outputs.append(str(output))
    log = {"inputs": list(map(str, args.inputs)), "case_rule": args.case, "duplicate_rule": "abort", "common_gene_count": len(common), "outputs": outputs}
    (args.output_dir / "gene_alignment.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(json.dumps(log, indent=2))


if __name__ == "__main__": main()
