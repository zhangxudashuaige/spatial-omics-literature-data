#!/usr/bin/env python3
"""根据数据清单评估并下载已确认公开的 MOSTA3D 文件。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


PAPER_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MANIFEST = PAPER_DIR / "metadata" / "data_manifest.csv"
CHUNK_SIZE = 8 * 1024 * 1024
USER_AGENT = "spatial-omics-literature-data/1.0"


def human_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            return f"{value:.2f} {unit}"
        value /= 1024
    raise AssertionError("不会执行到这里")


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def select_rows(rows: list[dict[str, str]], stage: str | None, category: str | None) -> list[dict[str, str]]:
    selected = []
    for row in rows:
        if stage and row["stage"] not in {stage, "both"}:
            continue
        if category and row["category"] != category:
            continue
        selected.append(row)
    return selected


def is_downloadable(row: dict[str, str]) -> bool:
    return row["availability_status"] == "public" and bool(row["download_url"].strip())


def secure_destination(root: Path, local_path: str) -> Path:
    if local_path.endswith(("/", "\\")):
        raise ValueError("可下载条目必须写具体文件路径，不能只写目录")
    resolved_root = root.resolve()
    destination = (resolved_root / local_path).resolve()
    if not destination.is_relative_to(resolved_root):
        raise ValueError(f"local_path 越出总仓库：{local_path}")
    return destination


def download_one(row: dict[str, str], root: Path, overwrite: bool) -> dict[str, object]:
    destination = secure_destination(root, row["local_path"])
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not overwrite:
        return {"item_id": row["item_id"], "status": "skipped_exists", "path": str(destination)}

    temporary = destination.with_name(destination.name + ".part")
    digest = hashlib.sha256()
    received = 0
    request = Request(row["download_url"], headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=120) as response, temporary.open("wb") as handle:
        while chunk := response.read(CHUNK_SIZE):
            handle.write(chunk)
            digest.update(chunk)
            received += len(chunk)

    expected_size = int(row["size_bytes"]) if row["size_bytes"].strip() else None
    expected_sha = row["sha256"].strip().lower() or None
    actual_sha = digest.hexdigest()
    if expected_size is not None and received != expected_size:
        temporary.unlink(missing_ok=True)
        raise ValueError(f"{row['item_id']} 大小不符：{received} != {expected_size}")
    if expected_sha is not None and actual_sha != expected_sha:
        temporary.unlink(missing_ok=True)
        raise ValueError(f"{row['item_id']} SHA-256 不符")
    temporary.replace(destination)
    return {
        "item_id": row["item_id"],
        "status": "downloaded",
        "path": str(destination),
        "size_bytes": received,
        "sha256": actual_sha,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--stage", choices=("E9.5", "E11.5"))
    parser.add_argument("--category")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="只评估，不下载（默认）")
    mode.add_argument("--download", action="store_true", help="下载清单中状态为 public 的文件")
    parser.add_argument("--accept-large-files", action="store_true", help="确认已准备足够磁盘空间")
    parser.add_argument("--allow-unknown-size", action="store_true", help="允许下载大小未知的文件")
    parser.add_argument("--max-gb", type=float, default=20.0, help="已知下载总量上限，默认20 GiB")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    rows = select_rows(load_rows(args.manifest), args.stage, args.category)
    downloadable = [row for row in rows if is_downloadable(row)]
    known_size = sum(int(row["size_bytes"]) for row in downloadable if row["size_bytes"].strip())
    unknown_size = sum(1 for row in downloadable if not row["size_bytes"].strip())

    print(f"选中条目：{len(rows)}")
    print(f"当前可下载的文件级条目：{len(downloadable)}")
    print(f"已知总大小：{human_size(known_size)}")
    print(f"大小未知的可下载条目：{unknown_size}")
    for row in rows:
        print(f"- {row['item_id']}：{row['availability_status']} -> {row['local_path']}")

    if not args.download:
        print("\n当前为下载预演；没有下载任何文件。")
        return 0
    if not args.accept_large_files:
        parser.error("真实下载必须同时指定 --accept-large-files")
    if unknown_size and not args.allow_unknown_size:
        parser.error("存在大小未知的可下载文件；请先核实大小")
    if known_size > int(args.max_gb * 1024**3):
        parser.error(f"已知总量 {human_size(known_size)} 超过 --max-gb {args.max_gb:g} GiB")
    if not downloadable:
        print("没有状态为 public 且带直接下载地址的条目；没有下载任何文件。")
        return 0

    report = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "manifest": str(args.manifest),
        "results": [],
    }
    try:
        for row in downloadable:
            result = download_one(row, args.output_root, args.overwrite)
            report["results"].append(result)
            print(f"{result['status']}：{result['item_id']}")
    finally:
        report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        report_path = PAPER_DIR / "metadata" / "download_report.local.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"下载报告：{report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
