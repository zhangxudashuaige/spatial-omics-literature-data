"""校验本地文件大小和 SHA256；官方未公布校验值时只生成本地基线。"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests" / "files.csv"
OUTPUT = ROOT / "results" / "tables" / "local_file_inventory.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    with MANIFEST.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    inventory: list[dict[str, str | int]] = []
    failed = 0
    for row in rows:
        path = ROOT / row["local_path"]
        if not path.is_file():
            continue
        actual_sha = sha256(path)
        expected_sha = row["sha256"].strip().lower()
        status = "ok"
        if expected_sha and actual_sha != expected_sha:
            status = "sha256_mismatch"
            failed += 1
        inventory.append({
            "file_id": row["file_id"],
            "local_path": row["local_path"],
            "size_bytes": path.stat().st_size,
            "sha256": actual_sha,
            "expected_sha256": expected_sha,
            "status": status,
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["file_id", "local_path", "size_bytes", "sha256", "expected_sha256", "status"]
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(inventory)
    print(f"已检查 {len(inventory)} 个本地文件；结果：{OUTPUT}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
