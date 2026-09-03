#!/usr/bin/env python3
"""从显式固定版本的 CELLxGENE Census 导出一个可审计的小型 H5AD 样例。"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path


def quote_filter_value(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def build_filter(tissue: str | None, cell_type: str | None, primary_only: bool) -> str:
    clauses: list[str] = []
    if primary_only:
        clauses.append("is_primary_data == True")
    if tissue:
        clauses.append(f"tissue == '{quote_filter_value(tissue)}'")
    if cell_type:
        clauses.append(f"cell_type == '{quote_filter_value(cell_type)}'")
    return " and ".join(clauses)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--census-version", required=True, help="固定日期版本，例如 2025-11-08；禁止省略")
    parser.add_argument("--organism", default="Homo sapiens", choices=["Homo sapiens"])
    parser.add_argument("--tissue", help="Census obs 中 tissue 的精确值")
    parser.add_argument("--cell-type", help="Census obs 中 cell_type 的精确值")
    parser.add_argument("--max-cells", type=int, default=100, help="最多导出的细胞数")
    parser.add_argument("--include-non-primary", action="store_true", help="允许重复数据；默认不允许")
    parser.add_argument("--output", type=Path, default=Path("data/tabula/sample/sample.h5ad"))
    args = parser.parse_args()

    if args.max_cells < 1 or args.max_cells > 10_000:
        parser.error("--max-cells 必须在 1 到 10000 之间")
    if args.census_version in {"stable", "latest"}:
        parser.error("必须填写日期版本，不能使用会变化的 stable/latest 别名")

    if platform.system() == "Windows":
        print("错误：CELLxGENE Census 官方 Python API 当前不支持原生 Windows。请在 WSL2、Linux 或容器中运行。", file=sys.stderr)
        return 3

    try:
        import cellxgene_census
    except ImportError:
        print("缺少 cellxgene-census。请在 Python 3.10–3.12 环境运行：pip install cellxgene-census", file=sys.stderr)
        return 2

    value_filter = build_filter(args.tissue, args.cell_type, not args.include_non_primary)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    obs_columns = [
        "soma_joinid",
        "dataset_id",
        "tissue",
        "cell_type",
        "is_primary_data",
    ]
    with cellxgene_census.open_soma(census_version=args.census_version) as census:
        obs = cellxgene_census.get_obs(
            census,
            organism=args.organism,
            value_filter=value_filter or None,
            column_names=obs_columns,
        )
        if obs.empty:
            raise RuntimeError(f"查询没有返回细胞：{value_filter or '<no filter>'}")
        selected = obs.head(args.max_cells).copy()
        soma_joinids = selected["soma_joinid"].astype("int64").to_numpy()
        adata = cellxgene_census.get_anndata(
            census,
            organism=args.organism,
            measurement_name="RNA",
            obs_coords=(soma_joinids,),
            obs_column_names=obs_columns,
        )

    adata.write_h5ad(output, compression="gzip")
    manifest = {
        "source": "CZ CELLxGENE Census",
        "source_url": "https://chanzuckerberg.github.io/cellxgene-census/index.html",
        "census_version": args.census_version,
        "query": {
            "organism": args.organism,
            "tissue": args.tissue,
            "cell_type": args.cell_type,
            "is_primary_data": not args.include_non_primary,
            "value_filter": value_filter,
            "max_cells": args.max_cells,
        },
        "cells": int(adata.n_obs),
        "genes": int(adata.n_vars),
        "dataset_ids": sorted(map(str, adata.obs["dataset_id"].unique().tolist())),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "output_file": output.name,
        "size_bytes": output.stat().st_size,
        "sha256": sha256(output),
        "reproducibility_status": "query_reproducible_not_paper_exact_pretraining_subset",
        "license_note": "Census 中各 source dataset 的许可证可能不同；公开样例前逐项核查 dataset_id 对应条款。",
    }
    manifest_path = output.with_name("sample_manifest.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
