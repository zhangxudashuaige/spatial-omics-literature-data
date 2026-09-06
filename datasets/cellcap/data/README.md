# 数据目录

本目录存放 CellCap 项目的所有数据文件。

**重要：大型数据文件不提交到普通 Git 历史。**

## 目录结构

- `raw/` — 从官方来源下载的原始文件，禁止修改
  - `simulation_data.h5ad` — CellCap 模拟数据
  - `CellCap_1MPBMC_Mono.h5ad` — 人单核细胞数据
- `processed/` — 我们处理生成的文件
  - `norman_crispra.h5ad` — Norman 2019 整理后的 AnnData

## 如何获取数据

1. **模拟数据**: 运行 `python scripts/download_simulation_data.py`
2. **Norman 数据**: 运行 `python scripts/download_norman_geo.py`，然后 `python scripts/prepare_norman_anndata.py`
3. **单核细胞数据**: 从官方 CellCap 仓库或配套资源获取（可能需要 Git LFS）

## 大文件规则

- `.h5ad`、`.h5`、`.mtx`、`.fastq.gz`、`.pt` 不进入普通 Git
- 已通过 `.gitignore` 排除
- 如需版本管理，使用 Git LFS 或 DVC
