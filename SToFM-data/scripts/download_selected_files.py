#!/usr/bin/env python3
"""按精确路径或glob选择性下载SToCorpus文件；绝不默认全量下载。"""
from __future__ import annotations

import argparse
import fnmatch
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download

REPO_ID = "Toycat/SToCorpus-88M"
ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pattern", action="append", required=True, help="可重复；如10x/human_brain.h5ad")
    parser.add_argument("--revision", default="6f699f128416e8d55d6ab74976e964caec98b157")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "raw")
    parser.add_argument("--confirm", action="store_true", help="明确确认实际下载；省略时只预览")
    args = parser.parse_args()
    if any(p.strip() in {"", "*", "**", "**/*"} for p in args.pattern):
        parser.error("禁止空模式或全仓通配；请缩小到明确文件/目录模式")

    info = HfApi(token=False).dataset_info(REPO_ID, revision=args.revision, files_metadata=True)
    selected = [f for f in info.siblings if any(fnmatch.fnmatch(f.rfilename, pattern) for pattern in args.pattern)]
    if not selected:
        raise SystemExit("没有匹配文件；先运行list_huggingface_files.py检查真实路径")
    total = sum(f.size or 0 for f in selected)
    print(f"revision={info.sha}\nfiles={len(selected)}\ntotal_bytes={total} ({total / 1e9:.3f} GB)")
    for item in selected:
        print(f"{item.size or 0:>14}\t{item.rfilename}")
    if not args.confirm:
        print("预览结束，未下载。确认体积后追加 --confirm。")
        return

    args.output.mkdir(parents=True, exist_ok=True)
    for item in selected:
        path = hf_hub_download(
            repo_id=REPO_ID, repo_type="dataset", filename=item.rfilename,
            revision=info.sha, local_dir=args.output, token=False,
        )
        print(f"downloaded\t{path}")


if __name__ == "__main__":
    main()
