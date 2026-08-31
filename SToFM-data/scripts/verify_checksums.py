#!/usr/bin/env python3
"""核验downloaded_files.csv中已记录的本地SHA256和大小。"""
from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    failures = 0
    with args.manifest.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            path = Path(row["local_path"])
            ok = path.exists() and path.stat().st_size == int(row["size_bytes"]) and digest(path).lower() == row["sha256"].lower()
            print(("OK" if ok else "FAIL"), path)
            failures += not ok
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
