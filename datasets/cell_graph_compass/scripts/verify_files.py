#!/usr/bin/env python3
"""核对 Zenodo 文件大小和 MD5。"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

EXPECTED = {
    "Readme.txt": (2290, "009088913f5ff881b41c5331da28d1f4"),
    "scData.zip": (2642248462, "0718023070988d51519ab4f3e740ebfd"),
}


def digest(path: Path) -> str:
    value = hashlib.md5()  # nosec B303 - upstream integrity checksum
    with path.open("rb") as handle:
        while chunk := handle.read(8 << 20):
            value.update(chunk)
    return value.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, default=Path(__file__).resolve().parents[1] / "raw")
    parser.add_argument("--require-large", action="store_true")
    args = parser.parse_args()
    failed = False
    for name, (size, wanted) in EXPECTED.items():
        path = args.raw_dir / name
        if not path.exists():
            required = name != "scData.zip" or args.require_large
            print(f"{'FAIL' if required else 'SKIP'} {name}: not present")
            failed |= required
            continue
        actual = digest(path)
        ok = path.stat().st_size == size and actual.lower() == wanted
        print(f"{'OK' if ok else 'FAIL'} {name}: size={path.stat().st_size}, md5={actual}")
        failed |= not ok
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()

