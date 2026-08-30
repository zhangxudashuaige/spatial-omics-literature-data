#!/usr/bin/env python3
"""把 stVCR 官方仓库固定到已记录 commit，保存在 Git 忽略的 raw/。"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

URL = "https://github.com/QiangweiPeng/stVCR"
COMMIT = "26aa79a63eba7a5e21726b1eb95bf6bb61cfe699"


def run(*args: str, cwd: Path | None = None) -> str:
    proc = subprocess.run(args, cwd=cwd, check=True, text=True, capture_output=True)
    return proc.stdout.strip()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", type=Path, default=root / "raw" / "official_repo")
    args = parser.parse_args()
    if not (args.destination / ".git").exists():
        run("git", "clone", "--filter=blob:none", URL, str(args.destination))
    run("git", "fetch", "origin", COMMIT, cwd=args.destination)
    run("git", "checkout", "--detach", COMMIT, cwd=args.destination)
    actual = run("git", "rev-parse", "HEAD", cwd=args.destination)
    if actual != COMMIT:
        raise SystemExit(f"commit mismatch: {actual}")
    inventory = {
        "repository": URL, "commit": actual,
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "license_first_lines": (args.destination / "LICENSE").read_text(encoding="utf-8").splitlines()[:12],
        "datasets": sorted(str(p.relative_to(args.destination)) for p in (args.destination / "datasets").rglob("*") if p.is_file()),
        "tutorial": sorted(str(p.relative_to(args.destination)) for p in (args.destination / "tutorial").rglob("*") if p.is_file()),
        "dependency_files": sorted(str(p.relative_to(args.destination)) for name in ("requirements*.txt", "environment*.yml", "pyproject.toml", "setup.py") for p in args.destination.glob(name)),
    }
    out = root / "raw" / "official_repo_inventory.local.json"
    out.write_text(json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(inventory, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

