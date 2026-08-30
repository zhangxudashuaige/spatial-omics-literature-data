#!/usr/bin/env python3
"""从 Zenodo 14650474 获取真实清单；默认只下载小型 README。"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://zenodo.org/api/records/14650474"


def md5(path: Path, block: int = 8 << 20) -> str:
    digest = hashlib.md5()  # nosec B303 - integrity value supplied by Zenodo
    with path.open("rb") as handle:
        while chunk := handle.read(block):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_json(url: str) -> dict:
    last = None
    for attempt in range(1, 11):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "paper-data-catalog/1.0"})
            with urllib.request.urlopen(req, timeout=60) as response:
                return json.load(response)
        except Exception as exc:
            last = exc
            if attempt < 10:
                time.sleep(min(30, 2**attempt))
    raise last


def download(url: str, target: Path, expected: int, retries: int = 100) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_suffix(target.suffix + ".part")
    for attempt in range(1, retries + 1):
        have = partial.stat().st_size if partial.exists() else 0
        headers = {"User-Agent": "paper-data-catalog/1.0"}
        if have:
            headers["Range"] = f"bytes={have}-"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=120) as response:
                if have and getattr(response, "status", 200) != 206:
                    partial.unlink(missing_ok=True)
                    have = 0
                mode = "ab" if have else "wb"
                with partial.open(mode) as handle:
                    received = have
                    while chunk := response.read(1 << 20):
                        handle.write(chunk)
                        received += len(chunk)
                        print(f"\r{target.name}: {received:,}/{expected:,} bytes", end="", flush=True)
            print()
            if partial.stat().st_size != expected:
                raise IOError(f"size mismatch: {partial.stat().st_size} != {expected}")
            partial.replace(target)
            return
        except Exception as exc:
            print(f"attempt {attempt}/{retries} failed: {exc}")
            if attempt == retries:
                raise
            time.sleep(min(30, 2**attempt))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-large", action="store_true", help="also download 2.64 GB scData.zip")
    parser.add_argument("--retries", type=int, default=100, help="resume after short/proxy-truncated responses")
    parser.add_argument("--raw-dir", type=Path, default=Path(__file__).resolve().parents[1] / "raw")
    args = parser.parse_args()

    record = fetch_json(API)
    files = []
    for item in record.get("files", []):
        name = item["key"]
        checksum = item.get("checksum", "")
        url = item.get("links", {}).get("content") or item.get("links", {}).get("self")
        row = {"name": name, "size_bytes": item["size"], "checksum": checksum, "url": url}
        files.append(row)
        if name == "scData.zip" and not args.include_large:
            print(f"skip large file {name} ({item['size']:,} bytes); pass --include-large")
            continue
        target = args.raw_dir / name
        if not target.exists() or target.stat().st_size != item["size"]:
            download(url, target, item["size"], retries=args.retries)
        expected_md5 = checksum.removeprefix("md5:")
        actual = md5(target)
        if expected_md5 and actual.lower() != expected_md5.lower():
            raise SystemExit(f"MD5 mismatch for {name}: {actual} != {expected_md5}")
        row["local_md5"] = actual

    args.raw_dir.mkdir(parents=True, exist_ok=True)
    output = {
        "record_id": record.get("id"),
        "title": record.get("metadata", {}).get("title"),
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": files,
    }
    (args.raw_dir / "zenodo_manifest.local.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
