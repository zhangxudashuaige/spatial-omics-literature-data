#!/usr/bin/env python3
"""安全列出或解压 scData.zip，拒绝目录穿越。"""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    root = Path(__file__).resolve().parents[1]
    parser.add_argument("--archive", type=Path, default=root / "raw" / "scData.zip")
    parser.add_argument("--output", type=Path, default=root / "raw" / "scData")
    parser.add_argument("--list-only", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    with zipfile.ZipFile(args.archive) as archive:
        total = sum(info.file_size for info in archive.infolist())
        print(f"members={len(archive.infolist())}, uncompressed_bytes={total:,}")
        for info in archive.infolist():
            print(f"{info.file_size:>12}  {info.filename}")
            destination = (output / info.filename).resolve()
            if output != destination and output not in destination.parents:
                raise SystemExit(f"unsafe member path: {info.filename}")
        if not args.list_only:
            output.mkdir(parents=True, exist_ok=True)
            archive.extractall(output)


if __name__ == "__main__":
    main()

