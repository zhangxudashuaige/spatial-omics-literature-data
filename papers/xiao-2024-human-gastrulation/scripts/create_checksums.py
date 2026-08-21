#!/usr/bin/env python3
"""为显式指定的本地文件计算 SHA-256；不会扫描未指定的大目录。"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path, help="一个或多个文件；不接受目录")
    parser.add_argument("--json", type=Path, help="可选的 JSON 输出路径")
    args = parser.parse_args()
    rows = []
    for path in args.files:
        if not path.is_file():
            raise SystemExit(f"不是文件或不存在：{path}")
        row = {
            "path": str(path.resolve()),
            "size_bytes": path.stat().st_size,
            "sha256": digest(path),
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }
        rows.append(row)
        print(f"{row['sha256']}  {path}")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
