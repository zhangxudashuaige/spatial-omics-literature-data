"""下载 GSE278603 处理后 TAR：续传、重试、进度与 SHA256。"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import requests
from tqdm import tqdm

URL = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE278nnn/GSE278603/suppl/GSE278603_RAW.tar"
DEFAULT_OUTPUT = Path("data/external/GSE278603/GSE278603_RAW.tar")


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_url(url: str, timeout: int) -> dict[str, object]:
    headers = {"Range": "bytes=0-0", "User-Agent": "xie-2025-data-project/1.0"}
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=timeout)
        result = {
            "ok": response.status_code in (200, 206),
            "status_code": response.status_code,
            "content_length": response.headers.get("Content-Length", ""),
            "content_range": response.headers.get("Content-Range", ""),
            "accept_ranges": response.headers.get("Accept-Ranges", ""),
            "url": response.url,
        }
        response.close()
        return result
    except requests.RequestException as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "url": url}


def download(url: str, output: Path, retries: int, timeout: int) -> dict[str, object]:
    output.parent.mkdir(parents=True, exist_ok=True)
    part = output.with_suffix(output.suffix + ".part")
    for attempt in range(1, retries + 1):
        existing = part.stat().st_size if part.exists() else 0
        headers = {"User-Agent": "xie-2025-data-project/1.0"}
        if existing:
            headers["Range"] = f"bytes={existing}-"
        try:
            with requests.get(
                url, headers=headers, stream=True, timeout=(timeout, timeout)
            ) as response:
                response.raise_for_status()
                if existing and response.status_code != 206:
                    existing = 0
                    part.unlink(missing_ok=True)
                content_length = int(response.headers.get("Content-Length", 0))
                total = existing + content_length if content_length else None
                mode = "ab" if existing else "wb"
                with part.open(mode) as handle, tqdm(
                    total=total,
                    initial=existing,
                    unit="B",
                    unit_scale=True,
                    desc=output.name,
                ) as bar:
                    for chunk in response.iter_content(chunk_size=8 * 1024 * 1024):
                        if chunk:
                            handle.write(chunk)
                            bar.update(len(chunk))
            part.replace(output)
            return {
                "ok": True,
                "path": str(output.resolve()),
                "size_bytes": output.stat().st_size,
                "sha256": sha256_file(output),
            }
        except (requests.RequestException, OSError) as exc:
            if attempt == retries:
                return {
                    "ok": False,
                    "attempts": attempt,
                    "partial_path": str(part.resolve()),
                    "partial_size_bytes": part.stat().st_size if part.exists() else 0,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            time.sleep(min(2 ** (attempt - 1), 30))
    raise AssertionError("unreachable")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=URL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--retries", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--check-url", action="store_true")
    parser.add_argument(
        "--report", type=Path, default=Path("results/reports/download_status.json")
    )
    args = parser.parse_args()
    result = (
        check_url(args.url, args.timeout)
        if args.check_url
        else download(args.url, args.output, args.retries, args.timeout)
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
