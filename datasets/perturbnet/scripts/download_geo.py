#!/usr/bin/env python3
"""
从 GEO 下载 PerturbNet 使用的原始数据。

支持的数据集:
- sci-Plex: GSE139944 (药物扰动)
- Norman CRISPRa: GSE133344 (基因扰动)
- Ursu TP53/KRAS: GSE161824 (蛋白质突变)
- Jorge GATA1: GSE215253 (蛋白质突变)

不默认下载全部 GEO 原始数据。优先使用 Hugging Face 上的作者处理后数据。
"""
import sys
import argparse
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

GSE_INFO = {
    "GSE139944": {
        "name": "sci-Plex",
        "description": "648857 细胞、3 细胞系、180 药物",
        "purpose": "药物扰动后单细胞表达分布预测",
    },
    "GSE133344": {
        "name": "Norman CRISPRa",
        "description": "109738 K562 细胞、2279 基因、230 扰动",
        "purpose": "预测未见单基因和双基因扰动",
    },
    "GSE161824": {
        "name": "Ursu TP53/KRAS",
        "description": "162532 A549 细胞、1629 基因、163 蛋白质序列",
        "purpose": "预测未见 TP53 和 KRAS 编码突变",
    },
    "GSE215253": {
        "name": "Jorge GATA1",
        "description": "142872 HSPC、2477 基因、257 GATA1 序列",
        "purpose": "预测未见 GATA1 突变及全部单氨基酸替换",
    },
}


def main():
    parser = argparse.ArgumentParser(description="从 GEO 下载 PerturbNet 原始数据")
    parser.add_argument("--gse", required=True, choices=list(GSE_INFO.keys()),
                        help="GEO accession")
    parser.add_argument("--list", action="store_true", help="仅显示信息，不下载")
    args = parser.parse_args()

    info = GSE_INFO[args.gse]
    url = f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={args.gse}"

    print("=" * 60)
    print(f"GEO {args.gse}: {info['name']}")
    print("=" * 60)
    print(f"描述: {info['description']}")
    print(f"用途: {info['purpose']}")
    print(f"URL: {url}")
    print()

    if args.list:
        print("[INFO] 请访问 GEO 页面查看补充文件列表。")
        print("[INFO] 补充文件的具体名称和格式以 GEO 当前页面为准。")
        print()
        print("[INFO] 替代方案: 使用 Hugging Face 上的作者处理后数据")
        print("       python scripts/inspect_huggingface.py")
        print("       python scripts/download_huggingface.py --phase 1")
        return 0

    out_dir = DATA_DIR / args.gse
    out_dir.mkdir(parents=True, exist_ok=True)

    print("[WARN] GEO 原始数据通常较大。")
    print("[WARN] 请从 GEO 页面获取实际补充文件下载链接。")
    print("[WARN] 下载的文件不会进入 Git (已被 .gitignore 排除)。")
    print()
    print(f"[INFO] 输出目录: {out_dir}")
    print()
    print("[INFO] 推荐优先使用 Hugging Face 上的作者处理后数据:")
    print("       python scripts/download_huggingface.py --phase 1")

    return 0


if __name__ == "__main__":
    sys.exit(main())
