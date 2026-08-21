#!/usr/bin/env python3
"""列出 HRA005567 官方 HTTPS 目录的真实文件，不下载文件内容。"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from html import unescape
from pathlib import Path
from urllib.parse import urljoin

import requests

ROOT_URL = "https://download.cncb.ac.cn/gsa-human/HRA005567/"
RUN_RE = re.compile(r"HRR\d+/?$")
LINK_RE = re.compile(r'href=["\']([^"\']+)["\']', re.I)
SIZE_RE = re.compile(r"([\d.]+)\s*([KMGT]?B)", re.I)


def request_text(session: requests.Session, url: str, retries: int) -> str:
    error: Exception | None = None
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=(20, 120))
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            error = exc
            time.sleep(2**attempt)
    raise RuntimeError(f"目录请求失败：{url}\n{error}")


def parse_size(line: str) -> int | None:
    # nginx autoindex 通常给精确字节数；兼容带单位的目录页面。
    numbers = re.findall(r"\s(\d{1,15})\s*$", line)
    if numbers:
        return int(numbers[-1])
    match = SIZE_RE.search(line)
    if not match:
        return None
    value, unit = float(match.group(1)), match.group(2).upper()
    factor = {"B": 1, "KB": 1000, "MB": 1000**2, "GB": 1000**3, "TB": 1000**4}[unit]
    return int(value * factor)


def list_run(session: requests.Session, run_url: str, retries: int) -> list[dict[str, object]]:
    html = request_text(session, run_url, retries)
    run = run_url.rstrip("/").rsplit("/", 1)[-1]
    rows: list[dict[str, object]] = []
    for line in html.splitlines():
        links = LINK_RE.findall(line)
        if not links:
            continue
        href = unescape(links[0])
        if href.startswith("?") or href in {"../", "./"} or href.endswith("/"):
            continue
        name = href.rsplit("/", 1)[-1]
        if not (name.endswith(".fq.gz") or name.endswith("_sta.xml")):
            continue
        rows.append(
            {
                "source_id": "HRA005567",
                "run_accession": run,
                "file_name": name,
                "file_type": "FASTQ" if name.endswith(".fq.gz") else "XML",
                "data_level": "raw" if name.endswith(".fq.gz") else "run_statistics",
                "size_bytes": parse_size(line) or "",
                "download_url": urljoin(run_url, href),
                "is_raw": "yes" if name.endswith(".fq.gz") else "no",
                "is_processed": "no",
                "download_status": "not_downloaded",
                "sha256": "",
                "git_tracking": "ignored",
            }
        )
    return rows


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root-url", default=ROOT_URL)
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "metadata/files_manifest.csv",
    )
    args = parser.parse_args()

    session = requests.Session()
    session.headers.update({"User-Agent": "spatial-omics-literature-data/1.0 (directory inventory)"})
    run_metadata_url = "https://ngdc.cncb.ac.cn/gsa-human/ajaxb/runinstudy?accession=HRA005567&pageNo=1&pageSize=500&totalCount=0"
    run_metadata = json.loads(request_text(session, run_metadata_url, args.retries))
    run_map = {
        (item.get("runAcc", ""), item.get("runFileName", "")): item
        for item in run_metadata.get("runViews", [])
    }
    root_html = request_text(session, args.root_url, args.retries)
    run_urls = sorted(
        {
            urljoin(args.root_url, href)
            for href in LINK_RE.findall(root_html)
            if RUN_RE.search(href.rstrip("/") + "/")
        }
    )
    if not run_urls:
        raise RuntimeError("没有在官方目录中找到 HRR run 子目录；页面结构可能已改变。")

    rows: list[dict[str, object]] = []
    for index, run_url in enumerate(run_urls, 1):
        rows.extend(list_run(session, run_url, args.retries))
        if index % 20 == 0 or index == len(run_urls):
            print(f"已检查 {index}/{len(run_urls)} 个 run")

    for row in rows:
        meta = run_map.get((str(row["run_accession"]), str(row["file_name"])), {})
        row.update(
            {
                "experiment_accession": meta.get("expName", ""),
                "experiment_title": meta.get("expTitle", ""),
                "run_title": meta.get("runTitle", ""),
                "local_path": f"data/{'raw' if row['file_type'] == 'FASTQ' else 'external'}/HRA005567/{row['run_accession']}/{row['file_name']}",
                "notes": "官方HTTPS目录；未下载" if row["file_type"] == "FASTQ" else "官方run统计；未提交附件",
            }
        )

    # 重新盘点 HRA 时保留已经记录的 Cell 补充表和作者代码行。
    preserved: list[dict[str, object]] = []
    if args.output.exists():
        with args.output.open(encoding="utf-8-sig", newline="") as handle:
            preserved = [row for row in csv.DictReader(handle) if row.get("source_id") != "HRA005567"]
    rows.extend(preserved)

    fields = [
        "source_id", "run_accession", "experiment_accession", "experiment_title", "run_title",
        "file_name", "file_type", "data_level", "size_bytes", "download_url", "is_raw",
        "is_processed", "local_path", "download_status", "sha256", "git_tracking", "notes",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    hra_rows = [row for row in rows if row.get("source_id") == "HRA005567"]
    total = sum(int(row["size_bytes"]) for row in hra_rows if row["size_bytes"] != "")
    print(f"HRA文件：{len(hra_rows):,}；合计：{total:,} bytes = {total / 10**12:.3f} TB = {total / 2**40:.3f} TiB")
    print(f"清单：{args.output}")
    print("本程序没有下载 FASTQ 文件内容。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
