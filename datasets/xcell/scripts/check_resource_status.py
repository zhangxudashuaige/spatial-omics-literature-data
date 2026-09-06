#!/usr/bin/env python3
"""
检查 X-Cell 官方资源公开状态。

功能:
- 访问官方 GitHub 和 Hugging Face API
- 检查数据仓库是否仍写着 Coming Soon
- 获取实际文件列表和每个文件大小
- 检查模型权重文件是否存在（.safetensors, .bin, .pt, .ckpt）
- 检查完整数据文件是否存在
- 记录检查时间
- 把结果写入 RESOURCE_STATUS.md

用法:
    python check_resource_status.py
"""
import sys
import json
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen, Request

BASE_DIR = Path(__file__).resolve().parent.parent
STATUS_FILE = BASE_DIR / "RESOURCE_STATUS.md"

HF_API = "https://huggingface.co/api"
GITHUB_API = "https://api.github.com"


def fetch_json(url, timeout=30):
    """获取 JSON 数据。"""
    try:
        req = Request(url, headers={"User-Agent": "xcell-data-checker/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [ERROR] 获取失败: {url}")
        print(f"          {e}")
        return None


def check_hf_dataset(repo_id):
    """检查 HuggingFace 数据集。"""
    print(f"\n  检查数据集: {repo_id}")

    # 获取数据集信息
    info = fetch_json(f"{HF_API}/datasets/{repo_id}")
    if not info:
        return {"status": "error", "files": [], "coming_soon": None}

    # 检查是否有 Coming Soon 标签
    tags = info.get("tags", [])
    card_data = info.get("cardData", {})
    description = info.get("description", "")

    coming_soon = any(
        "coming soon" in str(t).lower() or
        "coming_soon" in str(t).lower()
        for t in tags
    ) or "coming soon" in description.lower()

    # 获取文件列表
    files = fetch_json(f"{HF_API}/datasets/{repo_id}/tree/main")
    if not files:
        files = []

    file_list = []
    has_large_data = False
    for f in files:
        fname = f.get("path", "")
        fsize = f.get("size", 0)
        flfs = f.get("lfs", None)
        file_list.append({"path": fname, "size": fsize, "lfs": flfs is not None})
        if fsize > 1024 * 1024:  # > 1MB
            has_large_data = True

    print(f"    Coming Soon: {coming_soon}")
    print(f"    文件数: {len(file_list)}")
    print(f"    有大文件: {has_large_data}")
    for f in file_list[:10]:
        size_mb = f["size"] / (1024 * 1024) if f["size"] > 0 else 0
        lfs_mark = " [LFS]" if f["lfs"] else ""
        print(f"      - {f['path']} ({size_mb:.2f} MB){lfs_mark}")
    if len(file_list) > 10:
        print(f"      ... 还有 {len(file_list) - 10} 个文件")

    return {
        "status": "checked",
        "coming_soon": coming_soon,
        "files": file_list,
        "has_large_data": has_large_data,
    }


def check_hf_model(repo_id):
    """检查 HuggingFace 模型。"""
    print(f"\n  检查模型: {repo_id}")

    info = fetch_json(f"{HF_API}/models/{repo_id}")
    if not info:
        return {"status": "error", "files": []}

    files = fetch_json(f"{HF_API}/models/{repo_id}/tree/main")
    if not files:
        files = []

    file_list = []
    weight_exts = [".safetensors", ".bin", ".pt", ".ckpt", ".pth"]
    has_weights = False

    for f in files:
        fname = f.get("path", "")
        fsize = f.get("size", 0)
        flfs = f.get("lfs", None)
        is_weight = any(fname.endswith(ext) for ext in weight_exts)
        if is_weight:
            has_weights = True
        file_list.append({
            "path": fname, "size": fsize,
            "lfs": flfs is not None, "is_weight": is_weight
        })

    print(f"    有权重文件: {has_weights}")
    print(f"    文件数: {len(file_list)}")
    for f in file_list:
        if f["is_weight"]:
            size_mb = f["size"] / (1024 * 1024) if f["size"] > 0 else 0
            lfs_mark = " [LFS]" if f["lfs"] else ""
            print(f"      [权重] {f['path']} ({size_mb:.2f} MB){lfs_mark}")
    for f in file_list:
        if not f["is_weight"]:
            size_kb = f["size"] / 1024 if f["size"] > 0 else 0
            print(f"      - {f['path']} ({size_kb:.1f} KB)")

    return {
        "status": "checked",
        "has_weights": has_weights,
        "files": file_list,
    }


def check_github_repo(repo_id):
    """检查 GitHub 仓库。"""
    print(f"\n  检查 GitHub: {repo_id}")

    info = fetch_json(f"{GITHUB_API}/repos/{repo_id}")
    if not info:
        return {"status": "error"}

    print(f"    名称: {info.get('full_name')}")
    print(f"    描述: {info.get('description', 'N/A')}")
    print(f"    公开: {not info.get('private', True)}")
    print(f"    Stars: {info.get('stargazers_count', 0)}")

    return {"status": "checked", "public": not info.get("private", True)}


def generate_status_report(results, check_time):
    """生成 RESOURCE_STATUS.md。"""
    lines = []
    lines.append("# X-Cell 资源公开状态")
    lines.append("")
    lines.append(f"> 本文件由 `scripts/check_resource_status.py` 自动生成。")
    lines.append(f"> 最后更新: {check_time}")
    lines.append("")
    lines.append("## 检查结果摘要")
    lines.append("")
    lines.append("| 资源 | 类型 | 状态 | 检查时间 |")
    lines.append("|------|------|------|----------|")

    for name, data in results.items():
        rtype = data.get("type", "unknown")
        if data.get("coming_soon"):
            status = "**Coming Soon**"
        elif data.get("has_weights"):
            status = "已公开（含权重）"
        elif data.get("has_large_data"):
            status = "已公开（含数据）"
        elif data.get("status") == "checked":
            status = "已公开"
        elif data.get("status") == "error":
            status = "检查失败"
        else:
            status = "待检查"
        lines.append(f"| {name} | {rtype} | {status} | {check_time} |")

    lines.append("")
    lines.append("## 详细检查")
    lines.append("")

    for name, data in results.items():
        lines.append(f"### {name}")
        lines.append("")
        if data.get("status") == "error":
            lines.append("- **状态**: 检查失败（可能网络问题或资源不存在）")
        else:
            if "coming_soon" in data:
                lines.append(f"- **是否 Coming Soon**: {data['coming_soon']}")
            if "has_weights" in data:
                lines.append(f"- **模型权重文件是否存在**: {data['has_weights']}")
            if "has_large_data" in data:
                lines.append(f"- **完整数据文件是否存在**: {data['has_large_data']}")
            if data.get("files"):
                lines.append(f"- **实际文件列表** ({len(data['files'])} 个):")
                for f in data["files"][:20]:
                    size = f.get("size", 0)
                    if size > 1024 * 1024:
                        size_str = f"{size / (1024*1024):.2f} MB"
                    elif size > 1024:
                        size_str = f"{size / 1024:.1f} KB"
                    else:
                        size_str = f"{size} B"
                    lfs = " [LFS]" if f.get("lfs") else ""
                    weight = " [权重]" if f.get("is_weight") else ""
                    lines.append(f"  - `{f['path']}` ({size_str}){lfs}{weight}")
                if len(data["files"]) > 20:
                    lines.append(f"  - ... 还有 {len(data['files']) - 20} 个文件")
        lines.append(f"- **检查时间**: {check_time}")
        lines.append("")

    lines.append("## 运行检查")
    lines.append("")
    lines.append("```bash")
    lines.append("python scripts/check_resource_status.py")
    lines.append("```")
    lines.append("")
    lines.append("脚本会访问官方 GitHub 和 Hugging Face API，检查资源状态并更新本文件。")
    lines.append("")
    lines.append("**注意**: 如果资源仍为 Coming Soon，脚本不会报错退出，会输出\"尚未公开\"并保留官方链接。")

    return "\n".join(lines)


def main():
    print("=" * 70)
    print("X-Cell 资源公开状态检查")
    print("=" * 70)

    check_time = datetime.now().isoformat()
    results = {}

    # 1. 检查 X-Atlas/Pisces 训练数据
    print("\n[1/4] 检查核心训练数据...")
    results["X-Atlas/Pisces"] = check_hf_dataset("Xaira-Therapeutics/X-Atlas-Pisces")
    results["X-Atlas/Pisces"]["type"] = "HuggingFace Dataset"

    # 2. 检查 X-Cell 模型
    print("\n[2/4] 检查模型权重...")
    results["X-Cell 模型"] = check_hf_model("Xaira-Therapeutics/X-Cell")
    results["X-Cell 模型"]["type"] = "HuggingFace Model"

    # 3. 检查 GitHub 代码
    print("\n[3/4] 检查官方代码...")
    results["X-Cell 官方代码"] = check_github_repo("Xaira-Therapeutics/X-Cell")
    results["X-Cell 官方代码"]["type"] = "GitHub Repository"

    # 4. 检查外部评测数据
    print("\n[4/4] 检查外部评测数据...")
    eval_datasets = [
        ("Replogle-Nadig", "arcinstitute/Replogle-Nadig-Preprint"),
        ("Parse-1M", "arcinstitute/State-Parse-Filtered"),
        ("Tahoe-100M", "tahoe-bio/Tahoe-100M"),
    ]
    for name, repo_id in eval_datasets:
        results[name] = check_hf_dataset(repo_id)
        results[name]["type"] = "HuggingFace Dataset"

    # 生成报告
    print("\n" + "=" * 70)
    print("生成状态报告...")
    report = generate_status_report(results, check_time)

    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"报告已写入: {STATUS_FILE}")

    # 总结
    print("\n" + "=" * 70)
    print("检查完成")
    print("=" * 70)
    for name, data in results.items():
        if data.get("coming_soon"):
            print(f"  [Coming Soon] {name} — 尚未公开")
        elif data.get("has_weights") or data.get("has_large_data"):
            print(f"  [已公开]     {name} — 包含实际数据/权重")
        elif data.get("status") == "checked":
            print(f"  [已公开]     {name}")
        elif data.get("status") == "error":
            print(f"  [检查失败]   {name}")

    print("\n[INFO] 尚未公开的资源保留官方链接，不创建伪数据。")
    print("[INFO] 运行 download_public_resources.py 可下载已公开的外部资源。")

    return 0


if __name__ == "__main__":
    sys.exit(main())
