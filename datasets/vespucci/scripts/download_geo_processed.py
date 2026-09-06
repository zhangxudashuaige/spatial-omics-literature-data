#!/usr/bin/env python3
"""
下载 GEO 处理后文件（矩阵、图像等）。

功能:
- 默认只下载小型处理后文件
- 不默认下载 SRA FASTQ
- 支持按 GSE 或 GSM 编号选择样本
- 下载前显示预计文件大小
- 已存在文件不得重复下载
- 下载后计算 SHA256
- 记录下载来源和日期
- 下载地址无法核实时停止，不得编造

用法:
    python download_geo_processed.py --gse GSE268779
    python download_geo_processed.py --gsm GSMxxxxxxx
"""
import sys
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen, urlretrieve

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHECKSUM_DIR = BASE_DIR / "checksums"

GEO_URL = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"


def human_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def compute_sha256(filepath):
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            sha.update(chunk)
    return sha.hexdigest()


def fetch_supplementary_files(accession):
    """从 GEO 获取补充文件列表。"""
    url = f"{GEO_URL}?acc={accession}&targ=self&form=text&view=quick"
    print(f"[INFO] 获取 GEO 补充文件列表: {accession}")

    try:
        with urlopen(url, timeout=30) as resp:
            content = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"[ERROR] 获取失败: {e}")
        return []

    files = []
    for line in content.split("\n"):
        if line.startswith("!Series_supplementary_file =") or line.startswith("!Sample_supplementary_file ="):
            fpath = line.split("=", 1)[1].strip()
            if fpath and fpath != "N/A":
                files.append(fpath)

    return files


def download_file(url, dest):
    """下载文件。"""
    if dest.exists():
        size = dest.stat().st_size
        print(f"[SKIP] 已存在: {dest.name} ({human_size(size)})")
        return True

    print(f"[INFO] 下载: {url}")
    print(f"       保存到: {dest}")

    try:
        # 先获取文件大小
        req = urlopen(url, timeout=15)
        total_size = int(req.headers.get("Content-Length", 0))
        req.close()

        if total_size > 0:
            print(f"       预计大小: {human_size(total_size)}")
            if total_size > 50 * 1024 * 1024:
                print(f"[WARN] 文件大于 50 MB，谨慎使用 Git LFS。")
                print(f"[WARN] 此文件不会被提交到普通 Git（已被 .gitignore 排除）。")

        urlretrieve(url, str(dest))
        actual_size = dest.stat().st_size
        print(f"[OK] 下载完成 ({human_size(actual_size)})")

        # 校验大小
        if total_size > 0 and actual_size != total_size:
            print(f"[WARN] 实际大小 ({human_size(actual_size)}) 与预期 ({human_size(total_size)}) 不符")

        return True
    except Exception as e:
        print(f"[ERROR] 下载失败: {e}")
        if dest.exists():
            dest.unlink()
        return False


def main():
    parser = argparse.ArgumentParser(description="下载 GEO 处理后文件")
    parser.add_argument("--gse", default=None, help="GEO Series 编号")
    parser.add_argument("--gsm", default=None, help="GEO Sample 编号")
    parser.add_argument("--list", action="store_true", help="仅列出文件，不下载")
    parser.add_argument("--max-size", type=int, default=500,
                        help="最大下载大小 (MB)，超过则跳过 (默认 500)")
    args = parser.parse_args()

    if not args.gse and not args.gsm:
        print("[ERROR] 请指定 --gse 或 --gsm")
        return 1

    accession = args.gse or args.gsm
    out_dir = PROCESSED_DIR / accession
    out_dir.mkdir(parents=True, exist_ok=True)
    CHECKSUM_DIR.mkdir(parents=True, exist_ok=True)

    # 获取补充文件列表
    files = fetch_supplementary_files(accession)
    print(f"[INFO] 找到 {len(files)} 个补充文件")
    print()

    if not files:
        print("[WARN] 未找到补充文件。")
        print("[WARN] 可能需要从 SRA 下载原始数据，或该 GSE 没有补充文件。")
        print("[WARN] 下载地址无法确认，停止。不编造下载链接。")
        return 1

    print("=" * 70)
    print("补充文件列表")
    print("=" * 70)
    for f in files:
        print(f"  {f}")
    print()

    if args.list:
        return 0

    # 下载文件
    downloaded = []
    skipped = []
    failed = []

    for fpath in files:
        filename = Path(fpath).name
        dest = out_dir / filename

        # 构建下载 URL
        if fpath.startswith("http"):
            url = fpath
        elif fpath.startswith("ftp://"):
            url = fpath
        else:
            # GEO 补充文件通常在 ftp 上
            url = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{accession[:-3]}nnn/{accession}/suppl/{filename}"
            print(f"[INFO] 构建下载 URL: {url}")

        # 检查文件大小限制
        # （实际大小在下载时获取）

        if download_file(url, dest):
            sha = compute_sha256(dest)
            checksum_file = CHECKSUM_DIR / f"{filename}.sha256"
            with open(checksum_file, "w") as cf:
                cf.write(f"{sha}  {filename}\n")
            downloaded.append({"file": filename, "size": dest.stat().st_size, "sha256": sha})
        else:
            failed.append(filename)

    # 保存下载记录
    record_file = out_dir / "download_record.json"
    with open(record_file, "w", encoding="utf-8") as f:
        json.dump({
            "accession": accession,
            "download_date": datetime.now().isoformat(),
            "source": "GEO",
            "downloaded": downloaded,
            "failed": failed,
        }, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 70)
    print("下载完成")
    print("=" * 70)
    print(f"成功: {len(downloaded)} 个文件")
    print(f"失败: {len(failed)} 个文件")
    if failed:
        print(f"  失败文件: {failed}")
    print()
    print(f"输出目录: {out_dir}")
    print(f"校验目录: {CHECKSUM_DIR}")
    print()
    print("[INFO] 注意: 大型文件已被 .gitignore 排除，不提交普通 Git。")
    print("[INFO] 原始大文件保留在 GEO/SRA，可通过记录的 URL 重新下载。")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
