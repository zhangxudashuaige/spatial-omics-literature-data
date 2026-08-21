#!/usr/bin/env python3
"""导出资源数量、访问状态和缺失字段汇总。"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "metadata"
OUT = ROOT / "results" / "resource_summary.json"
URL_CHECK = ROOT / "results" / "url_check.csv"


def read(name: str) -> list[dict[str, str]]:
    with (META / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    corpora = read("pretraining_corpora.csv")
    datasets = read("downstream_datasets.csv")
    platforms = read("data_platforms.csv")
    models = read("model_repositories.csv")
    relations = read("task_model_matrix.csv")
    summary = {
        "counts": {
            "pretraining_corpora": len(corpora),
            "downstream_datasets": len(datasets),
            "data_platforms": len(platforms),
            "models": len(models),
            "task_model_relations": len(relations),
        },
        "corpus_access_types": Counter(row["access_type"] for row in corpora),
        "dataset_access_types": Counter(row["access_type"] for row in datasets),
        "official_model_repositories": sum(row["repository_type"] == "official" for row in models),
        "models_without_confirmed_official_code": [row["model_name"] for row in models if row["repository_type"] != "official"],
        "datasets_without_independent_paper": [
            row["dataset_name"] for row in datasets
            if "no independent dataset paper" in row["original_paper_title"]
        ],
        "datasets_without_paper_url": [row["dataset_name"] for row in datasets if not row["original_paper_url"]],
    }
    if URL_CHECK.exists():
        with URL_CHECK.open(encoding="utf-8-sig", newline="") as handle:
            url_rows = list(csv.DictReader(handle))
        summary["url_check"] = {
            "unique_urls": len(url_rows),
            "status_counts": Counter(row["status"] for row in url_rows),
            "not_found_urls": [row["url"] for row in url_rows if row["status"] == "not_found"],
            "note": "429/503通常为限流或临时服务错误；network_error表示本次检查无法判定，不等同于链接失效。",
        }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
