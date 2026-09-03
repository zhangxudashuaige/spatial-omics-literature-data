#!/usr/bin/env python3
"""检查仓库目录约定、大文件红线和基础CSV一致性。"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_TOP_LEVEL = {"paper-datasets", "scmamba-data", "spagcn-data", "SToFM-data"}
LARGE_LIMIT = 100 * 1024 * 1024
REVIEW_LIMIT = 10 * 1024 * 1024
RAW_PARTS = {"raw", "processed", "external", "downloads", "checkpoints"}
CATALOGS = ("catalog/papers.csv", "catalog/datasets.csv", "catalog/resources.csv")


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    )
    return [ROOT / item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    existing_forbidden = sorted(name for name in FORBIDDEN_TOP_LEVEL if (ROOT / name).exists())
    if existing_forbidden:
        errors.append("顶层存在旧式数据目录: " + ", ".join(existing_forbidden))

    datasets = ROOT / "datasets"
    if not datasets.is_dir():
        errors.append("缺少统一 datasets/ 目录")
    else:
        for module in sorted(path for path in datasets.iterdir() if path.is_dir()):
            if not (module / "README.md").is_file():
                errors.append(f"数据模块缺少 README.md: {module.relative_to(ROOT)}")

    for path in tracked_files():
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        size = path.stat().st_size
        if size >= LARGE_LIMIT:
            errors.append(f"普通Git跟踪了 >=100 MiB 文件: {relative} ({size} bytes)")
        elif size >= REVIEW_LIMIT:
            warnings.append(f"需人工确认的 >=10 MiB 文件: {relative} ({size} bytes)")
        strict_payload_parts = {"raw", "processed", "external", "downloads"}
        if any(part in strict_payload_parts for part in relative.parts) and path.name not in {".gitkeep", "README.md"}:
            errors.append(f"原始/处理后大文件目录中存在Git跟踪文件: {relative}")
        if "checkpoints" in relative.parts and path.name not in {".gitkeep", "README.md"} and path.suffix.lower() != ".json":
            errors.append(f"模型检查点目录中存在非说明性Git跟踪文件: {relative}")

    for relative_name in CATALOGS:
        path = ROOT / relative_name
        if not path.is_file():
            errors.append(f"缺少目录表: {relative_name}")
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        if not rows:
            errors.append(f"空目录表: {relative_name}")
            continue
        widths = {len(row) for row in rows}
        if len(widths) != 1:
            errors.append(f"CSV列数不一致: {relative_name} -> {sorted(widths)}")

    print(f"仓库: {ROOT}")
    print(f"错误: {len(errors)}，警告: {len(warnings)}")
    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings:
        print(f"WARN:  {item}")
    if errors:
        return 1
    print("PASS: 目录、Git大文件红线和基础CSV检查通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
