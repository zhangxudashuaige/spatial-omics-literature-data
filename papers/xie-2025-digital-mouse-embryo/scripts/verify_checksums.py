"""计算本地文件 SHA256，并与 metadata/file_checksums.csv 比较。"""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("metadata/file_checksums.csv"))
    args = parser.parse_args()
    failures = 0
    with args.manifest.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        path = Path(row["local_path"])
        if not path.exists():
            print(f"MISSING  {path}")
            continue
        actual = digest(path)
        expected = row.get("sha256", "").strip()
        status = "OK" if expected and actual == expected else "COMPUTED"
        if expected and actual != expected:
            status = "MISMATCH"
            failures += 1
        print(f"{status:8} {actual}  {path}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
