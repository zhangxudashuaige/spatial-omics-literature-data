#!/usr/bin/env python3
"""离线检查 Cheng 2024 数据清单、字段模板和合成样本。"""

from __future__ import annotations

import csv
import sys
from pathlib import Path, PurePosixPath


PAPER_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST = PAPER_DIR / "metadata" / "data_manifest.csv"

MANIFEST_FIELDS = {
    "item_id", "stage", "category", "description", "expected_file_count",
    "preferred_format", "local_path", "source_name", "source_url", "accession",
    "availability_status", "checked_at", "size_bytes", "sha256", "download_url", "notes",
}
ALLOWED_STATUSES = {
    "public", "not_publicly_retrievable", "not_found", "unknown", "reference_only",
}
REQUIRED_CATEGORIES = {
    "raw_fastq", "expression", "coordinates_2d", "coordinates_3d", "segmentation",
    "cell_annotation", "spatial_annotation", "sbfi", "histology", "metadata",
    "registration", "mesh", "external_reference",
}
TEMPLATE_FIELDS = {
    "section_metadata.template.csv": {
        "stage", "embryo_id", "section_id", "section_order", "section_thickness_um",
        "stereo_seq", "has_sbfi", "has_ssdna", "has_he", "qc_status", "qc_notes",
    },
    "cell_annotation.template.csv": {
        "cell_id", "section_id", "cluster_id", "cell_type", "marker_genes",
        "annotation_confidence", "reference_cell_type",
    },
    "spatial_annotation.template.csv": {
        "cell_id", "section_id", "organ", "spatial_domain", "subdomain",
    },
    "cell_coordinates.template.csv": {
        "cell_id", "section_id", "x_2d", "y_2d", "x_3d", "y_3d", "z_3d", "boundary_ref",
    },
    "registration_transform.template.csv": {
        "stage", "section_id", "source_image", "target_image", "rotation_deg",
        "translation_x", "translation_y", "scale_x", "scale_y", "affine_matrix_ref",
        "deformation_field_ref", "z_position_um",
    },
}


def csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def validate() -> list[str]:
    errors: list[str] = []
    fields, rows = csv_rows(MANIFEST)
    if set(fields) != MANIFEST_FIELDS:
        errors.append(f"manifest 字段不符：{fields}")

    ids = [row["item_id"] for row in rows]
    if len(ids) != len(set(ids)):
        errors.append("manifest 的 item_id 不唯一")
    categories = {row["category"] for row in rows}
    if not REQUIRED_CATEGORIES.issubset(categories):
        errors.append(f"manifest 缺少类别：{sorted(REQUIRED_CATEGORIES - categories)}")

    for row in rows:
        if row["availability_status"] not in ALLOWED_STATUSES:
            errors.append(f"{row['item_id']} 状态无效：{row['availability_status']}")
        path = PurePosixPath(row["local_path"])
        if path.is_absolute() or ".." in path.parts:
            errors.append(f"{row['item_id']} local_path 不安全：{row['local_path']}")
        if not row["local_path"].startswith("data/cheng-2024-mouse-embryo-3d/"):
            errors.append(f"{row['item_id']} 没有放入统一数据目录")
        if row["availability_status"] == "public" and not row["download_url"]:
            errors.append(f"{row['item_id']} 标为 public 却没有 download_url")
        if row["size_bytes"] and not row["size_bytes"].isdigit():
            errors.append(f"{row['item_id']} size_bytes 不是整数")
        if row["sha256"] and (len(row["sha256"]) != 64 or any(c not in "0123456789abcdefABCDEF" for c in row["sha256"])):
            errors.append(f"{row['item_id']} SHA-256 格式无效")

    schema_dir = PAPER_DIR / "metadata" / "schemas"
    for name, expected in TEMPLATE_FIELDS.items():
        actual, _ = csv_rows(schema_dir / name)
        if set(actual) != expected:
            errors.append(f"{name} 字段不符：{actual}")

    sample_dir = PAPER_DIR / "sample_data"
    _, sections = csv_rows(sample_dir / "synthetic_section_metadata.csv")
    _, cells = csv_rows(sample_dir / "synthetic_cells.csv")
    _, annotations = csv_rows(sample_dir / "synthetic_annotations.csv")
    _, expression = csv_rows(sample_dir / "synthetic_expression_long.csv")
    section_ids = {row["section_id"] for row in sections}
    cell_ids = {row["cell_id"] for row in cells}
    if len(cell_ids) != len(cells):
        errors.append("合成样本 cell_id 不唯一")
    if not {row["section_id"] for row in cells}.issubset(section_ids):
        errors.append("合成细胞引用了不存在的 section_id")
    if {row["cell_id"] for row in annotations} != cell_ids:
        errors.append("合成注释与细胞表的 cell_id 不完全一致")
    if not {row["cell_id"] for row in expression}.issubset(cell_ids):
        errors.append("合成表达表引用了不存在的 cell_id")

    forbidden_legacy = ("Mouse_E9.5_embryo.h5ad", "Mouse_E11.5_embryo.h5ad")
    audit_files = [
        PAPER_DIR / "datasets.csv",
        REPO_ROOT / "catalog" / "datasets.csv",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in audit_files)
    for legacy in forbidden_legacy:
        if legacy in combined:
            errors.append(f"仍把旧版 MOSTA 文件关联到本论文：{legacy}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("数据契约校验失败：", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("数据契约校验通过：清单、统一路径、字段模板和合成样本一致。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
