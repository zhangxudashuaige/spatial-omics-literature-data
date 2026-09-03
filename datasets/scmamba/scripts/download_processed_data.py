#!/usr/bin/env python3
"""按 manifest 下载已确认的 scMamba 处理后文件；默认不下载。"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
from pathlib import Path

import requests
from tqdm import tqdm


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data_manifest.csv"


def rows() -> list[dict[str, str]]:
    with MANIFEST.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download(row: dict[str, str], retries: int = 3) -> dict[str, object]:
    url = row["processed_data_url"]
    if not url.startswith("https://"):
        raise ValueError(f"{row['dataset_name']} 没有已验证的直接下载地址")
    target = ROOT / row["local_path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_suffix(target.suffix + ".part")
    expected = int(row["expected_file_size"]) if row["expected_file_size"].isdigit() else None
    if target.exists() and (expected is None or target.stat().st_size == expected):
        return {"path": str(target), "size": target.stat().st_size, "sha256": sha256(target), "reused": True}
    for attempt in range(1, retries + 1):
        offset = partial.stat().st_size if partial.exists() else 0
        headers = {"Range": f"bytes={offset}-"} if offset else {}
        try:
            with requests.get(url, headers=headers, stream=True, timeout=(30, 180)) as response:
                response.raise_for_status()
                if offset and response.status_code != 206:
                    offset = 0
                    partial.unlink(missing_ok=True)
                total = expected or (offset + int(response.headers.get("content-length", 0)))
                with partial.open("ab" if offset else "wb") as handle, tqdm(
                    total=total, initial=offset, unit="B", unit_scale=True, desc=target.name
                ) as bar:
                    for chunk in response.iter_content(8 * 1024 * 1024):
                        if chunk:
                            handle.write(chunk)
                            bar.update(len(chunk))
            if expected and partial.stat().st_size != expected:
                raise IOError(f"大小不符：{partial.stat().st_size} != {expected}")
            partial.replace(target)
            return {"path": str(target), "size": target.stat().st_size, "sha256": sha256(target), "reused": False}
        except Exception:
            if attempt == retries:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("unreachable")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", help="data_manifest.csv 中的 dataset_name")
    parser.add_argument("--download", action="store_true", help="明确执行下载；否则只列出")
    parser.add_argument("--list", action="store_true", help="列出全部状态")
    args = parser.parse_args()
    entries = rows()
    if args.list or not args.download:
        for row in entries:
            print(f"{row['dataset_name']}: {row['download_status']} -> {row['processed_data_url'] or '(无直接文件)'}")
        if not args.download:
            return
    if not args.dataset:
        parser.error("为避免误下载大文件，--download 必须同时指定 --dataset")
    match = next((row for row in entries if row["dataset_name"] == args.dataset), None)
    if match is None:
        parser.error(f"未知数据集：{args.dataset}")
    result = download(match)
    report = ROOT / "datasets" / args.dataset / "download_status.local.json"
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
