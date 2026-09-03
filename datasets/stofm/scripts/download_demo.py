#!/usr/bin/env python3
"""安全登记作者Drive demo；仅在给出已核对的单文件URL时下载。"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import requests
from tqdm import tqdm

FOLDER = "https://drive.google.com/drive/folders/1mHE8gf8MAPwzZoEB0vwOOfQ4lz3H_-xo?usp=sharing"
ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file-url", help="从官方文件夹人工核对得到的单文件直接下载URL")
    parser.add_argument("--file-name", help="本地文件名")
    parser.add_argument("--expected-bytes", type=int)
    parser.add_argument("--confirm", action="store_true")
    args = parser.parse_args()
    print("官方checkpoint/demo文件夹：", FOLDER)
    if not args.file_url:
        print("动态目录未提供稳定的公开文件清单API；为避免误下全部权重，未下载。")
        return
    if not (args.file_name and args.expected_bytes is not None and args.confirm):
        parser.error("下载必须同时提供--file-name、--expected-bytes和--confirm")
    if not args.file_url.startswith("https://"):
        parser.error("只允许HTTPS")
    target = ROOT / "data" / "raw" / "demo" / Path(args.file_name).name
    target.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(args.file_url, stream=True, timeout=(30, 180)) as response:
        response.raise_for_status()
        with target.open("wb") as handle, tqdm(total=args.expected_bytes, unit="B", unit_scale=True, desc=target.name) as bar:
            for chunk in response.iter_content(8 * 1024 * 1024):
                if chunk:
                    handle.write(chunk)
                    bar.update(len(chunk))
    if target.stat().st_size != args.expected_bytes:
        raise SystemExit(f"大小不符：实际{target.stat().st_size}，预期{args.expected_bytes}")
    sha = hashlib.sha256()
    with target.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            sha.update(block)
    print(f"SHA256 {sha.hexdigest()}  {target}")


if __name__ == "__main__":
    main()
