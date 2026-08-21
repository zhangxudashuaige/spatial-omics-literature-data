#!/usr/bin/env python3
"""按文件名或 run 从清单选择下载；默认只预览，必须加 --download 才执行。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
import time
from pathlib import Path

import requests
from tqdm import tqdm


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download(session: requests.Session, url: str, target: Path, expected: int | None, retries: int) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    part = target.with_suffix(target.suffix + ".part")
    for attempt in range(retries):
        start = part.stat().st_size if part.exists() else 0
        headers = {"Range": f"bytes={start}-"} if start else {}
        try:
            with session.get(url, headers=headers, stream=True, timeout=(30, 180)) as response:
                if start and response.status_code == 200:
                    start = 0
                    mode = "wb"
                else:
                    response.raise_for_status()
                    mode = "ab" if start else "wb"
                total = expected or int(response.headers.get("Content-Length", 0)) + start or None
                with part.open(mode) as handle, tqdm(
                    total=total, initial=start, unit="B", unit_scale=True, desc=target.name
                ) as bar:
                    for chunk in response.iter_content(8 * 1024 * 1024):
                        if chunk:
                            handle.write(chunk)
                            bar.update(len(chunk))
            if expected is not None and part.stat().st_size != expected:
                raise IOError(f"大小不符：期望 {expected}，实际 {part.stat().st_size}")
            part.replace(target)
            return
        except (requests.RequestException, OSError) as exc:
            if attempt + 1 == retries:
                raise RuntimeError(f"下载失败：{url}\n{exc}") from exc
            time.sleep(2**attempt)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    project = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=project / "metadata/files_manifest.csv")
    parser.add_argument("--file", action="append", default=[], help="精确文件名；可重复")
    parser.add_argument("--run", action="append", default=[], help="HRR run accession；可重复")
    parser.add_argument("--output-dir", type=Path, default=project / "data/raw/HRA005567")
    parser.add_argument("--download", action="store_true", help="真正执行下载；缺省只预览")
    parser.add_argument("--retries", type=int, default=4)
    args = parser.parse_args()

    if not args.file and not args.run:
        parser.error("必须明确给出至少一个 --file 或 --run；本脚本不提供默认全量下载。")

    with args.manifest.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    selected = [
        row for row in rows
        if row.get("file_name") in set(args.file) or row.get("run_accession") in set(args.run)
    ]
    if not selected:
        raise SystemExit("清单中没有匹配文件。请使用精确文件名或 HRR accession。")

    total = sum(int(row["size_bytes"]) for row in selected if row.get("size_bytes", "").isdigit())
    print(f"已选择 {len(selected)} 个文件，合计 {total:,} bytes ({total / 2**30:.2f} GiB)：")
    for row in selected:
        print(f"  {row['run_accession']}/{row['file_name']}  {row.get('size_bytes', '未知')} bytes")
    if not args.download:
        print("当前为预览模式；确认后加 --download。")
        return 0

    session = requests.Session()
    session.headers.update({"User-Agent": "spatial-omics-literature-data/1.0"})
    checksum_rows: list[tuple[str, str, int]] = []
    for row in selected:
        if row.get("source_id") == "HRA005567":
            target = args.output_dir / row["run_accession"] / row["file_name"]
            if row.get("file_type") == "XML":
                target = project / row["local_path"]
        elif row.get("local_path"):
            target = project / row["local_path"]
        else:
            target = args.output_dir / row["file_name"]
        expected = int(row["size_bytes"]) if row.get("size_bytes", "").isdigit() else None
        download(session, row["download_url"], target, expected, args.retries)
        digest = sha256(target)
        checksum_rows.append((str(target), digest, target.stat().st_size))
        print(f"SHA256 {digest}  {target}")

    print("下载完成。文件位于被 Git 忽略的 data/ 目录。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
