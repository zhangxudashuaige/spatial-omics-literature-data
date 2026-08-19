"""确定性生成五个项目 Notebook。"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks"


def md(text: str) -> dict:
    cell_id = hashlib.sha1(("markdown\n" + text).encode()).hexdigest()[:12]
    return {"cell_type": "markdown", "id": cell_id, "metadata": {}, "source": text.splitlines(keepends=True)}


def code(text: str) -> dict:
    cell_id = hashlib.sha1(("code\n" + text).encode()).hexdigest()[:12]
    return {
        "cell_type": "code", "id": cell_id, "execution_count": None, "metadata": {},
        "outputs": [], "source": text.splitlines(keepends=True),
    }


def notebook(cells: list[dict]) -> dict:
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4, "nbformat_minor": 5,
    }


SETUP = """from pathlib import Path
import sys
ROOT = Path.cwd()
if ROOT.name == 'notebooks':
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from create_sample_data import synthetic
from h5ad_utils import choose_h5ad
synthetic_path = ROOT / 'data' / 'processed' / 'synthetic_test.h5ad'
if not list((ROOT / 'data' / 'external' / 'GSE278603' / 'h5ad').glob('*.h5ad')):
    synthetic(synthetic_path)
H5AD = choose_h5ad(ROOT)
IS_SYNTHETIC = H5AD.name == 'synthetic_test.h5ad'
print('数据文件：', H5AD)
print('注意：' if IS_SYNTHETIC else '状态：', '当前使用完全合成测试数据' if IS_SYNTHETIC else '当前使用真实 GEO 数据')
"""


NOTEBOOKS = {
    "01_data_inventory.ipynb": [
        md("# 01 数据清单\n\n展示六个官方样本的阶段、重复、文件大小和下载状态。"),
        code("""from pathlib import Path
import pandas as pd
ROOT = Path.cwd()
if ROOT.name == 'notebooks': ROOT = ROOT.parent
manifest = pd.read_csv(ROOT / 'metadata' / 'sample_manifest.csv')
manifest[['gsm_accession','stage','replicate','file_name','reported_size','download_status']]
"""),
        code("""manifest.assign(reported_mb=manifest['reported_size'].str.extract(r'([0-9.]+)')[0].astype(float)).groupby('stage', sort=False).agg(samples=('gsm_accession','count'), reported_mb=('reported_mb','sum'))
"""),
    ],
    "02_inspect_h5ad.ipynb": [
        md("# 02 检查 H5AD\n\n`X` 是主表达矩阵；`obs` 是观测元数据；`var` 是基因元数据；`obsm` 存放多维坐标；`uns` 是非结构化信息；`layers` 保存其他表达层。真实数据用 `backed='r'` 打开。"),
        code(SETUP),
        code("""import anndata as ad
adata = ad.read_h5ad(H5AD, backed='r')
summary = {
    'shape': adata.shape,
    'X_type': type(adata.X).__name__,
    'X_dtype': str(getattr(adata.X, 'dtype', 'unknown')),
    'obs': list(adata.obs.columns),
    'var': list(adata.var.columns),
    'obsm': list(adata.obsm.keys()),
    'uns': list(adata.uns.keys()),
    'layers': list(adata.layers.keys()),
    'raw': adata.raw is not None,
    'obs_names': list(map(str, adata.obs_names[:5])),
    'var_names': list(map(str, adata.var_names[:5])),
}
summary
"""),
        code("adata.file.close()"),
    ],
    "03_visualize_spatial_coordinates.ipynb": [
        md("# 03 空间坐标可视化\n\n自动搜索坐标，不假定键名。"),
        code(SETUP),
        code("""import anndata as ad
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei','SimHei','DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
from h5ad_utils import select_coordinates
adata = ad.read_h5ad(H5AD, backed='r')
coords, source = select_coordinates(adata, 2)
plt.figure(figsize=(7,5.5))
plt.scatter(coords[:,0], coords[:,1], s=5, alpha=.7)
plt.gca().set_aspect('equal')
plt.title(('合成测试：' if IS_SYNTHETIC else '') + f'空间坐标 {source}')
plt.xlabel('x'); plt.ylabel('y'); plt.tight_layout()
out = ROOT / 'results' / 'figures' / 'notebook_spatial_coordinates.png'
plt.savefig(out, dpi=180); plt.show()
adata.file.close()
out
"""),
    ],
    "04_visualize_marker_expression.ipynb": [
        md("# 04 Marker 空间表达\n\n依次检查 Myl7、Tnnt2、Mef2c、Shh、Cer1、Apela，只绘制真实存在的基因。"),
        code(SETUP),
        code("""import anndata as ad
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei','SimHei','DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
from h5ad_utils import gene_vector, select_coordinates
markers = ['Myl7','Tnnt2','Mef2c','Shh','Cer1','Apela']
adata = ad.read_h5ad(H5AD, backed='r')
coords, source = select_coordinates(adata, 2)
available = [g for g in markers if g in adata.var_names]
if not available:
    raise KeyError('六个候选 marker 均不在 var_names；请检查基因标识类型')
fig, axes = plt.subplots(2, 3, figsize=(13,8), constrained_layout=True)
for ax, gene in zip(axes.flat, available):
    values = gene_vector(adata, gene)
    p = ax.scatter(coords[:,0], coords[:,1], c=values, s=4, cmap='magma')
    ax.set_title(gene); ax.set_aspect('equal'); fig.colorbar(p, ax=ax, shrink=.7)
for ax in axes.flat[len(available):]: ax.axis('off')
fig.suptitle(('合成测试：' if IS_SYNTHETIC else '') + 'Marker 空间表达')
out = ROOT / 'results' / 'figures' / 'notebook_marker_expression.png'
fig.savefig(out, dpi=180); plt.show()
adata.file.close()
out
"""),
    ],
    "05_compare_developmental_stages.ipynb": [
        md("# 05 发育阶段比较\n\n比较 E7.5、E7.75 和 E8.0。真实文件下载后逐样本读取；无真实文件时仅验证代码流程。"),
        code(SETUP),
        code("""import anndata as ad
import pandas as pd
files = sorted((ROOT / 'data' / 'external' / 'GSE278603' / 'h5ad').glob('*.h5ad')) or [H5AD]
rows = []
for path in files:
    a = ad.read_h5ad(path, backed='r')
    if 'stage' in a.obs:
        for stage, count in a.obs['stage'].astype(str).value_counts().items():
            rows.append({'file':path.name,'stage':stage,'n_obs':int(count),'n_vars':a.n_vars})
    else:
        stage = next((s for s in ['E7.75','E7.5','E8.0'] if s in path.name), '字段待确认')
        rows.append({'file':path.name,'stage':stage,'n_obs':a.n_obs,'n_vars':a.n_vars})
    a.file.close()
comparison = pd.DataFrame(rows)
comparison
"""),
        code("""import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei','SimHei','DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
summary = comparison.groupby('stage', sort=False)['n_obs'].sum()
ax = summary.plot.bar(figsize=(7,4), color='#4C78A8')
ax.set_ylabel('观测数量'); ax.set_title(('合成测试：' if IS_SYNTHETIC else '') + '各发育阶段观测数')
plt.tight_layout()
out = ROOT / 'results' / 'figures' / 'notebook_stage_comparison.png'
plt.savefig(out, dpi=180); plt.show()
comparison.to_csv(ROOT / 'results' / 'tables' / 'stage_comparison.csv', index=False)
out
"""),
    ],
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, cells in NOTEBOOKS.items():
        (OUT / name).write_text(json.dumps(notebook(cells), ensure_ascii=False, indent=1), encoding="utf-8")
        print(OUT / name)


if __name__ == "__main__":
    main()
