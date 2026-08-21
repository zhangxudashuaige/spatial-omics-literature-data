#!/usr/bin/env python3
"""从CSV生成Markdown资源表，并更新README中的自动摘要。"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "metadata"
OUTPUT = ROOT / "docs" / "resource_tables.md"
README = ROOT / "README.md"
START = "<!-- GENERATED_SUMMARY_START -->"
END = "<!-- GENERATED_SUMMARY_END -->"


def rows(name: str) -> list[dict[str, str]]:
    with (META / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def md_table(items: list[dict[str, str]], columns: list[str]) -> str:
    def clean(value: str) -> str:
        return (value or "").replace("|", "\\|").replace("\n", " ")
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join(["---"] * len(columns)) + "|"]
    for item in items:
        lines.append("| " + " | ".join(clean(item.get(column, "")) for column in columns) + " |")
    return "\n".join(lines)


def main() -> int:
    corpora = rows("pretraining_corpora.csv")
    datasets = rows("downstream_datasets.csv")
    platforms = rows("data_platforms.csv")
    models = rows("model_repositories.csv")
    relations = rows("task_model_matrix.csv")
    papers = rows("original_papers.csv")
    sections = [
        "# 自动生成的资源表\n\n> 请勿手工编辑；运行 `python scripts/generate_markdown_tables.py` 重新生成。",
        "## 预训练语料\n\n" + md_table(corpora, ["model", "corpus_name", "survey_reported_size", "access_type", "official_url"]),
        "## 下游数据\n\n" + md_table(datasets, ["dataset_id", "dataset_name", "dataset_category", "accession", "original_paper_url"]),
        "## 下游数据原始论文\n\n" + md_table(papers, ["paper_id", "title", "year", "journal_or_venue", "related_dataset_ids", "paper_url"]),
        "## 数据平台\n\n" + md_table(platforms, ["platform_name", "main_use", "official_url", "requires_account"]),
        "## 模型仓库\n\n" + md_table(models, ["model_name", "model_category", "repository_type", "official_repository", "paper_url"]),
    ]
    OUTPUT.write_text("\n\n".join(sections) + "\n", encoding="utf-8")

    official = sum(row["repository_type"] == "official" for row in models)
    summary = (
        f"{START}\n"
        f"当前目录包含 **{len(corpora)}** 个预训练语料、**{len(datasets)}** 个唯一的下游数据集、"
        f"**{len(papers)}** 篇下游数据原始论文、**{len(platforms)}** 个数据平台、"
        f"**{len(models)}** 个模型（其中 **{official}** 个确认官方仓库）和 "
        f"**{len(relations)}** 条模型—数据—任务关系。完整自动表格见 "
        f"[`docs/resource_tables.md`](docs/resource_tables.md)。\n"
        f"{END}"
    )
    text = README.read_text(encoding="utf-8")
    before, remainder = text.split(START, 1)
    _, after = remainder.split(END, 1)
    README.write_text(before + summary + after, encoding="utf-8")
    print(f"生成 {OUTPUT} 并更新 README 摘要。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
