#!/usr/bin/env python3
"""检查项目CSV中的HTTP/HTTPS链接，不下载大型数据。"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import datetime as dt
from pathlib import Path
import ssl
import urllib.error
import urllib.request
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
METADATA = ROOT / "metadata"
DEFAULT_OUTPUT = ROOT / "results" / "url_check.csv"
URL_FIELDS = {
    "official_url", "download_url", "model_paper_url", "original_paper_url",
    "paper_url", "weights_url", "documentation_url", "official_repository",
    "platform_paper_url",
}


def collect_urls() -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    seen: set[str] = set()
    for csv_path in sorted(METADATA.glob("*.csv")):
        with csv_path.open(encoding="utf-8", newline="") as handle:
            for row_number, row in enumerate(csv.DictReader(handle), start=2):
                for field, value in row.items():
                    url = (value or "").strip()
                    if field not in URL_FIELDS or not url.startswith(("http://", "https://")):
                        continue
                    if url in seen:
                        continue
                    seen.add(url)
                    records.append({
                        "source_file": csv_path.name,
                        "row_number": str(row_number),
                        "field": field,
                        "url": url,
                    })
    return records


def classify(status_code: int | None, error: str) -> str:
    if error:
        return "network_error"
    if status_code in (401, 403):
        return "access_restricted"
    if status_code is not None and 200 <= status_code < 400:
        return "ok"
    if status_code in (404, 410):
        return "not_found"
    return "http_error"


def check(url: str, timeout: float) -> dict[str, str]:
    headers = {"User-Agent": "single-cell-foundation-model-resources/1.0 link-checker"}
    status_code: int | None = None
    final_url = ""
    error = ""
    try:
        request = urllib.request.Request(url, headers=headers, method="HEAD")
        try:
            response = urllib.request.urlopen(request, timeout=timeout, context=ssl.create_default_context())
        except urllib.error.HTTPError as exc:
            if exc.code in (405, 429) or exc.code >= 500:
                request = urllib.request.Request(url, headers={**headers, "Range": "bytes=0-1023"}, method="GET")
                response = urllib.request.urlopen(request, timeout=timeout, context=ssl.create_default_context())
            else:
                raise
        with response:
            status_code = response.status
            final_url = response.geturl()
    except urllib.error.HTTPError as exc:
        status_code = exc.code
        final_url = exc.geturl()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        error = f"{type(exc).__name__}: {exc}"
    return {
        "status_code": "" if status_code is None else str(status_code),
        "status": classify(status_code, error),
        "final_url": final_url,
        "host": urlparse(url).netloc,
        "error": error,
        "checked_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--limit", type=int, default=0, help="仅检查前N个唯一URL；0表示全部")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    records = collect_urls()
    if args.limit:
        records = records[: args.limit]
    with ThreadPoolExecutor(max_workers=min(12, max(1, len(records)))) as pool:
        checked = pool.map(lambda record: check(record["url"], args.timeout), records)
        output_rows = [{**record, **result} for record, result in zip(records, checked)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = ["source_file", "row_number", "field", "url", "status_code", "status", "final_url", "host", "error", "checked_at"]
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output_rows)
    counts: dict[str, int] = {}
    for row in output_rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    print(f"检查 {len(output_rows)} 个唯一URL；结果：{counts}；输出：{args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
