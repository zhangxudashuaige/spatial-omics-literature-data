"""以 backed='r' 检查 H5AD，并生成 CSV、JSON 和中文 Markdown。"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import anndata as ad
import h5py

from h5ad_utils import find_candidate_columns, find_coordinate_candidates


SUMMARY_FIELDS = [
    "file_name", "inspection_status", "n_obs", "n_vars", "shape",
    "x_type", "x_dtype", "x_storage", "obs_columns", "var_columns",
    "obsm_keys", "uns_keys", "layers_keys", "raw_exists",
    "obs_names_example", "var_names_example", "cell_type_candidates",
    "germ_layer_candidates", "section_candidates", "stage_candidates",
    "cluster_candidates", "coordinate_candidates", "expression_layer_candidates",
    "error",
]


def x_encoding(path: Path) -> str:
    with h5py.File(path, "r") as handle:
        if "X" not in handle:
            return "missing"
        node = handle["X"]
        encoding = node.attrs.get("encoding-type", "")
        if isinstance(encoding, bytes):
            encoding = encoding.decode()
        return str(encoding or type(node).__name__)


def inspect_one(path: Path) -> dict[str, Any]:
    row: dict[str, Any] = {field: "" for field in SUMMARY_FIELDS}
    row["file_name"] = path.name
    try:
        adata = ad.read_h5ad(path, backed="r")
        try:
            columns = [str(c) for c in adata.obs.columns]
            candidates = find_candidate_columns(columns)
            coords = find_coordinate_candidates(adata)
            x = adata.X
            encoding = x_encoding(path)
            layer_keys = [str(k) for k in adata.layers.keys() if k is not None]
            expression_layers = [
                str(k) for k in layer_keys
                if any(p in str(k).lower() for p in ("count", "umi", "raw", "norm", "log"))
            ]
            row.update(
                inspection_status="inspected",
                n_obs=int(adata.n_obs),
                n_vars=int(adata.n_vars),
                shape=f"{adata.n_obs} × {adata.n_vars}",
                x_type=type(x).__name__,
                x_dtype=str(getattr(x, "dtype", "unknown")),
                x_storage=encoding,
                obs_columns=json.dumps(columns, ensure_ascii=False),
                var_columns=json.dumps([str(c) for c in adata.var.columns], ensure_ascii=False),
                obsm_keys=json.dumps([str(k) for k in adata.obsm.keys()], ensure_ascii=False),
                uns_keys=json.dumps([str(k) for k in adata.uns.keys()], ensure_ascii=False),
                layers_keys=json.dumps(layer_keys, ensure_ascii=False),
                raw_exists=bool(adata.raw is not None),
                obs_names_example=json.dumps([str(x) for x in adata.obs_names[:5]], ensure_ascii=False),
                var_names_example=json.dumps([str(x) for x in adata.var_names[:5]], ensure_ascii=False),
                cell_type_candidates=json.dumps(candidates["cell_type"], ensure_ascii=False),
                germ_layer_candidates=json.dumps(candidates["germ_layer"], ensure_ascii=False),
                section_candidates=json.dumps(candidates["section"], ensure_ascii=False),
                stage_candidates=json.dumps(candidates["stage"], ensure_ascii=False),
                cluster_candidates=json.dumps(candidates["cluster"], ensure_ascii=False),
                coordinate_candidates=json.dumps(coords, ensure_ascii=False),
                expression_layer_candidates=json.dumps(expression_layers, ensure_ascii=False),
            )
        finally:
            if getattr(adata, "file", None) is not None:
                adata.file.close()
    except Exception as exc:  # 逐文件记录错误，其他样本仍继续
        row["inspection_status"] = "error"
        row["error"] = f"{type(exc).__name__}: {exc}"
    return row


def write_outputs(rows: list[dict[str, Any]], csv_path: Path, json_path: Path, md_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# H5AD 真实结构检查", "", "以下内容由 `inspect_h5ad.py` 实际读取生成。", ""]
    for row in rows:
        lines.extend([
            f"## {row['file_name']}", "",
            f"- 状态：`{row['inspection_status']}`",
            f"- shape：`{row['shape'] or '未取得'}`",
            f"- X：`{row['x_type'] or '未知'}`；dtype=`{row['x_dtype'] or '未知'}`；存储=`{row['x_storage'] or '未知'}`",
            f"- obs：`{row['obs_columns'] or '[]'}`",
            f"- var：`{row['var_columns'] or '[]'}`",
            f"- obsm：`{row['obsm_keys'] or '[]'}`",
            f"- layers：`{row['layers_keys'] or '[]'}`",
            f"- 坐标候选：`{row['coordinate_candidates'] or '[]'}`",
            f"- 细胞类型候选：`{row['cell_type_candidates'] or '[]'}`",
            f"- 错误：`{row['error'] or '无'}`", "",
        ])
    md_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("data/external/GSE278603/h5ad"))
    parser.add_argument("--csv", type=Path, default=Path("metadata/h5ad_summary.csv"))
    parser.add_argument("--json", type=Path, default=Path("results/reports/h5ad_schema.json"))
    parser.add_argument("--markdown", type=Path, default=Path("docs/h5ad_schema.md"))
    parser.add_argument("files", nargs="*", type=Path)
    args = parser.parse_args()
    files = args.files or sorted(args.input_dir.glob("*.h5ad"))
    if not files:
        print(f"没有找到 H5AD：{args.input_dir}")
        return 2
    rows = [inspect_one(path) for path in files]
    write_outputs(rows, args.csv, args.json, args.markdown)
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0 if all(r["inspection_status"] == "inspected" for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
