# 数据目录

存放 PerturbNet 项目的所有数据文件。

**重要：大型原始数据和模型权重不直接提交到普通 Git 历史。data/raw/、data/processed/、data/model_weights/ 已加入 .gitignore。**

## 目录结构

- `example/` — 小型教程数据 (第一阶段下载，可进 Git)
- `raw/` — 从 GEO 等来源下载的原始数据 (不进 Git)
- `processed/` — 处理后的数据，包括 Hugging Face data_paper (不进 Git)
- `model_weights/` — 模型权重，包括 models 和 pretrained_model (不进 Git)
- `source_data/` — 论文图表源数据 (BioStudies)

## 如何获取数据

### 第一阶段 (推荐首先执行)
```bash
# 1. 检查 Hugging Face 仓库文件清单
python scripts/inspect_huggingface.py

# 2. 下载小型教程数据
python scripts/download_huggingface.py --phase 1
```

### 第二阶段 (根据磁盘空间决定)
```bash
# 下载 data_paper、models、pretrained_model
python scripts/download_huggingface.py --phase 2
```

### GEO 原始数据
```bash
# 列出数据集信息
python scripts/download_geo.py --gse GSE133344 --list
# 实际下载需从 GEO 页面获取链接
```

## 数据来源

| 类型 | 来源 | 链接 |
|------|------|------|
| 作者处理后数据 | Hugging Face | https://huggingface.co/cyclopeta/PerturbNet_reproduce |
| 药物扰动 | GEO GSE139944 | sci-Plex |
| 基因扰动 | GEO GSE133344 | Norman CRISPRa |
| 蛋白质突变 | GEO GSE161824, GSE215253 | Ursu TP53/KRAS, Jorge GATA1 |
| 预训练数据 | ZINC, GO, UniParc | 见 dataset_catalog.csv |
| 源数据 | BioStudies | S-SCDT-10_1038-S44320-025-00131-3 |

## 大文件规则

- `.h5ad`、`.h5`、`.pt`、`.pth`、`.safetensors`、`.npy`、`.npz` 不进入普通 Git
- 已通过 `.gitignore` 排除
- 如需版本管理，使用 Git LFS 或 DVC
- 不直接提交数 GB 的表达矩阵和模型权重
