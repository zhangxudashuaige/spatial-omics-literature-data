#!/usr/bin/env python3
"""列出或下载GEO补充文件；默认只列清单，支持续传。"""
from __future__ import annotations

import argparse
import hashlib
import html
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from tqdm import tqdm


ROOT = Path(__file__).resolve().parents[1]


def series_prefix(accession: str) -> str:
    match = re.fullmatch(r"GSE(\d+)", accession.upper())
    if not match:
        raise ValueError("accession必须形如GSE111672")
    digits = match.group(1)
    return f"GSE{digits[:-3]}nnn"


def inventory(accession: str) -> list[dict[str, str]]:
    base = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{series_prefix(accession)}/{accession.upper()}/suppl/"
    response = requests.get(base, timeout=30)
    response.raise_for_status()
    rows = []
    for href, name in re.findall(r'<a href="([^"]+)">([^<]+)</a>', response.text):
        name = html.unescape(name)
        if name == "Parent Directory" or not (name.startswith(accession.upper() + "_") or name == "filelist.txt"):
            continue
        rows.append({"name": name, "url": urljoin(base, href)})
    return rows


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download(url: str, target: Path, retries: int = 3) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_suffix(target.suffix + ".part")
    for attempt in range(1, retries + 1):
        offset = partial.stat().st_size if partial.exists() else 0
        try:
            response = requests.get(url, headers={"Range": f"bytes={offset}-"} if offset else {}, stream=True, timeout=(30, 180))
            response.raise_for_status()
            if offset and response.status_code != 206:
                partial.unlink(missing_ok=True)
                offset = 0
            total = offset + int(response.headers.get("content-length", 0))
            with partial.open("ab" if offset else "wb") as handle, tqdm(total=total, initial=offset, unit="B", unit_scale=True, desc=target.name) as bar:
                for chunk in response.iter_content(8 * 1024 * 1024):
                    if chunk:
                        handle.write(chunk)
                        bar.update(len(chunk))
            partial.replace(target)
            print(f"SHA256 {sha256(target)}  {target}")
            return
        except Exception:
            if attempt == retries:
                raise
            time.sleep(2**attempt)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accession", default="GSE111672")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--file", help="只下载清单中完全匹配的文件名")
    args = parser.parse_args()
    rows = inventory(args.accession)
    for row in rows:
        print(f"{row['name']}\t{row['url']}")
    if not args.file:
        return
    match = next((row for row in rows if row["name"] == args.file), None)
    if match is None:
        parser.error("--file必须与官方清单中的文件名完全一致")
    download(match["url"], ROOT / "datasets" / "pancreatic_cancer_st" / "raw" / match["name"])


if __name__ == "__main__":
    main()
