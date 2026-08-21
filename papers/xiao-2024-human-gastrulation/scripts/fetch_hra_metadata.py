#!/usr/bin/env python3
"""下载 HRA005567 的小型元数据；不会下载 FASTQ。"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from urllib.parse import quote

import requests

BASE = "https://ngdc.cncb.ac.cn"
ACCESSION = "HRA005567"


def get_with_retry(session: requests.Session, url: str, retries: int = 4) -> requests.Response:
    error: Exception | None = None
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=(20, 120))
            response.raise_for_status()
            return response
        except (requests.RequestException, OSError) as exc:
            error = exc
            time.sleep(2**attempt)
    raise RuntimeError(f"请求失败：{url}\n{error}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data/external/HRA005567/metadata",
    )
    parser.add_argument("--skip-xlsx", action="store_true", help="不尝试获取官方 Excel 元数据")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": "spatial-omics-literature-data/1.0 (metadata only)"})

    endpoints = {
        "project_page.html": f"{BASE}/gsa-human/browse/{ACCESSION}",
        "runs.json": f"{BASE}/gsa-human/ajaxb/runinstudy?accession={ACCESSION}&pageNo=1&pageSize=500&totalCount=0",
        "individuals.json": f"{BASE}/gsa-human/ajaxb/indinstudy?accession={ACCESSION}&pageNo=1&pageSize=500&totalCount=0",
    }
    for name, url in endpoints.items():
        response = get_with_retry(session, url)
        target = args.output_dir / name
        if name.endswith(".json"):
            target.write_text(json.dumps(response.json(), ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            target.write_bytes(response.content)
        print(f"已保存 {target} ({target.stat().st_size:,} bytes)")

    if not args.skip_xlsx:
        file_name = "/data/gsa-Human/webApp/gsa-human/batchExcel/human/HRA005567/HRA005567.xlsx"
        url = f"{BASE}/gsa-human/file/exportExcelFile?fileName={quote(file_name, safe='')}&accession={ACCESSION}"
        try:
            response = get_with_retry(session, url)
            target = args.output_dir / "HRA005567.xlsx"
            target.write_bytes(response.content)
            print(f"已保存 {target} ({target.stat().st_size:,} bytes)")
        except RuntimeError as exc:
            print(f"警告：官方 Excel 接口暂时不可用；JSON 元数据已保存。\n{exc}")

    print("完成：没有下载任何 FASTQ。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
