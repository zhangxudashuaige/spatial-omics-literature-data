#!/usr/bin/env python3
"""验证 checksums.md5 中本机存在的文件。"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(); parser.add_argument("--require-all", action="store_true"); args = parser.parse_args()
    failed = False
    for line in (root / "checksums.md5").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"): continue
        wanted, relative = line.split(maxsplit=1); path = root / relative.strip()
        if not path.exists():
            print(f"{'FAIL' if args.require_all else 'SKIP'} {relative}: absent"); failed |= args.require_all; continue
        value = hashlib.md5()  # nosec B303 - integrity checksum
        with path.open("rb") as handle:
            while chunk := handle.read(8 << 20): value.update(chunk)
        ok = value.hexdigest() == wanted; print(f"{'OK' if ok else 'FAIL'} {relative}"); failed |= not ok
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__": main()

