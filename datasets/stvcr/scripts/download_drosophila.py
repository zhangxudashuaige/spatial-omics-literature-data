#!/usr/bin/env python3
"""探测或下载官方教程链接的两个 Spateo 果蝇 H5AD。"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

FILES = {
    "E7-9h_cellbin_tdr_v2.h5ad": "https://www.dropbox.com/s/bvstb3en5kc6wui/E7-9h_cellbin_tdr_v2.h5ad?dl=1",
    "E9-10h_cellbin_tdr_v2.h5ad": "https://www.dropbox.com/s/q02sx6acvcqaf35/E9-10h_cellbin_tdr_v2.h5ad?dl=1",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(8 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def probe(url: str) -> dict:
    last = None
    for attempt in range(1, 5):
        try:
            req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "paper-data-catalog/1.0"})
            with urllib.request.urlopen(req, timeout=60) as response:
                return {"status": response.status, "final_url": response.url, "content_length": response.headers.get("Content-Length"), "content_type": response.headers.get("Content-Type")}
        except Exception as exc:
            last = exc
            if attempt < 4: time.sleep(min(30, 2**attempt))
    raise last


def download(url: str, target: Path, expected: int | None, retries: int = 100) -> None:
    partial = target.with_suffix(target.suffix + ".part")
    for attempt in range(1, retries + 1):
        offset = partial.stat().st_size if partial.exists() else 0
        headers = {"User-Agent": "paper-data-catalog/1.0"}
        if offset:
            headers["Range"] = f"bytes={offset}-"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=120) as response:
                if offset and response.status != 206:
                    partial.unlink(missing_ok=True)
                    offset = 0
                with partial.open("ab" if offset else "wb") as handle:
                    total = offset
                    while chunk := response.read(1 << 20):
                        handle.write(chunk); total += len(chunk)
                        print(f"\r{target.name}: {total:,} bytes", end="", flush=True)
            print()
            if expected is not None and partial.stat().st_size != expected:
                raise IOError(f"size mismatch: {partial.stat().st_size} != {expected}")
            partial.replace(target); return
        except Exception as exc:
            print(f"attempt {attempt}/{retries} failed: {exc}")
            if attempt == retries: raise
            time.sleep(min(30, 2**attempt))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--metadata-only", action="store_true")
    parser.add_argument("--retries", type=int, default=100)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "raw" / "drosophila_3d")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "files": []}
    for name, url in FILES.items():
        row = {"name": name, "source_url": url}
        try: row.update(probe(url))
        except Exception as exc: row["probe_error"] = f"{type(exc).__name__}: {exc}"
        target = args.output_dir / name
        if args.download and not args.metadata_only:
            expected = int(row["content_length"]) if row.get("content_length") else None
            download(url, target, expected=expected, retries=args.retries)
            row.update({"local_bytes": target.stat().st_size, "sha256": sha256(target)})
        report["files"].append(row)
    (args.output_dir / "download_manifest.local.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__": main()
