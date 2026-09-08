#!/usr/bin/env python3
"""从 Google Drive 下载数据（DynaMorph 示例和 DynaCLR 感染演示）。

注意：Google Drive 文件夹需要手动确认文件列表和ID，不编造下载链接。
"""
import sys, argparse
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

# 已知的 Google Drive 文件夹ID
DRIVE_FOLDERS = {
    "dynamorph_example": {
        "url": "https://drive.google.com/drive/folders/11GoWDwaBo1PE5FO5tcnGCOzA4pzjf-Tk",
        "folder_id": "11GoWDwaBo1PE5FO5tcnGCOzA4pzjf-Tk",
        "description": "DynaMorph Microglia 示例数据",
        "local": "data/microglia_dynamorph",
    },
    "dynaclr_infection": {
        "url": "https://drive.google.com/drive/folders/1SeQcWQcTF3Xfvz4XU_2DzMzGSxc-Hkgb",
        "folder_id": "1SeQcWQcTF3Xfvz4XU_2DzMzGSxc-Hkgb",
        "description": "DynaCLR 感染与细胞器演示资源",
        "local": "data/dynaclr_infection",
    },
}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--folder", choices=list(DRIVE_FOLDERS.keys()), required=True)
    p.add_argument("--list-only", action="store_true")
    p.add_argument("--file-id", help="单个文件ID（从Google Drive手动获取）")
    p.add_argument("--output", help="输出文件名")
    args = p.parse_args()

    info = DRIVE_FOLDERS[args.folder]
    print(f"=== {info['description']} ===")
    print(f"URL: {info['url']}")
    print(f"文件夹ID: {info['folder_id']}")
    print(f"本地路径: {info['local']}")
    print()

    if args.list_only:
        print("[INFO] Google Drive 文件夹内容需要在浏览器中手动查看。")
        print("[INFO] 打开上述URL，记录需要下载的文件名和文件ID。")
        print("[INFO] 文件ID可从文件分享链接中获取: https://drive.google.com/file/d/<FILE_ID>/view")
        return 0

    if not args.file_id:
        print("[ERROR] 请使用 --file-id 指定要下载的文件ID。")
        print("[INFO] 先使用 --list-only 在浏览器中查看文件夹内容。")
        print("[INFO] 不编造下载链接。")
        return 1

    if not args.output:
        print("[ERROR] 请使用 --output 指定输出文件名。")
        return 1

    out_dir = BASE / info["local"]
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / args.output

    if dest.exists():
        print(f"[SKIP] 已存在: {dest.name}")
        return 0

    download_url = f"https://drive.google.com/uc?export=download&id={args.file_id}"
    print(f"[INFO] 下载: {download_url}")
    print(f"[INFO] 输出: {dest}")
    print("[INFO] 大文件可能需要确认病毒扫描提示。")
    print("[INFO] 建议使用 gdown 工具: pip install gdown && gdown <FILE_ID> -O <OUTPUT>")
    return 0

if __name__ == "__main__":
    sys.exit(main())
