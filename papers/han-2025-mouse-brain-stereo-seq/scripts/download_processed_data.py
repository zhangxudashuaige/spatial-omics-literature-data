"""依据 manifests/files.csv 下载有明确官方直链的处理后文件。"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from urllib.parse import urlparse

import requests
from tqdm import tqdm


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests" / "files.csv"


def safe_target(relative_path: str) -> Path:
    target = (ROOT / relative_path).resolve()
    if ROOT.resolve() not in target.parents:
        raise ValueError(f"本地路径越界：{relative_path}")
    return target


def download(url: str, target: Path, timeout: int) -> None:
    if urlparse(url).scheme != "https":
        raise ValueError(f"仅允许 HTTPS：{url}")
    target.parent.mkdir(parents=True, exist_ok=True)
    part = target.with_suffix(target.suffix + ".part")
    with requests.get(url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        total = int(response.headers.get("content-length", 0))
        with part.open("wb") as handle, tqdm(total=total, unit="B", unit_scale=True) as bar:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)
                    bar.update(len(chunk))
    part.replace(target)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="只列出可下载项（默认）")
    mode.add_argument("--download", action="store_true", help="真正下载 direct_download=yes 的条目")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    with MANIFEST.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    candidates = [
        row
        for row in rows
        if row["direct_download"].lower() == "yes"
        and row["download_url"].startswith("https://")
        and row["commit_to_github"].lower() == "no"
        and row["local_path"].startswith("data/processed/")
    ]
    print(f"清单条目：{len(rows)}；有明确直链的非 GitHub 数据：{len(candidates)}")

    for row in candidates:
        target = safe_target(row["local_path"])
        print(f"- {row['file_id']}: {row['download_url']} -> {target}")
        if not args.download:
            continue
        if target.exists() and not args.overwrite:
            print("  已存在，跳过；使用 --overwrite 可覆盖。")
            continue
        download(row["download_url"], target, args.timeout)
        print("  下载完成。")

    if not args.download:
        print("当前为预览模式；确认磁盘空间后添加 --download。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
