#!/usr/bin/env python3
"""从10x官方页面列出可见数据资源；下载必须显式提供已核对URL。"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import urljoin

import requests


PAGE = "https://www.10xgenomics.com/resources/datasets/mouse-brain-serial-section-1-sagittal-posterior-1-standard-1-0-0"
ROOT = Path(__file__).resolve().parents[1]


def candidates() -> list[str]:
    response = requests.get(PAGE, timeout=30, headers={"User-Agent": "spagcn-data-inventory/1.0"})
    response.raise_for_status()
    hrefs = re.findall(r'(?:href|url)=["\']([^"\']+)', response.text, flags=re.I)
    return sorted({urljoin(PAGE, h) for h in hrefs if any(token in h.lower() for token in (".tar", ".h5", ".mtx", "download"))})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--download-url", help="人工核对后的10x直接文件URL")
    parser.add_argument("--file-name", help="与--download-url同时提供")
    args = parser.parse_args()
    print("官方页面：", PAGE)
    print("页面候选链接：")
    try:
        urls = candidates()
    except requests.RequestException as exc:
        print(f"无法自动读取动态页面（不代表数据不存在）：{exc}")
        print("请在浏览器打开官方页面，核对直接下载链接后再传入 --download-url 与 --file-name。")
        urls = []
    for url in urls:
        print(url)
    if args.download_url:
        if not args.file_name or not args.download_url.startswith("https://"):
            parser.error("必须同时提供安全的https --download-url和--file-name")
        target = ROOT / "datasets" / "mouse_brain_visium" / "raw" / Path(args.file_name).name
        target.parent.mkdir(parents=True, exist_ok=True)
        with requests.get(args.download_url, stream=True, timeout=(30, 180)) as response:
            response.raise_for_status()
            with target.open("wb") as handle:
                for chunk in response.iter_content(8 * 1024 * 1024):
                    if chunk:
                        handle.write(chunk)
        print(f"下载到 {target}")


if __name__ == "__main__":
    main()
