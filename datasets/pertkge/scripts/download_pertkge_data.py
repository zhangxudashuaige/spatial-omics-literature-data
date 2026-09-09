#!/usr/bin/env python3
"""下载 PertKGE 数据（Google Drive 数据包和 LINCS 上游数据）。"""
import sys, argparse
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent.parent

# Google Drive 文件ID
PERTKGE_DATA_ID = "1jFo0dDAnUOzMoKHFqPRM4pd_loTFwmMa"
DOCKING_FOLDER_ID = "1wPcn7EaQldWbXONrRVd-ZOcBsNo6IXHw"

def human_size(b):
    for u in ["B","KB","MB","GB"]:
        if b < 1024: return f"{b:.2f} {u}"
        b /= 1024
    return f"{b:.2f} TB"

def list_resources():
    print("=== PertKGE 资源清单 ===\n")
    print("1. 作者数据与模型 (Google Drive)")
    print(f"   URL: https://drive.google.com/file/d/{PERTKGE_DATA_ID}/view")
    print("   说明: 需手动确认文件列表，不猜测包内有模型权重")
    print()
    print("2. 对接网格 (Google Drive 文件夹)")
    print(f"   URL: https://drive.google.com/drive/folders/{DOCKING_FOLDER_ID}")
    print("   说明: 案例与对接资源")
    print()
    print("3. LINCS Phase I (GSE92742)")
    print("   URL: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE92742")
    print()
    print("4. LINCS Phase II (GSE70138)")
    print("   URL: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE70138")
    print()
    print("5. PertKGE 官方代码")
    print("   URL: https://github.com/myzhengSIMM/PertKGE")
    print()
    print("注意:")
    print("  - Google Drive 大文件需使用 gdown 工具下载")
    print("  - 不默认作者案例目录包含全部湿实验原始数据")
    print("  - 下载失败、需要登录、文件缺失或大小未知时，明确标注状态")

def download_google_drive(file_id, output):
    print(f"[INFO] 下载 Google Drive 文件: {file_id}")
    print(f"[INFO] 输出: {output}")
    print("[INFO] 建议使用 gdown: pip install gdown && gdown <FILE_ID> -O <OUTPUT>")
    print("[INFO] 大文件可能需要确认病毒扫描提示。")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--list-only", action="store_true")
    p.add_argument("--download", choices=["pertkge_data", "docking", "lincs_phase1", "lincs_phase2"])
    p.add_argument("--output", help="输出文件路径")
    args = p.parse_args()

    if args.list_only or not args.download:
        list_resources()
        return 0

    if args.download == "pertkge_data":
        out = args.output or str(BASE / "data" / "raw" / "pertkge_package.zip")
        download_google_drive(PERTKGE_DATA_ID, out)
    elif args.download == "docking":
        print(f"[INFO] 对接网格文件夹: https://drive.google.com/drive/folders/{DOCKING_FOLDER_ID}")
        print("[INFO] 文件夹需手动浏览并选择文件下载。")
    elif args.download in ["lincs_phase1", "lincs_phase2"]:
        gse = "GSE92742" if args.download == "lincs_phase1" else "GSE70138"
        print(f"[INFO] LINCS {gse}")
        print(f"[INFO] URL: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={gse}")
        print("[INFO] LINCS 数据较大，建议从 GEO 或 CLUE 平台手动下载。")
    return 0

if __name__ == "__main__":
    sys.exit(main())
