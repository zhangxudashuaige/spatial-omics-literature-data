#!/usr/bin/env python3
"""按 YAML manifest 核验本地存在文件的大小和 SHA256。"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError as exc:  # pragma: no cover - 清晰的运行时提示
    raise SystemExit("缺少 PyYAML：pip install PyYAML") from exc


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def walk_records(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        if "local_path" in value:
            yield value
        for child in value.values():
            yield from walk_records(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_records(child)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    project_root = Path(__file__).resolve().parents[1]
    parser.add_argument(
        "manifests",
        nargs="*",
        type=Path,
        default=[
            project_root / "manifests/graphsage.yaml",
            project_root / "manifests/tabula.yaml",
            project_root / "manifests/heist.yaml",
        ],
    )
    parser.add_argument("--strict-missing", action="store_true", help="本地缺失也返回失败")
    args = parser.parse_args()

    failures = 0
    checked = 0
    missing = 0
    for manifest_path in args.manifests:
        manifest_path = manifest_path.resolve()
        document = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        print(f"[{manifest_path.name}]")
        for record in walk_records(document):
            local_path_value = record.get("local_path")
            if local_path_value is None:
                continue
            raw_local_path = str(local_path_value).strip()
            if not raw_local_path:
                continue
            candidate = Path(raw_local_path)
            file_path = candidate if candidate.is_absolute() else project_root / candidate
            if not file_path.exists():
                print(f"MISSING  {raw_local_path}")
                missing += 1
                continue
            if not file_path.is_file():
                continue
            checked += 1
            expected_size = record.get("size_bytes")
            expected_hash = str(record.get("sha256") or "").lower()
            actual_size = file_path.stat().st_size
            actual_hash = sha256(file_path)
            size_ok = expected_size in (None, "", "unknown") or int(expected_size) == actual_size
            hash_ok = not expected_hash or expected_hash == actual_hash
            status = "OK" if size_ok and hash_ok else "FAIL"
            print(f"{status:7} {raw_local_path} bytes={actual_size} sha256={actual_hash}")
            if status == "FAIL":
                failures += 1

    print(f"汇总：checked={checked}, missing={missing}, failures={failures}")
    if failures or (args.strict_missing and missing):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
