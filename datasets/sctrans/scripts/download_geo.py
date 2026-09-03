#!/usr/bin/env python3
"""列出或下载 GEO Series supplementary 文件，不自动下载 SRA FASTQ。"""
from __future__ import annotations

import argparse
import hashlib
import html.parser
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


class Links(html.parser.HTMLParser):
    def __init__(self): super().__init__(); self.hrefs = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href: self.hrefs.append(href)


def geo_suppl_url(accession: str) -> str:
    accession = accession.upper()
    if not accession.startswith("GSE") or not accession[3:].isdigit():
        raise ValueError("only GSE accessions are supported")
    family = accession[:-3] + "nnn"
    return f"https://ftp.ncbi.nlm.nih.gov/geo/series/{family}/{accession}/suppl/"


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as h:
        while chunk := h.read(8 << 20): value.update(chunk)
    return value.hexdigest()


def open_retry(request, timeout: int = 60, retries: int = 4):
    error = None
    for attempt in range(1, retries + 1):
        try:
            return urllib.request.urlopen(request, timeout=timeout)
        except Exception as exc:
            error = exc
            if attempt < retries: time.sleep(2**attempt)
    raise error


def download(url: str, target: Path, retries: int = 4) -> None:
    part = target.with_suffix(target.suffix + ".part")
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "paper-data-catalog/1.0"})
            with open_retry(req, timeout=120) as response, part.open("wb") as out:
                total = 0
                while chunk := response.read(1 << 20):
                    out.write(chunk); total += len(chunk); print(f"\r{target.name}: {total:,} bytes", end="", flush=True)
            print(); part.replace(target); return
        except Exception:
            if attempt == retries: raise
            time.sleep(2**attempt)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accession", required=True)
    parser.add_argument("--list-only", action="store_true")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--file", action="append", help="exact filename; repeatable. Omit to download every supplementary file.")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    base = geo_suppl_url(args.accession)
    req = urllib.request.Request(base, headers={"User-Agent": "paper-data-catalog/1.0"})
    with open_retry(req, timeout=60) as response: page = response.read().decode("utf-8", "replace")
    parser_html = Links(); parser_html.feed(page)
    names = sorted({urllib.parse.unquote(h.split("?")[0]) for h in parser_html.hrefs if h not in ("../", "/") and not h.endswith("/")})
    selected = names if not args.file else [name for name in names if name in set(args.file)]
    if args.file and len(selected) != len(set(args.file)):
        missing = sorted(set(args.file) - set(selected)); raise SystemExit(f"requested filenames not present: {missing}")
    outdir = args.output_dir or Path(__file__).resolve().parents[1] / "raw" / args.accession.lower()
    report = {"accession": args.accession.upper(), "directory": base, "checked_at_utc": datetime.now(timezone.utc).isoformat(), "files": []}
    for name in names:
        url = urllib.parse.urljoin(base, name); row = {"name": name, "url": url}
        try:
            head = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "paper-data-catalog/1.0"})
            with open_retry(head, timeout=60) as response: row["size_bytes"] = int(response.headers.get("Content-Length", 0)) or None
        except Exception as exc: row["head_error"] = str(exc)
        if args.download and name in selected and not args.list_only:
            outdir.mkdir(parents=True, exist_ok=True); target = outdir / name; download(url, target)
            row.update({"local_path": str(target), "local_size_bytes": target.stat().st_size, "sha256": sha256(target), "download_date": datetime.now(timezone.utc).date().isoformat()})
        report["files"].append(row)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "geo_manifest.local.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__": main()
