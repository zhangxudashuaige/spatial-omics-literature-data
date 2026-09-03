#!/usr/bin/env python3
"""获取 HEIST 官方代码/模型元数据；仅在显式请求时下载固定版本资源。"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GITHUB_REPO = "Graph-and-Geometric-Learning/HEIST"
GITHUB_COMMIT = "b83615df17126581294b0ba3c8a3b30f7860c6ff"
HF_REPO = "HirenMadhu/HEIST"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "paper-datasets/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def file_records(root: Path) -> list[dict[str, Any]]:
    records = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and ".git" not in path.parts:
            records.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
    return records


def write_record(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已写入本地记录：{path}")


def metadata(raw_root: Path) -> int:
    github = get_json(f"https://api.github.com/repos/{GITHUB_REPO}/commits/{GITHUB_COMMIT}")
    hf = get_json(f"https://huggingface.co/api/models/{HF_REPO}")
    resolved_hf_revision = hf.get("sha")
    payload = {
        "retrieved_at": now(),
        "biological_data_downloaded": False,
        "github": {
            "repository": f"https://github.com/{GITHUB_REPO}",
            "requested_commit": GITHUB_COMMIT,
            "resolved_commit": github.get("sha"),
            "commit_date": github.get("commit", {}).get("committer", {}).get("date"),
            "license_note": "Repository README reports CC BY 4.0; verify repository files before reuse.",
        },
        "huggingface": {
            "repository": f"https://huggingface.co/{HF_REPO}",
            "resolved_revision": resolved_hf_revision,
            "last_modified": hf.get("lastModified"),
            "model_card_license": (hf.get("cardData") or {}).get("license"),
            "siblings": [
                {"file_name": item.get("rfilename")} for item in hf.get("siblings", [])
            ],
        },
    }
    write_record(raw_root / "metadata/resource_metadata.json", payload)
    print(f"GitHub commit: {payload['github']['resolved_commit']}")
    print(f"Hugging Face revision: {resolved_hf_revision}")
    return 0


def checkout_code(raw_root: Path) -> int:
    destination = raw_root / "code/HEIST"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not (destination / ".git").exists():
        raise SystemExit(f"目标已存在但不是 Git 仓库：{destination}")
    if not destination.exists():
        subprocess.run(
            ["git", "clone", "--filter=blob:none", f"https://github.com/{GITHUB_REPO}.git", str(destination)],
            check=True,
        )
    subprocess.run(["git", "-C", str(destination), "fetch", "origin", GITHUB_COMMIT], check=True)
    subprocess.run(["git", "-C", str(destination), "checkout", "--detach", GITHUB_COMMIT], check=True)
    resolved = subprocess.check_output(
        ["git", "-C", str(destination), "rev-parse", "HEAD"], text=True
    ).strip()
    if resolved != GITHUB_COMMIT:
        raise SystemExit(f"commit 不匹配：期望 {GITHUB_COMMIT}，实际 {resolved}")
    write_record(
        raw_root / "metadata/code_inventory.json",
        {
            "source_url": f"https://github.com/{GITHUB_REPO}",
            "download_date": now(),
            "commit": resolved,
            "license_note": "Repository README reports CC BY 4.0.",
            "files": file_records(destination),
        },
    )
    return 0


def download_model(raw_root: Path, revision: str | None) -> int:
    try:
        from huggingface_hub import HfApi, snapshot_download
    except ImportError as exc:
        raise SystemExit("缺少 huggingface_hub：pip install huggingface_hub") from exc

    api = HfApi()
    info = api.model_info(HF_REPO, revision=revision or "main")
    resolved = info.sha
    if revision is None:
        print(f"拒绝用浮动 main 下载。当前解析 revision 为 {resolved}")
        print(f"请重跑：--revision {resolved}")
        return 2
    destination = raw_root / "model"
    destination.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id=HF_REPO,
        revision=revision,
        local_dir=destination,
        allow_patterns=["*.json", "*.md", "*.safetensors", ".gitattributes"],
    )
    write_record(
        raw_root / "metadata/model_inventory.json",
        {
            "source_url": f"https://huggingface.co/{HF_REPO}",
            "download_date": now(),
            "requested_revision": revision,
            "resolved_revision": resolved,
            "license_note": "Hugging Face model card reports MIT; biological data are not covered by this entry.",
            "files": file_records(destination),
        },
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["metadata", "code", "model"])
    parser.add_argument("--revision", help="下载 Hugging Face 模型时必须显式给出固定 commit SHA")
    parser.add_argument(
        "--raw-root",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data/heist/raw",
    )
    args = parser.parse_args()
    args.raw_root.mkdir(parents=True, exist_ok=True)
    try:
        if args.action == "metadata":
            return metadata(args.raw_root)
        if args.action == "code":
            return checkout_code(args.raw_root)
        return download_model(args.raw_root, args.revision)
    except Exception as exc:
        print(f"失败：{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
