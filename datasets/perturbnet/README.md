# PerturbNet Data

为 PerturbNet 论文建立的结构规范的 GitHub 数据项目。

> **论文**: https://doi.org/10.1038/s44320-025-00131-3
> **官方代码**: https://github.com/welch-lab/PerturbNet
> **作者整理的数据和模型**: https://huggingface.co/cyclopeta/PerturbNet_reproduce

**目标**: 保存 PerturbNet 使用的数据目录、访问链接、下载脚本、数据字典、小型示例数据和查看代码。不把大型原始数据直接提交到普通 Git 历史。

## 项目结构

```
PerturbNet-data/
├── README.md
├── LICENSE
├── CITATION.cff
├── .gitignore
├── metadata/
│   ├── dataset_catalog.csv    # 数据目录
│   ├── accession_manifest.tsv # accession 清单
│   ├── file_manifest.csv      # Hugging Face 文件清单
│   └── data_dictionary.md     # 数据字典
├── data/
│   ├── README.md
│   ├── example/        # 小型教程数据
│   ├── processed/      # 处理后数据
│   ├── raw/            # 原始数据
│   ├── model_weights/  # 模型权重
│   └── source_data/    # 论文图表源数据
├── scripts/
│   ├── inspect_huggingface.py   # 检查 HF 仓库
│   ├── download_huggingface.py  # 下载 HF 文件
│   ├── download_geo.py          # 下载 GEO 数据
│   ├── inspect_h5ad.py          # 检查 h5ad
│   ├── inspect_expression_data.py # 检查表达数据
│   └── verify_checksums.py      # 校验
└── notebooks/
    ├── 01_inspect_example_data.ipynb
    ├── 02_inspect_perturbation_matrix.ipynb
    └── 03_compare_real_and_generated_cells.ipynb
```

## 数据分类

### A. 扰动编码器预训练数据

| 数据 | 用途 | 链接 |
|------|------|------|
| ZINC | 预训练 ChemicalVAE，学习 SMILES 药物结构嵌入 | https://zinc15.docking.org/ |
| Gene Ontology | 构建 15988 维基因功能向量，训练 GenotypeVAE | https://geneontology.org/ |
| UniParc/ESM | 预训练 ESM，用蛋白质序列表示编码突变 | https://www.uniprot.org/uniparc |

### B. 药物扰动数据

| 数据 | 规模 | 用途 | 链接 |
|------|------|------|------|
| LINCS-Drug | 677159 表达测量、170 细胞系、19990 化合物 | 训练和评估未见药物响应 | https://clue.io/data |
| sci-Plex (GSE139944) | 648857 细胞、3 细胞系、180 药物 | 药物扰动后单细胞表达分布预测 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE139944 |

### C. CRISPR 基因扰动数据

| 数据 | 规模 | 用途 | 链接 |
|------|------|------|------|
| Norman CRISPRa (GSE133344) | 109738 K562 细胞、2279 基因、230 扰动 | 预测未见单基因和双基因扰动 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE133344 |

### D. 蛋白质突变数据

| 数据 | 规模 | 用途 | 链接 |
|------|------|------|------|
| Ursu TP53/KRAS (GSE161824) | 162532 A549 细胞、1629 基因、163 蛋白质序列 | 预测未见 TP53 和 KRAS 编码突变 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE161824 |
| Jorge GATA1 (GSE215253) | 142872 HSPC、2477 基因、257 GATA1 序列 | 预测未见 GATA1 突变及全部单氨基酸替换 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE215253 |

### E. 作者处理后的数据和模型 (Hugging Face)

https://huggingface.co/cyclopeta/PerturbNet_reproduce

目录包括:
- `data_paper` — 论文使用的数据
- `example_data` — 小型教程数据
- `models` — 模型
- `pretrained_model` — 预训练模型

### F. 论文图表源数据

BioStudies: S-SCDT-10_1038-S44320-025-00131-3
https://www.ebi.ac.uk/biostudies/studies/S-SCDT-10_1038-S44320-025-00131-3

## 三个任务的输入输出

### 药物扰动
**输入**: SMILES + 剂量 + 细胞背景 + 噪声
**输出**: 扰动后单细胞表达矩阵

### 基因扰动
**输入**: GO 功能向量 + 细胞背景 + 噪声
**输出**: 扰动后单细胞表达矩阵

### 蛋白质突变
**输入**: 氨基酸序列嵌入 + 细胞背景 + 噪声
**输出**: 扰动后单细胞表达矩阵

## 快速开始

```bash
# 1. 检查 Hugging Face 仓库文件清单
python scripts/inspect_huggingface.py

# 2. 第一阶段: 下载小型教程数据
python scripts/download_huggingface.py --phase 1

# 3. 检查示例数据
python scripts/inspect_h5ad.py data/example/<file>.h5ad

# 4. 查看 notebook
jupyter notebook notebooks/01_inspect_example_data.ipynb
```

## 下载阶段

### 第一阶段 (默认)
- example_data 中的小型教程数据
- README 和配置文件
- 必要的数据字典
- 小型模型配置
- BioStudies 中的补充表格和小型源数据

### 第二阶段 (根据空间决定)
- data_paper
- models
- pretrained_model
- GEO 原始数据

没有用户确认不自动下载全部大型文件。

## 大型文件管理

- `data/raw/`、`data/processed/`、`data/model_weights/` 全部加入 `.gitignore`
- 普通 GitHub 只保存: 下载脚本、数据链接和 accession、文件清单、数据字典、小型 example 数据、notebook、校验值
- 不直接提交数 GB 的表达矩阵和模型权重
- 如确实需要远程版本管理，先评估 Git LFS 或 DVC，并报告预计存储量和带宽成本

## 许可证

本项目代码仅供学术研究使用。数据版权归原始作者所有。
