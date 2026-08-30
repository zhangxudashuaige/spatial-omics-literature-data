#!/usr/bin/env python3
"""为本机已下载文件生成大小和 SHA-256 清单。"""
from __future__ import annotations

import argparse
import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(8 << 20): value.update(chunk)
    return value.hexdigest()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=root / "raw")
    parser.add_argument("--output", type=Path, default=root / "raw" / "files_manifest.local.csv")
    args = parser.parse_args()
    rows = [{"path": str(p.relative_to(root)), "size_bytes": p.stat().st_size, "sha256": sha256(p), "checked_at_utc": datetime.now(timezone.utc).isoformat()} for p in sorted(args.data_dir.rglob("*")) if p.is_file() and not p.name.endswith(".part")]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "size_bytes", "sha256", "checked_at_utc"]); writer.writeheader(); writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__": main()

