#!/usr/bin/env python3
"""从 10X 官方页面/历史 CDN 获取 Zheng68K 处理矩阵；默认仅探测。"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PAGE = "https://www.10xgenomics.com/cn/datasets/fresh-68-k-pbm-cs-donor-a-1-standard-1-1-0"
OFFICIAL_CANDIDATES = [
    "https://cf.10xgenomics.com/samples/cell-exp/1.1.0/fresh_68k_pbmc_donor_a/fresh_68k_pbmc_donor_a_filtered_gene_bc_matrices.tar.gz",
    "https://cf.10xgenomics.com/samples/cell-exp/1.1.0/fresh_68k_pbmc_donor_a/fresh_68k_pbmc_donor_a_raw_gene_bc_matrices.tar.gz",
]


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as h:
        while chunk := h.read(8 << 20): value.update(chunk)
    return value.hexdigest()


def download(url: str, target: Path, expected: int | None, retries: int = 50) -> None:
    part = target.with_suffix(target.suffix + ".part")
    if target.exists() and (expected is None or target.stat().st_size != expected):
        if part.exists():
            target.unlink()
        else:
            target.replace(part)
    last = None
    for attempt in range(1, retries + 1):
        offset = part.stat().st_size if part.exists() else 0
        headers = {"User-Agent": "paper-data-catalog/1.0"}
        if offset: headers["Range"] = f"bytes={offset}-"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=120) as response:
                if offset and response.status != 206: part.unlink(missing_ok=True); offset = 0
                with part.open("ab" if offset else "wb") as handle:
                    while chunk := response.read(1 << 20): handle.write(chunk)
            if expected is not None and part.stat().st_size != expected:
                raise IOError(f"size mismatch: {part.stat().st_size} != {expected}")
            part.replace(target); return
        except Exception as exc:
            last = exc
            if attempt < retries: time.sleep(min(30, 2**attempt))
    raise last


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--download", action="store_true"); parser.add_argument("--url"); parser.add_argument("--expected-size", type=int); parser.add_argument("--skip-probe", action="store_true", help="requires --url and --expected-size; useful for resuming after a transient HEAD failure"); parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "raw" / "zheng68k"); args = parser.parse_args()
    if args.skip_probe and (not args.url or not args.expected_size):
        parser.error("--skip-probe requires --url and --expected-size")
    urls = [args.url] if args.url else OFFICIAL_CANDIDATES
    report = {"source_page": PAGE, "sra": "SRP073767", "checked_at_utc": datetime.now(timezone.utc).isoformat(), "candidates": []}
    failed_download = False
    for url in urls:
        row = {"url": url, "verified": False}
        try:
            if args.skip_probe:
                row.update({"verified": True, "status": "probe_skipped_using_previously_verified_size", "size_bytes": args.expected_size, "final_url": url})
            else:
                req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "paper-data-catalog/1.0"})
                with urllib.request.urlopen(req, timeout=60) as response:
                    row.update({"verified": response.status == 200, "status": response.status, "size_bytes": int(response.headers.get("Content-Length", 0)) or None, "final_url": response.url})
            if args.download and row["verified"]:
                args.output_dir.mkdir(parents=True, exist_ok=True); target = args.output_dir / Path(urllib.parse.urlparse(url).path).name
                download(url, target, expected=row.get("size_bytes")); row.update({"local_path": str(target), "local_size_bytes": target.stat().st_size, "sha256": sha256(target), "download_date": datetime.now(timezone.utc).date().isoformat()})
        except Exception as exc:
            row["error"] = f"{type(exc).__name__}: {exc}"
            failed_download |= args.download
        report["candidates"].append(row)
    args.output_dir.mkdir(parents=True, exist_ok=True); (args.output_dir / "source_probe.local.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"); print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(1 if failed_download else 0)


if __name__ == "__main__":
    import urllib.parse
    main()
