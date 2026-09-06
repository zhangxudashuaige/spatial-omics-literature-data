#!/usr/bin/env python3
"""
从 GEO 下载原始补充文件。

支持的数据集:
- Norman 2019: GSE133344
- Adamson 2016: GSE90546
- Dixit 2016: GSE90063
- Jost 2020: GSE132080
- Tian 2019: GSE124703
- Replogle 2020: GSE146194
- Horlbeck 2018: GSE116198

注意: 优先使用 GEARS 官方预处理数据 (download_gears_processed.py)。
此脚本用于需要原始数据的场景。
"""
import sys
import argparse
from pathlib import Path
from urllib.request import urlretrieve

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

GSE_URLS = {
    "GSE133344": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE133344",
    "GSE90546": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE90546",
    "GSE90063": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE90063",
    "GSE132080": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE132080",
    "GSE124703": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE124703",
    "GSE146194": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE146194",
    "GSE116198": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE116198",
    "GSE196826": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE196826",
}


def download_file(url, dest):
    """下载文件。"""
    print(f"[INFO] 下载: {url}")
    print(f"       保存到: {dest}")
    try:
        urlretrieve(url, str(dest))
        size_mb = dest.stat().st_size / (1024 * 1024)
        print(f"[OK] 下载完成 ({size_mb:.1f} MB)")
        return True
    except Exception as e:
        print(f"[ERROR] 下载失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="从 GEO 下载原始补充文件")
    parser.add_argument("--gse", required=True, help="GEO accession (如 GSE133344)")
    parser.add_argument("--list", action="store_true", help="仅列出补充文件信息，不下载")
    args = parser.parse_args()

    gse = args.gse.upper()
    if gse not in GSE_URLS:
        print(f"[WARN] 未配置 {gse} 的信息。")
        print(f"[WARN] 请访问 GEO 页面: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={gse}")
        return 1

    out_dir = RAW_DIR / gse
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print(f"GEO {gse} 原始数据下载")
    print("=" * 60)
    print(f"GEO 页面: {GSE_URLS[gse]}")
    print(f"输出目录: {out_dir}")
    print()

    if args.list:
        print("[INFO] 请访问 GEO 页面查看补充文件列表。")
        print("[INFO] 补充文件的具体名称和格式以 GEO 当前页面为准。")
        print("[INFO] 不伪造下载链接。")
        return 0

    print("[WARN] 此脚本需要用户手动确认补充文件的下载链接。")
    print("[WARN] 请从 GEO 页面获取实际补充文件 URL，然后使用 download_file() 下载。")
    print()
    print("[INFO] 替代方案: 使用 GEARS 官方预处理数据")
    print("       python scripts/download_gears_processed.py --dataset norman")
    print()
    print("[INFO] 原始数据文件较大，下载前请确认磁盘空间。")
    print("[INFO] 下载的原始文件保存在 data/raw/ 下，不进入 Git。")

    return 0


if __name__ == "__main__":
    sys.exit(main())
