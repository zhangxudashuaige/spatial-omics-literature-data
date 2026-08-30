#!/usr/bin/env python3
"""轻量读取 Matrix Market 头部；仅显式 --full-stats 时加载矩阵。"""
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path


def header(path: Path) -> dict[str, object]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as handle:
        banner = handle.readline().strip()
        for line in handle:
            if not line.startswith("%"):
                rows, columns, entries = map(int, line.split())
                return {"banner": banner, "shape": [rows, columns], "stored_entries": entries}
    raise ValueError("没有找到 Matrix Market 维度行")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--full-stats", action="store_true")
    args = parser.parse_args()
    report = header(args.path)
    if args.full_stats:
        from scipy.io import mmread
        matrix = mmread(args.path)
        report.update({"loaded_type": type(matrix).__name__, "dtype": str(matrix.dtype), "nnz": int(getattr(matrix, "nnz", 0))})
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
