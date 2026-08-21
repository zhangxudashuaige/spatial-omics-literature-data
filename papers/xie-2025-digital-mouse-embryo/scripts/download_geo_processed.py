"""下载 GSE278603 处理后数据：官方总包与六个 H5AD 双重路径。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import tarfile
import time
from pathlib import Path
from typing import Callable

import requests
from tqdm import tqdm

ARCHIVE_URLS = [
    "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE278603&format=file",
    "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE278nnn/GSE278603/suppl/GSE278603_RAW.tar",
]
DEFAULT_ARCHIVE = Path("data/external/GSE278603/GSE278603_RAW.tar")
DEFAULT_MANIFEST = Path("metadata/sample_manifest.csv")
DEFAULT_REPORT = Path("results/reports/download_status.json")
HDF5_MAGIC = b"\x89HDF\r\n\x1a\n"


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_samples(manifest: Path) -> list[dict[str, str]]:
    with manifest.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        headers = set(reader.fieldnames or [])
    required = {"gsm_accession", "file_name", "download_url", "local_path"}
    missing = required - headers
    if missing:
        raise ValueError(f"样本清单缺少字段：{sorted(missing)}")
    return rows


def check_url(url: str, timeout: int) -> dict[str, object]:
    """请求一个字节并立即关闭连接，验证下载端点而不下载大文件。"""
    headers = {"Range": "bytes=0-0", "User-Agent": "xie-2025-data-project/2.0"}
    try:
        with requests.get(
            url,
            headers=headers,
            stream=True,
            timeout=(timeout, timeout),
            allow_redirects=True,
        ) as response:
            return {
                "ok": response.status_code in (200, 206),
                "status_code": response.status_code,
                "content_type": response.headers.get("Content-Type", ""),
                "content_length": response.headers.get("Content-Length", ""),
                "content_range": response.headers.get("Content-Range", ""),
                "accept_ranges": response.headers.get("Accept-Ranges", ""),
                "requested_url": url,
                "final_url": response.url,
            }
    except requests.RequestException as exc:
        return {
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "requested_url": url,
        }


def validate_h5ad(path: Path) -> tuple[bool, str]:
    with path.open("rb") as handle:
        magic = handle.read(len(HDF5_MAGIC))
    valid = magic == HDF5_MAGIC
    return valid, "HDF5 文件头有效" if valid else "不是 HDF5/H5AD 文件"


def validate_archive(path: Path) -> tuple[bool, str]:
    try:
        with tarfile.open(path, "r:*") as archive:
            h5ad_names = {
                Path(member.name).name
                for member in archive.getmembers()
                if member.isfile() and member.name.lower().endswith(".h5ad")
            }
        if len(h5ad_names) != 6:
            return False, f"TAR 中检测到 {len(h5ad_names)} 个 H5AD，预期 6 个"
        return True, "TAR 可读取且包含 6 个 H5AD"
    except (tarfile.TarError, OSError) as exc:
        return False, f"TAR 校验失败：{type(exc).__name__}: {exc}"


def success_result(
    output: Path, requested_url: str, final_url: str, validation: str
) -> dict[str, object]:
    return {
        "ok": True,
        "requested_url": requested_url,
        "final_url": final_url,
        "path": str(output.resolve()),
        "size_bytes": output.stat().st_size,
        "sha256": sha256_file(output),
        "validation": validation,
    }


def download(
    url: str,
    output: Path,
    retries: int,
    timeout: int,
    validator: Callable[[Path], tuple[bool, str]],
) -> dict[str, object]:
    """支持 Range 续传；校验通过后才把 .part 改为正式文件名。"""
    output.parent.mkdir(parents=True, exist_ok=True)
    part = output.with_suffix(output.suffix + ".part")
    for attempt in range(1, retries + 1):
        existing = part.stat().st_size if part.exists() else 0
        headers = {"User-Agent": "xie-2025-data-project/2.0"}
        if existing:
            headers["Range"] = f"bytes={existing}-"
        try:
            with requests.get(
                url,
                headers=headers,
                stream=True,
                timeout=(timeout, timeout),
                allow_redirects=True,
            ) as response:
                if response.status_code == 416 and existing:
                    valid, detail = validator(part)
                    if valid:
                        part.replace(output)
                        return success_result(output, url, response.url, detail)
                response.raise_for_status()
                if existing and response.status_code != 206:
                    existing = 0
                    part.unlink(missing_ok=True)
                length = int(response.headers.get("Content-Length", 0))
                total = existing + length if length else None
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
                final_url = response.url
            valid, detail = validator(part)
            if not valid:
                raise ValueError(detail)
            part.replace(output)
            return success_result(output, url, final_url, detail)
        except (requests.RequestException, OSError, ValueError) as exc:
            if attempt == retries:
                return {
                    "ok": False,
                    "requested_url": url,
                    "output": str(output),
                    "attempts": attempt,
                    "partial_path": str(part.resolve()),
                    "partial_size_bytes": part.stat().st_size if part.exists() else 0,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            time.sleep(min(2 ** (attempt - 1), 30))
    raise AssertionError("unreachable")


def check_all(samples: list[dict[str, str]], timeout: int) -> dict[str, object]:
    archives = [check_url(url, timeout) for url in ARCHIVE_URLS]
    files = [
        {"gsm_accession": row["gsm_accession"], **check_url(row["download_url"], timeout)}
        for row in samples
    ]
    return {
        "mode": "link_check",
        "ok": any(item["ok"] for item in archives) and all(item["ok"] for item in files),
        "archive_endpoints": archives,
        "sample_endpoints": files,
    }


def download_archive(retries: int, timeout: int) -> dict[str, object]:
    attempts = []
    for url in ARCHIVE_URLS:
        result = download(url, DEFAULT_ARCHIVE, retries, timeout, validate_archive)
        attempts.append(result)
        if result["ok"]:
            return {"mode": "archive", "ok": True, "attempts": attempts}
    return {"mode": "archive", "ok": False, "attempts": attempts}


def download_files(
    samples: list[dict[str, str]], retries: int, timeout: int
) -> dict[str, object]:
    results = []
    for row in samples:
        result = download(
            row["download_url"],
            Path(row["local_path"]),
            retries,
            timeout,
            validate_h5ad,
        )
        results.append({"gsm_accession": row["gsm_accession"], **result})
    return {"mode": "files", "ok": all(item["ok"] for item in results), "files": results}


def write_report(path: Path, result: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="优先下载 GSE 总包；失败时可自动改为逐个下载六个 H5AD。"
    )
    parser.add_argument("--mode", choices=("auto", "archive", "files"), default="auto")
    parser.add_argument("--sample", help="只下载一个 GSM；例如 GSM9046244")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--retries", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--check-url", action="store_true")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    samples = read_samples(args.manifest)
    if args.sample:
        samples = [row for row in samples if row["gsm_accession"] == args.sample]
        if not samples:
            parser.error(f"样本清单中不存在 {args.sample}")

    if args.check_url:
        result = check_all(samples, args.timeout)
    elif args.sample or args.mode == "files":
        result = download_files(samples, args.retries, args.timeout)
    elif args.mode == "archive":
        result = download_archive(args.retries, args.timeout)
    else:
        archive_result = download_archive(args.retries, args.timeout)
        if archive_result["ok"]:
            result = archive_result
        else:
            fallback = download_files(samples, args.retries, args.timeout)
            result = {
                "mode": "auto",
                "ok": fallback["ok"],
                "archive": archive_result,
                "fallback": fallback,
            }

    write_report(args.report, result)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
