# 数据目录

存放 GEARS 项目的所有数据文件。

**重要：大型数据文件不提交到普通 Git 历史。**

## 目录结构

- `raw/` — 从 GEO 等来源下载的原始文件
- `processed/` — GEARS 官方预处理后的数据（PertData 自动下载）
  - `norman/` — Norman 2019
  - `adamson/` — Adamson 2016
  - `dixit/` — Dixit 2016
- `external/gene_ontology/` — Gene Ontology OBO 和 GAF 注释文件

## 如何获取数据

### GEARS 官方预处理数据（推荐）
```bash
python scripts/download_gears_processed.py --dataset norman
python scripts/download_gears_processed.py --dataset adamson
python scripts/download_gears_processed.py --dataset dixit
```

### 从 GEO 下载原始数据
```bash
python scripts/download_geo.py --gse GSE133344 --list
```

### Gene Ontology 数据
```bash
# OBO 文件由 build_go_graph.py 自动下载
# GAF 注释文件需从 http://current.geneontology.org/products/pages/downloads.html 手动下载
```

## 大文件规则

- `.h5ad`、`.h5`、`.mtx`、`.fastq.gz` 不进入普通 Git
- 已通过 `.gitignore` 排除
- 如需版本管理，使用 Git LFS 或 DVC
