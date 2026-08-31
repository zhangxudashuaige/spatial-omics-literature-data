#!/usr/bin/env python3
"""通过HfApi生成SToCorpus-88M真实文件清单；不下载数据。"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from huggingface_hub import HfApi

REPO_ID = "Toycat/SToCorpus-88M"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "manifests" / "huggingface_files.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-id", default=REPO_ID)
    parser.add_argument("--revision", default="main")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--use-token", action="store_true", help="使用本机HF token；公开仓默认匿名，避免错误/过期token")
    args = parser.parse_args()

    api = HfApi(token=None if args.use_token else False)
    info = api.dataset_info(args.repo_id, revision=args.revision, files_metadata=True)
    rows = []
    for item in info.siblings:
        lfs = item.lfs
        rows.append({
            "repository": args.repo_id,
            "revision": info.sha,
            "path": item.rfilename,
            "size_bytes": item.size or 0,
            "lfs_sha256": getattr(lfs, "sha256", "") if lfs else "",
            "download_url": f"https://huggingface.co/datasets/{args.repo_id}/resolve/{info.sha}/{item.rfilename}",
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    total = sum(int(row["size_bytes"]) for row in rows)
    print(f"revision={info.sha}")
    print(f"files={len(rows)}")
    print(f"total_bytes={total} ({total / 1e9:.2f} GB)")
    print(f"manifest={args.output}")


if __name__ == "__main__":
    main()
