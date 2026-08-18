"""读取合成空间表达和细胞元数据，按 cell_id 合并并绘制空间散点图。"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "sample"
FIGURE = ROOT / "results" / "figures" / "sample_Gad1_spatial_expression.png"
TABLE = ROOT / "results" / "tables" / "sample_Gad1_joined.csv"


def main() -> int:
    expression = pd.read_csv(SAMPLE / "sample_spatial_expression.csv")
    metadata = pd.read_csv(SAMPLE / "sample_cell_metadata.csv")
    gene = expression.loc[expression["gene"] == "Gad1", ["cell_id", "umi_count"]]
    merged = metadata.merge(gene, on="cell_id", how="inner", validate="one_to_one")
    if merged.empty:
        raise RuntimeError("Gad1 与细胞元数据合并后为空。")

    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    TABLE.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(TABLE, index=False, encoding="utf-8-sig")
    fig, ax = plt.subplots(figsize=(7.2, 5.4), constrained_layout=True)
    scatter = ax.scatter(merged["x"], merged["y"], c=merged["umi_count"], s=90,
                         cmap="viridis", edgecolor="white", linewidth=0.5)
    ax.set_title("Synthetic sample: Gad1 spatial expression")
    ax.set_xlabel("slice x")
    ax.set_ylabel("slice y")
    ax.set_aspect("equal", adjustable="box")
    ax.invert_yaxis()
    fig.colorbar(scatter, ax=ax, label="UMI count")
    fig.savefig(FIGURE, dpi=180)
    plt.close(fig)

    print(f"表达行数：{len(expression)}")
    print(f"细胞数：{len(metadata)}")
    print(f"合并后 Gad1 细胞数：{len(merged)}")
    print(f"图：{FIGURE}")
    print(f"表：{TABLE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
