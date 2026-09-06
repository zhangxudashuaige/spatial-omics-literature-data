#!/usr/bin/env python3
"""
从 Hugging Face 下载 PerturbNet 数据。

第一阶段 (默认): 下载 example_data 中的小型教程数据
第二阶段: 下载 data_paper、models、pretrained_model (需用户确认)

不立即下载全部文件。下载前报告文件大小。
"""
import sys
import argparse
import csv
from pathlib import Path
from urllib.request import urlretrieve

HF_REPO = "cyclopeta/PerturbNet_reproduce"
BASE_URL = f"https://huggingface.co/{HF_REPO}/resolve/main"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
METADATA_DIR = Path(__file__).resolve().parent.parent / "metadata"

PHASE_CATEGORIES = {
    1: ["example_data"],
    2: ["data_paper", "models", "pretrained_model"],
}


def human_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def load_file_manifest():
    """加载文件清单。"""
    manifest_path = METADATA_DIR / "file_manifest.csv"
    if not manifest_path.exists():
        print("[WARN] file_manifest.csv 不存在。")
        print("[WARN] 请先运行: python scripts/inspect_huggingface.py")
        return []

    files = []
    with open(manifest_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            files.append(row)
    return files


def download_file(url, dest):
    """下载文件。"""
    print(f"[INFO] 下载: {url}")
    print(f"       保存到: {dest}")

    def report_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, downloaded * 100 / total_size)
            mb_dl = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            print(f"\r  进度: {percent:.1f}% ({mb_dl:.1f}/{mb_total:.1f} MB)", end="", flush=True)

    try:
        urlretrieve(url, str(dest), reporthook=report_hook)
        print()
        size_mb = dest.stat().st_size / (1024 * 1024)
        print(f"[OK] 下载完成 ({size_mb:.1f} MB)")
        return True
    except Exception as e:
        print()
        print(f"[ERROR] 下载失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="从 Hugging Face 下载 PerturbNet 数据")
    parser.add_argument("--phase", type=int, default=1, choices=[1, 2],
                        help="下载阶段: 1=example_data (默认), 2=data_paper+models+pretrained_model")
    parser.add_argument("--file", default=None, help="下载指定文件路径")
    parser.add_argument("--dry-run", action="store_true", help="仅显示将下载的文件，不实际下载")
    args = parser.parse_args()

    files = load_file_manifest()
    if not files:
        return 1

    # 筛选要下载的文件
    if args.file:
        to_download = [f for f in files if f["file_path"] == args.file]
        if not to_download:
            print(f"[ERROR] 未找到文件: {args.file}")
            return 1
    else:
        categories = PHASE_CATEGORIES[args.phase]
        to_download = [f for f in files if f["category"] in categories]

    if not to_download:
        print(f"[INFO] 阶段 {args.phase} 没有可下载的文件。")
        return 0

    # 报告文件大小
    total_size = sum(int(f.get("file_size_bytes", 0)) for f in to_download)
    print("=" * 60)
    print(f"阶段 {args.phase} 下载清单")
    print("=" * 60)
    for f in to_download:
        size = int(f.get("file_size_bytes", 0))
        print(f"  {f['file_path']}: {human_size(size)} (LFS: {f.get('lfs', '?')})")
    print(f"  总计: {len(to_download)} 个文件, {human_size(total_size)}")
    print()

    if args.dry_run:
        print("[INFO] dry-run 模式，未实际下载。")
        return 0

    # 大文件警告
    if total_size > 500 * 1024 * 1024:
        print("[WARN] 总下载量超过 500 MB。")
        print("[WARN] 请确认磁盘空间充足。")
        print("[WARN] 下载的大文件不会进入 Git (已被 .gitignore 排除)。")
        print()

    # 下载
    for f in to_download:
        path = f["file_path"]
        category = f["category"]

        # 确定本地保存路径
        if category == "example_data":
            local_dir = DATA_DIR / "example"
        elif category == "data_paper":
            local_dir = DATA_DIR / "processed" / "data_paper"
        elif category == "models":
            local_dir = DATA_DIR / "model_weights" / "models"
        elif category == "pretrained_model":
            local_dir = DATA_DIR / "model_weights" / "pretrained_model"
        else:
            local_dir = DATA_DIR / "other"

        local_dir.mkdir(parents=True, exist_ok=True)
        filename = Path(path).name
        dest = local_dir / filename

        if dest.exists():
            print(f"[SKIP] 已存在: {dest}")
            continue

        url = f"{BASE_URL}/{path}"
        download_file(url, dest)

    print()
    print("[DONE] 下载完成。")
    print(f"[INFO] 文件保存在: {DATA_DIR}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
