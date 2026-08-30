#!/usr/bin/env python3
"""验证 checksums.md5 中列出的精确文件。"""
from __future__ import annotations

import hashlib
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]; failed = False
    for line in (root / "checksums.md5").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"): continue
        wanted, rel = line.split(maxsplit=1); path = root / rel.strip()
        if not path.exists(): print(f"MISSING {rel}"); failed = True; continue
        value = hashlib.md5()  # nosec B303 - source integrity checksum
        with path.open("rb") as h:
            while chunk := h.read(8 << 20): value.update(chunk)
        ok = value.hexdigest() == wanted; print(f"{'OK' if ok else 'FAIL'} {rel}"); failed |= not ok
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__": main()

