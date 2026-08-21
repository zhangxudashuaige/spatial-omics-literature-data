#!/usr/bin/env python3
"""解析 Zenodo DOI 并下载作者代码的固定 GitHub 标签。"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import requests

DOI = "10.5281/zenodo.10851179"
DATACITE = f"https://api.datacite.org/dois/{DOI}"
EXPECTED_REPO = "https://github.com/JingtaoLab/STO-analysis.git"
EXPECTED_TAG = "STO-analysis"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    project = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=project / "data/external/zenodo_code")
    parser.add_argument("--metadata-only", action="store_true", help="只解析 DOI，不克隆代码")
    args = parser.parse_args()

    response = requests.get(DATACITE, timeout=(20, 120), headers={"User-Agent": "spatial-omics-literature-data/1.0"})
    response.raise_for_status()
    record = response.json()
    attrs = record["data"]["attributes"]
    related = [item.get("relatedIdentifier", "") for item in attrs.get("relatedIdentifiers", [])]
    metadata = {
        "doi": DOI,
        "title": attrs.get("titles", [{}])[0].get("title"),
        "version": attrs.get("version"),
        "rights": attrs.get("rightsList", []),
        "related_identifiers": related,
        "resolved_repository": EXPECTED_REPO,
        "resolved_tag": EXPECTED_TAG,
    }
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    if args.metadata_only:
        return 0
    if shutil.which("git") is None:
        raise RuntimeError("没有找到 git。请安装 Git for Windows。")
    if args.output.exists():
        raise RuntimeError(f"目标已存在：{args.output}。为避免覆盖，请移动或删除后重试。")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--depth", "1", "--branch", EXPECTED_TAG, EXPECTED_REPO, str(args.output)],
        check=True,
    )
    commit = subprocess.check_output(["git", "-C", str(args.output), "rev-parse", "HEAD"], text=True).strip()
    print(f"已克隆标签 {EXPECTED_TAG}，提交 {commit}")
    print("注意：该快照没有 LICENSE 文件；不要未经核实重新分发源码。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
