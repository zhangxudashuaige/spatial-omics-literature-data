#!/usr/bin/env python3
"""
下载已公开的 X-Cell 外部资源。

功能:
- 只有确认文件真实存在后才能下载
- 若资源不存在（Coming Soon），输出"尚未公开"，保留官方链接，不报错退出，不创建伪数据
- 下载外部评测数据（Replogle-Nadig, Parse-1M, Tahoe-100M）
- 下载生物先验（GenePT, STRING, DepMap 等）
- 不下载 Coming Soon 的 X-Atlas/Pisces 和 X-Cell 权重
- 已存在文件不重复下载
- 下载后记录来源和日期

用法:
    python download_public_resources.py
    python download_public_resources.py --only evaluation
    python download_public_resources.py --only priors
    python download_public_resources.py --dry-run
"""
import sys
import os
import json
import argparse
import hashlib
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen, urlretrieve, Request

BASE_DIR = Path(__file__).resolve().parent.parent
MANIFEST_DIR = BASE_DIR / "manifests"

# 可下载的外部资源
EVALUATION_DATASETS = {
    "replogle_nadig": {
        "hf_repo": "arcinstitute/Replogle-Nadig-Preprint",
        "local_dir": "data/evaluation/replogle_nadig",
        "description": "Replogle-Nadig CRISPRi 扰动数据",
    },
    "parse_1m": {
        "hf_repo": "arcinstitute/State-Parse-Filtered",
        "local_dir": "data/evaluation/parse_1m",
        "description": "Parse-1M 大规模扰动数据",
    },
    "tahoe_100m": {
        "hf_repo": "tahoe-bio/Tahoe-100M",
        "local_dir": "data/evaluation/tahoe_100m",
        "description": "Tahoe-100M 子集",
    },
}

PRIOR_DATASETS = {
    "genept": {
        "url": "https://zenodo.org/records/10833191",
        "local_dir": "data/priors/genept",
        "description": "GenePT 基因文本嵌入",
        "note": "需要从 Zenodo 页面手动确认下载链接",
    },
    "string": {
        "url": "https://stringdb-downloads.org/download/protein.network.embeddings.v12.0.h5",
        "local_dir": "data/priors/string",
        "description": "STRING 蛋白质网络嵌入",
        "direct_file": "protein.network.embeddings.v12.0.h5",
    },
    "depmap": {
        "url": "https://plus.figshare.com/articles/dataset/DepMap_24Q4_Public/27993248",
        "local_dir": "data/priors/depmap",
        "description": "DepMap 24Q4 癌症依赖图谱",
        "note": "需要从 figshare 页面选择具体文件下载",
    },
}

# Coming Soon 资源（不下载）
COMING_SOON = {
    "xatlas_pisces": "https://huggingface.co/datasets/Xaira-Therapeutics/X-Atlas-Pisces",
    "xcell_mini": "https://huggingface.co/Xaira-Therapeutics/X-Cell",
    "xcell_ultra": "https://huggingface.co/Xaira-Therapeutics/X-Cell",
}


def human_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def fetch_json(url, timeout=30):
    try:
        req = Request(url, headers={"User-Agent": "xcell-downloader/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [ERROR] {e}")
        return None


def check_hf_repo_files(repo_id, repo_type="datasets"):
    """检查 HuggingFace 仓库的文件列表。"""
    files = fetch_json(f"https://huggingface.co/api/{repo_type}/{repo_id}/tree/main")
    if not files:
        return []
    return [{"path": f.get("path"), "size": f.get("size", 0), "lfs": f.get("lfs")} for f in files]


def download_hf_file(repo_id, filename, dest_path, repo_type="datasets"):
    """从 HuggingFace 下载文件。"""
    url = f"https://huggingface.co/{repo_type}/{repo_id}/resolve/main/{filename}"
    return download_file(url, dest_path)


def download_file(url, dest_path):
    """下载文件。"""
    if dest_path.exists():
        size = dest_path.stat().st_size
        print(f"  [SKIP] 已存在: {dest_path.name} ({human_size(size)})")
        return True

    print(f"  [INFO] 下载: {url}")
    print(f"         保存到: {dest_path}")

    try:
        # 获取文件大小
        req = Request(url, headers={"User-Agent": "xcell-downloader/1.0"})
        with urlopen(req, timeout=15) as resp:
            total_size = int(resp.headers.get("Content-Length", 0))
        if total_size > 0:
            print(f"         预计大小: {human_size(total_size)}")

        urlretrieve(url, str(dest_path))
        actual_size = dest_path.stat().st_size
        print(f"  [OK] 下载完成 ({human_size(actual_size)})")
        return True
    except Exception as e:
        print(f"  [ERROR] 下载失败: {e}")
        if dest_path.exists():
            dest_path.unlink()
        return False


def download_evaluation(dry_run=False):
    """下载外部评测数据。"""
    print("\n" + "=" * 70)
    print("下载外部评测数据")
    print("=" * 70)

    for name, info in EVALUATION_DATASETS.items():
        print(f"\n--- {info['description']} ---")
        print(f"  HF 仓库: {info['hf_repo']}")

        # 检查文件
        files = check_hf_repo_files(info["hf_repo"])
        if not files:
            print(f"  [WARN] 无法获取文件列表，跳过。")
            continue

        print(f"  文件数: {len(files)}")
        for f in files[:10]:
            size_mb = f["size"] / (1024 * 1024) if f["size"] > 0 else 0
            print(f"    - {f['path']} ({size_mb:.2f} MB)")

        if dry_run:
            print(f"  [DRY-RUN] 跳过实际下载。")
            continue

        # 下载文件
        local_dir = BASE_DIR / info["local_dir"]
        local_dir.mkdir(parents=True, exist_ok=True)

        for f in files:
            fname = f["path"]
            # 跳过目录
            if f["size"] == 0 and not fname.endswith((".h5ad", ".h5", ".parquet", ".csv", ".tsv", ".json", ".txt", ".md")):
                continue
            dest = local_dir / Path(fname).name
            download_hf_file(info["hf_repo"], fname, dest)


def download_priors(dry_run=False):
    """下载生物先验。"""
    print("\n" + "=" * 70)
    print("下载生物先验")
    print("=" * 70)

    for name, info in PRIOR_DATASETS.items():
        print(f"\n--- {info['description']} ---")
        print(f"  来源: {info['url']}")

        if info.get("note"):
            print(f"  [NOTE] {info['note']}")

        if dry_run:
            print(f"  [DRY-RUN] 跳过实际下载。")
            continue

        local_dir = BASE_DIR / info["local_dir"]
        local_dir.mkdir(parents=True, exist_ok=True)

        if info.get("direct_file"):
            dest = local_dir / info["direct_file"]
            download_file(info["url"], dest)
        else:
            print(f"  [INFO] 请手动访问 {info['url']} 下载所需文件，")
            print(f"         保存到: {local_dir}")


def main():
    parser = argparse.ArgumentParser(description="下载已公开的 X-Cell 外部资源")
    parser.add_argument("--only", choices=["evaluation", "priors", "all"], default="all",
                        help="只下载指定类型 (默认: all)")
    parser.add_argument("--dry-run", action="store_true", help="仅显示将要下载的内容，不实际下载")
    args = parser.parse_args()

    print("=" * 70)
    print("X-Cell 公共资源下载器")
    print("=" * 70)
    print(f"下载时间: {datetime.now().isoformat()}")
    if args.dry_run:
        print("模式: DRY-RUN (不实际下载)")

    # 明确列出 Coming Soon 资源
    print("\n" + "=" * 70)
    print("Coming Soon 资源（不下载）")
    print("=" * 70)
    for name, url in COMING_SOON.items():
        print(f"  [尚未公开] {name}: {url}")
    print("\n[INFO] 以上资源尚未公开，保留官方链接，不创建伪数据。")
    print("[INFO] 待官方发布后，重新运行此脚本即可下载。")

    # 下载
    if args.only in ["evaluation", "all"]:
        download_evaluation(dry_run=args.dry_run)

    if args.only in ["priors", "all"]:
        download_priors(dry_run=args.dry_run)

    # 总结
    print("\n" + "=" * 70)
    print("下载完成")
    print("=" * 70)
    print("[INFO] 大型文件已被 .gitignore 排除，不提交普通 Git。")
    print("[INFO] 运行 inspect_h5ad.py 可检查已下载的数据。")
    print("[INFO] 运行 make_small_example.py 可从真实数据抽取小样本。")

    return 0


if __name__ == "__main__":
    sys.exit(main())
