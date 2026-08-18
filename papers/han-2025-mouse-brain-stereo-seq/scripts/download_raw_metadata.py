"""获取 CNP0003837 的公开项目元数据，不下载 FASTQ 或图像大文件。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests


PROJECT = "CNP0003837"
API_URL = f"https://db.cngb.org/cnsa/ajax/project/public_view/?q={PROJECT}"
PROJECT_URL = f"https://db.cngb.org/data_resources/project/{PROJECT}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("data/raw/metadata"))
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / "CNP0003837_project_public_view.json"
    print(f"项目页面：{PROJECT_URL}")
    print("说明：项目总量约 125.58 TB，完整数据需按官方页面申请或联系 datasubs@genomics.cn。")

    try:
        response = requests.get(
            API_URL,
            headers={"User-Agent": "han-2025-data-catalog/1.0"},
            timeout=args.timeout,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        print(f"未能获取公开 API：{exc}")
        print("请在浏览器打开项目页面，下载 Metadata 或 FTP 文件清单。")
        return 2

    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已保存：{output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
