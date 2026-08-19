"""用合成 H5AD 验证结构检查、空间图和 marker 图的最小流程。"""

from __future__ import annotations

import json
from pathlib import Path

import anndata as ad
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

from create_sample_data import synthetic
from h5ad_utils import gene_vector, select_coordinates
from inspect_h5ad import inspect_one


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    h5ad = root / "data" / "processed" / "synthetic_test.h5ad"
    synthetic(h5ad)
    schema = inspect_one(h5ad)
    adata = ad.read_h5ad(h5ad, backed="r")
    try:
        coords, source = select_coordinates(adata, 2)
        values = gene_vector(adata, "Myl7")

        figures = root / "results" / "figures"
        figures.mkdir(parents=True, exist_ok=True)
        plt.figure(figsize=(7, 5.5))
        plt.scatter(coords[:, 0], coords[:, 1], s=8, alpha=0.8)
        plt.gca().set_aspect("equal")
        plt.title(f"合成测试数据：空间坐标（{source}）")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.tight_layout()
        spatial = figures / "synthetic_spatial_coordinates.png"
        plt.savefig(spatial, dpi=180)
        plt.close()

        plt.figure(figsize=(7, 5.5))
        points = plt.scatter(coords[:, 0], coords[:, 1], c=values, s=9, cmap="magma")
        plt.colorbar(points, label="Myl7 合成计数")
        plt.gca().set_aspect("equal")
        plt.title("合成测试数据：Myl7 空间表达")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.tight_layout()
        marker = figures / "synthetic_Myl7_expression.png"
        plt.savefig(marker, dpi=180)
        plt.close()
    finally:
        adata.file.close()

    report = {
        "notice": "验证使用完全合成数据，不代表 GSE278603 的真实结构或数值",
        "synthetic_h5ad": str(h5ad),
        "schema": schema,
        "spatial_figure": str(spatial),
        "marker_figure": str(marker),
    }
    report_path = root / "results" / "reports" / "synthetic_validation.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
