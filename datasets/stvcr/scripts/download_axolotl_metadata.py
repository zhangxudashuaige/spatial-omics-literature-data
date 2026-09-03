#!/usr/bin/env python3
"""保存 CNGB/ARTISTA 公开页面元数据；不绕过登录或动态下载权限。"""
from __future__ import annotations

import argparse
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URLS = {
    "raw_project": "https://db.cngb.org/search/project/CNP0002068/",
    "processed_portal": "https://db.cngb.org/stomics/artista/",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "raw" / "axolotl_brain")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = {"accession": "CNP0002068", "checked_at_utc": datetime.now(timezone.utc).isoformat(), "pages": {}}
    for name, url in URLS.items():
        req = urllib.request.Request(url, headers={"User-Agent": "paper-data-catalog/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                body = response.read()
                (args.output_dir / f"{name}.html").write_bytes(body)
                report["pages"][name] = {"url": url, "status": response.status, "bytes": len(body), "final_url": response.url}
        except Exception as exc:
            report["pages"][name] = {"url": url, "error": f"{type(exc).__name__}: {exc}"}
    report["download_note"] = "If ARTISTA requires interaction/login, use the browser manually; this script does not bypass access controls."
    target = args.output_dir / "metadata.local.json"
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

