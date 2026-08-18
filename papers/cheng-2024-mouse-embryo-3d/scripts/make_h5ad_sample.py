#!/usr/bin/env python3
"""从真实 H5AD 随机抽取细胞，生成可测试的小型样本。"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path


PAPER_DIR = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="真实来源 H5AD")
    parser.add_argument("--cells", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--stage", choices=("E9.5", "E11.5"), required=True)
    parser.add_argument("--output", type=Path, default=PAPER_DIR / "sample_data" / "sample_1000_cells.h5ad")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if args.cells <= 0:
        parser.error("--cells 必须为正整数")
    if not args.input.is_file():
        parser.error(f"找不到输入文件：{args.input}")
    if args.output.exists() and not args.overwrite:
        parser.error(f"输出已存在：{args.output}；如需覆盖请加 --overwrite")

    try:
        import anndata as ad
        import numpy as np
    except ImportError as exc:
        parser.error(f"缺少分析依赖：{exc}；请安装 anndata 和 numpy")

    backed = ad.read_h5ad(args.input, backed="r")
    count = min(args.cells, backed.n_obs)
    rng = np.random.default_rng(args.seed)
    indices = np.sort(rng.choice(backed.n_obs, size=count, replace=False))
    sample = backed[indices].to_memory()
    if getattr(backed, "file", None) is not None:
        backed.file.close()

    sample.uns["sample_provenance"] = {
        "source_file": str(args.input.resolve()),
        "stage": args.stage,
        "requested_cells": args.cells,
        "sampled_cells": count,
        "random_seed": args.seed,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_accession": "CNP0005981",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sample.write_h5ad(args.output, compression="gzip")
    size_mb = args.output.stat().st_size / 1024**2
    print(f"已写入 {args.output}：{sample.n_obs} 个细胞 × {sample.n_vars} 个基因，{size_mb:.2f} MiB")
    if size_mb >= 95:
        print("警告：样本接近 GitHub 100 MB 单文件限制，请减少 --cells。", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
