# X-Cell 数据资源

整理 X-Cell 论文的数据、外部评测集和生物先验。

> **论文**: https://doi.org/10.64898/2026.03.18.712807
> **官方代码**: https://github.com/Xaira-Therapeutics/X-Cell
> **官方模型**: https://huggingface.co/Xaira-Therapeutics/X-Cell
> **官方训练数据**: https://huggingface.co/datasets/Xaira-Therapeutics/X-Atlas-Pisces

## 重要声明

**截至当前官方页面，X-Cell 权重、完整推理代码和完整 X-Atlas/Pisces 数据仍标注 Coming Soon。**

- 不伪造下载成功
- 不创建假的 .h5ad 文件
- 不把只有 24.3 kB 的说明文件误认为 2560 万细胞数据
- 项目记录资源状态，并提供将来数据公开后可以运行的下载脚本

**当前项目首先是数据目录、下载器和检查工具，不宣称已经复现 X-Cell。** 官方完整数据、权重和推理实现发布后，再更新下载和运行流程。

## 目录结构

```
xcell/
├── README.md
├── RESOURCE_STATUS.md          # 资源公开状态（由脚本自动生成）
├── DATA_LICENSES.md            # 各资源许可证
├── requirements.txt
├── .gitignore
├── manifests/
│   ├── xatlas_pisces.json      # 核心训练数据清单
│   ├── evaluation_datasets.json # 外部评测数据清单
│   └── biological_priors.json   # 生物先验清单
├── data/
│   ├── xatlas_pisces/          # 核心训练数据（Coming Soon）
│   ├── evaluation/              # 外部评测数据
│   │   ├── replogle_nadig/
│   │   ├── parse_1m/
│   │   ├── tahoe_100m/
│   │   ├── melanocyte_progenitor/
│   │   └── primary_t_cells/
│   └── priors/                  # 生物先验
│       ├── genept/
│       ├── esm2/
│       ├── string/
│       ├── depmap/
│       ├── cell_painting/
│       └── scgpt/
├── scripts/
│   ├── check_resource_status.py    # 检查官方资源公开状态
│   ├── download_public_resources.py # 下载已公开资源
│   ├── inspect_h5ad.py             # 检查 h5ad 数据
│   ├── inspect_prior_embeddings.py # 检查先验嵌入
│   └── make_small_example.py       # 从真实数据抽取小样本
└── notebooks/
    └── inspect_xcell_data.ipynb
```

## 资源分类

### A. 核心训练数据 — X-Atlas/Pisces

| 项目 | 内容 |
|------|------|
| 规模 | 25.6M 细胞 |
| CRISPRi screen | 7 个 |
| 细胞背景 | 16 种 |
| 细胞系 | HCT116、HEK293T、HepG2、iPSC、Jurkat Resting、Jurkat Active、iPSC Multi-Diff |
| 状态 | **Coming Soon** |
| 链接 | https://huggingface.co/datasets/Xaira-Therapeutics/X-Atlas-Pisces |

### B. 外部评测数据

| 数据集 | 链接 | 状态 |
|--------|------|------|
| Replogle-Nadig | https://huggingface.co/datasets/arcinstitute/Replogle-Nadig-Preprint | 可下载 |
| Parse-1M | https://huggingface.co/datasets/arcinstitute/State-Parse-Filtered | 可下载 |
| Tahoe-100M 子集 | https://huggingface.co/datasets/tahoe-bio/Tahoe-100M | 可下载 |
| melanocyte progenitor | 待确认 | 待确认 |
| primary human CD4+ T cells | 待确认 | 待确认 |

### C. 生物先验

| 先验 | 链接 | 状态 |
|------|------|------|
| GenePT | https://zenodo.org/records/10833191 | 可下载 |
| ESM-2 | https://github.com/facebookresearch/esm | 可下载 |
| STRING | https://stringdb-downloads.org/download/protein.network.embeddings.v12.0.h5 | 可下载 |
| DepMap 24Q4 | https://plus.figshare.com/articles/dataset/DepMap_24Q4_Public/27993248 | 可下载 |
| JUMP Cell Painting | https://jump-cellpainting.broadinstitute.org/ | 可下载 |
| scGPT | https://github.com/bowang-lab/scGPT | 可下载 |

### D. 模型资源

| 模型 | 参数 | 状态 |
|------|------|------|
| X-Cell Mini | 55M | **Coming Soon** |
| X-Cell Ultra | 4.87B | **Coming Soon** |
| 链接 | https://huggingface.co/Xaira-Therapeutics/X-Cell | |

## 快速开始

```bash
# 1. 检查资源公开状态（自动更新 RESOURCE_STATUS.md）
python scripts/check_resource_status.py

# 2. 下载已公开的外部资源（不下载 Coming Soon 的 X-Atlas/Pisces）
python scripts/download_public_resources.py

# 3. 检查 h5ad 数据（数据可用时）
python scripts/inspect_h5ad.py --file data/evaluation/replogle_nadig/example.h5ad

# 4. 检查先验嵌入
python scripts/inspect_prior_embeddings.py --prior genept

# 5. 从真实数据抽取小样本（原始数据可用时）
python scripts/make_small_example.py

# 6. 查看数据
jupyter notebook notebooks/inspect_xcell_data.ipynb
```

## 大型数据处理规则

- `.h5ad`、`.h5`、`.parquet`、`.zarr`、`.loom`、`.safetensors`、`.bin`、`.pt`、`.ckpt` 全部加入 `.gitignore`
- `data/**` 全部排除，只保留 `.gitkeep`
- GitHub 只保存代码、元数据、下载脚本和小型示例
- 大型文件使用 DVC 或 Git LFS
- 不要把无法确认来源的第三方处理数据上传 GitHub

## 许可证

详见 [DATA_LICENSES.md](DATA_LICENSES.md)。

- X-Cell 项目和模型页面标注 **CC BY-NC-SA 4.0**
- 每个外部数据和先验保留自身许可证
- 不统一改成 MIT
- 如果某资源许可证不明确，标记为"需要人工确认"
