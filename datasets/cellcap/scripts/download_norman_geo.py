#!/usr/bin/env python3
"""
从 GEO GSE133344 下载 Norman 2019 CRISPRa 数据的公开补充文件。

保留:
- 原始计数矩阵
- 基因列表
- 细胞 barcode
- sgRNA/扰动标签
- 单扰动与组合扰动信息
- 质控元数据
"""
import os
import sys
import gzip
import shutil
from pathlib import Path
from urllib.request import urlretrieve

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

GSE = "GSE133344"
GEO_URL = f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={GSE}"

# GSE133344 的补充文件（需以 GEO 当前页面为准，此处列出常见文件）
# 实际文件名可能不同，下载前请确认
SUPPLEMENTAL_FILES = {
    # 示例：实际文件名需从 GEO 页面获取
    # "GSE133344_RAW.tar": "https://...",
}


def download_file(url, dest):
    """下载文件，带进度显示。"""
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


def list_geo_supplements():
    """列出 GSE133344 的补充文件（需用户确认）。"""
    print("=" * 60)
    print(f"GEO {GSE} 补充文件下载")
    print("=" * 60)
    print()
    print(f"[INFO] 访问 GEO 页面查看补充文件: {GEO_URL}")
    print()
    print("[INFO] Norman 2019 数据通常包含:")
    print("       - 原始计数矩阵 (counts matrix)")
    print("       - 基因列表 (gene names)")
    print("       - 细胞 barcode")
    print("       - sgRNA 分配信息 (sgRNA assignment)")
    print("       - 扰动标签 (perturbation labels)")
    print("       - 质控元数据 (QC metadata)")
    print()
    print("[WARN] 补充文件的具体名称和格式以 GEO 当前页面为准。")
    print("[WARN] 请手动确认后更新本脚本中的 SUPPLEMENTAL_FILES 字典。")
    print()


def extract_tar(tar_path, dest_dir):
    """解压 tar 文件。"""
    import tarfile
    print(f"[INFO] 解压: {tar_path}")
    with tarfile.open(tar_path, "r:*") as tar:
        tar.extractall(dest_dir)
    print("[OK] 解压完成")


def main():
    list_geo_supplements()

    if not SUPPLEMENTAL_FILES:
        print("[WARN] 未配置补充文件下载链接。")
        print("[WARN] 请从 GEO 页面获取实际链接后更新本脚本。")
        print()
        print("[INFO] 替代方案: 使用 GEARS 官方预处理的 Norman 数据")
        print("       from gears import PertData")
        print('       pert_data = PertData("./data")')
        print('       pert_data.load(data_name="norman")')
        return 1

    for name, url in SUPPLEMENTAL_FILES.items():
        dest = RAW_DIR / name
        if dest.exists():
            print(f"[SKIP] 已存在: {dest}")
            continue
        if not download_file(url, dest):
            continue
        if name.endswith(".tar") or name.endswith(".tar.gz"):
            extract_tar(dest, RAW_DIR)

    print()
    print("[DONE] 下载流程结束。")
    print(f"[INFO] 原始文件保存在: {RAW_DIR}")
    print("[INFO] 下一步: python scripts/prepare_norman_anndata.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
