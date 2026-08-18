#!/usr/bin/env python3
"""检查 CNP0005981、MOSTA3D 和外部单细胞参考入口。"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PAPER_DIR = Path(__file__).resolve().parents[1]
CNGB_API = "https://db.cngb.org/cnsa/ajax/project/public_view/?q=CNP0005981"
CNGB_PROJECT = "https://db.cngb.org/data_resources/project/CNP0005981/"
MOSTA3D = "https://db.cngb.org/stomics/mosta/3d/"
GEO_REFERENCE = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE228590"
USER_AGENT = "spatial-omics-literature-data/1.0"


def fetch_json(url: str, timeout: float) -> tuple[int | None, dict[str, Any] | None, str | None]:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return response.status, payload, None
    except HTTPError as exc:
        return exc.code, None, f"HTTP {exc.code}"
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        return None, None, str(exc)


def fetch_http_status(url: str, timeout: float) -> tuple[int | None, str | None, str | None]:
    request = Request(url, headers={"User-Agent": USER_AGENT}, method="GET")
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status, response.geturl(), None
    except HTTPError as exc:
        return exc.code, exc.geturl(), f"HTTP {exc.code}"
    except (URLError, TimeoutError) as exc:
        return None, None, str(exc)


def check(timeout: float) -> dict[str, Any]:
    cngb_http, cngb_payload, cngb_error = fetch_json(CNGB_API, timeout)
    if cngb_payload and cngb_payload.get("code") == 0:
        summary = cngb_payload.get("data", {}).get("summary_data", {})
        cngb_status = "public" if summary.get("select_control") == "Public" else "record_found_not_public"
    elif cngb_payload:
        cngb_status = "not_publicly_retrievable"
    else:
        cngb_status = "check_failed"

    mosta_http, mosta_final_url, mosta_error = fetch_http_status(MOSTA3D, timeout)
    if mosta_http == 200:
        mosta_status = "public_page_reachable"
    elif mosta_http == 404:
        mosta_status = "not_found"
    else:
        mosta_status = "check_failed"

    geo_http, geo_final_url, geo_error = fetch_http_status(GEO_REFERENCE, timeout)
    geo_status = "public_reference_only" if geo_http == 200 else "check_failed"

    return {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "cnsa": {
            "accession": "CNP0005981",
            "project_url": CNGB_PROJECT,
            "public_api_url": CNGB_API,
            "http_status": cngb_http,
            "response": cngb_payload,
            "error": cngb_error,
            "status": cngb_status,
        },
        "mosta3d": {
            "url": MOSTA3D,
            "http_status": mosta_http,
            "final_url": mosta_final_url,
            "error": mosta_error,
            "status": mosta_status,
        },
        "external_scrna_reference": {
            "accession": "GSE228590",
            "url": GEO_REFERENCE,
            "http_status": geo_http,
            "final_url": geo_final_url,
            "error": geo_error,
            "status": geo_status,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=30.0, help="每个请求的超时秒数")
    parser.add_argument(
        "--write",
        nargs="?",
        const=str(PAPER_DIR / "metadata" / "availability_status.local.json"),
        help="把本次结果写入本地 JSON 报告",
    )
    parser.add_argument("--strict", action="store_true", help="任一论文主入口不可用时返回非零退出码")
    args = parser.parse_args()

    result = check(args.timeout)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    print(rendered)
    if args.write:
        output = Path(args.write)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
        print(f"\n已写入：{output}")

    if args.strict:
        ok = result["cnsa"]["status"] == "public" and result["mosta3d"]["status"] == "public_page_reachable"
        return 0 if ok else 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
