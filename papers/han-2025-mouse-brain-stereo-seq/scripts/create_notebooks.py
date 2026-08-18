"""确定性生成本目录的五个教学 Notebook。"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks"


def markdown(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def notebook(title: str, description: str, cells: list[dict]) -> dict:
    return {
        "cells": [
            markdown(f"# {title}\n\n{description}\n\n> 本 Notebook 默认使用合成测试数据，不代表论文真实数值。"),
            code(
                "from pathlib import Path\n"
                "ROOT = Path.cwd().resolve()\n"
                "if ROOT.name == 'notebooks':\n"
                "    ROOT = ROOT.parent\n"
                "SAMPLE = ROOT / 'data' / 'sample'\n"
                "RESULTS = ROOT / 'results'\n"
                "print('项目目录:', ROOT)\n"
            ),
            *cells,
        ],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


NOTEBOOKS = {
    "01_inspect_spatial_matrix.ipynb": notebook(
        "01 检查空间表达矩阵",
        "读取 cell × gene 长表，检查维度、基因和 UMI 分布。",
        [
            code("import pandas as pd\nexpression = pd.read_csv(SAMPLE / 'sample_spatial_expression.csv')\nexpression.head()\n"),
            code("summary = {\n    'rows': len(expression),\n    'cells': expression['cell_id'].nunique(),\n    'genes': expression['gene'].nunique(),\n    'total_umi': int(expression['umi_count'].sum()),\n}\nsummary\n"),
            code("matrix = expression.pivot(index='cell_id', columns='gene', values='umi_count').fillna(0)\nmatrix\n"),
        ],
    ),
    "02_inspect_cell_metadata.ipynb": notebook(
        "02 检查细胞元数据",
        "查看细胞类型、脑区、切片以及二维/三维坐标字段。",
        [
            code("import pandas as pd\nmetadata = pd.read_csv(SAMPLE / 'sample_cell_metadata.csv')\nmetadata.head()\n"),
            code("metadata[['cell_cluster','cell_subclass','cell_class','brain_region']].nunique()\n"),
            code("metadata.groupby(['cell_class','brain_region'], dropna=False).size().rename('cell_count').reset_index()\n"),
            code("assert metadata['cell_id'].is_unique\nassert metadata[['x','y','ccf_x','ccf_y','ccf_z']].notna().all().all()\nprint('字段和主键检查通过')\n"),
        ],
    ),
    "03_visualize_spatial_coordinates.ipynb": notebook(
        "03 可视化二维空间基因表达",
        "按 cell_id 合并 Gad1 表达与二维坐标，并保存空间散点图。",
        [
            code("import matplotlib.pyplot as plt\nimport pandas as pd\nexpression = pd.read_csv(SAMPLE / 'sample_spatial_expression.csv')\nmetadata = pd.read_csv(SAMPLE / 'sample_cell_metadata.csv')\ngad1 = expression.query(\"gene == 'Gad1'\")[[\"cell_id\",\"umi_count\"]]\nplot_data = metadata.merge(gad1, on='cell_id', validate='one_to_one')\nplot_data.head()\n"),
            code("out = RESULTS / 'figures' / 'notebook_Gad1_spatial_expression.png'\nout.parent.mkdir(parents=True, exist_ok=True)\nfig, ax = plt.subplots(figsize=(7,5))\nsc = ax.scatter(plot_data.x, plot_data.y, c=plot_data.umi_count, s=90, cmap='viridis', edgecolor='white')\nax.set(title='Synthetic sample: Gad1 spatial expression', xlabel='slice x', ylabel='slice y')\nax.invert_yaxis(); ax.set_aspect('equal', adjustable='box')\nfig.colorbar(sc, ax=ax, label='UMI count')\nfig.tight_layout(); fig.savefig(out, dpi=180); plt.show()\nprint(out)\n"),
        ],
    ),
    "04_compare_snRNAseq_and_stereoseq.ipynb": notebook(
        "04 比较 snRNA-seq 与 Stereo-seq",
        "把 Stereo-seq 按 cluster 聚合后，与合成 snRNA-seq cluster 参考表达比较。",
        [
            code("import matplotlib.pyplot as plt\nimport pandas as pd\nexpression = pd.read_csv(SAMPLE / 'sample_spatial_expression.csv')\nmetadata = pd.read_csv(SAMPLE / 'sample_cell_metadata.csv')[['cell_id','cell_cluster']]\nreference = pd.read_csv(SAMPLE / 'sample_snrna_reference.csv')\nspatial = expression.merge(metadata, on='cell_id').groupby(['cell_cluster','gene'], as_index=False)['umi_count'].mean()\ncomparison = spatial.merge(reference, on=['cell_cluster','gene'], how='inner')\ncomparison\n"),
            code("fig, ax = plt.subplots(figsize=(6,5))\nfor gene, group in comparison.groupby('gene'):\n    ax.scatter(group.mean_expression, group.umi_count, label=gene, s=60)\nax.set(xlabel='snRNA-seq mean expression (synthetic)', ylabel='Stereo-seq mean UMI (synthetic)', title='Cluster-level comparison')\nax.legend(); fig.tight_layout(); plt.show()\n"),
        ],
    ),
    "05_visualize_3d_ccf_coordinates.ipynb": notebook(
        "05 可视化 CCF 三维坐标",
        "用合成 CCF 坐标展示三维散点；真实 CCF 文件取得后可替换输入。",
        [
            code("import matplotlib.pyplot as plt\nimport pandas as pd\nmetadata = pd.read_csv(SAMPLE / 'sample_cell_metadata.csv')\n"),
            code("fig = plt.figure(figsize=(8,6))\nax = fig.add_subplot(111, projection='3d')\nfor region, group in metadata.groupby('brain_region'):\n    ax.scatter(group.ccf_x, group.ccf_y, group.ccf_z, label=region, s=45)\nax.set(xlabel='CCF x', ylabel='CCF y', zlabel='CCF z', title='Synthetic CCF coordinates')\nax.legend(bbox_to_anchor=(1.04,1), loc='upper left', fontsize=8)\nfig.tight_layout(); plt.show()\n"),
        ],
    ),
}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, payload in NOTEBOOKS.items():
        (OUT / name).write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"已生成：{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
