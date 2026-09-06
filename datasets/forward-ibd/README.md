# FORWARD-IBD 数据项目

整理并提供下载、检查和预处理 FORWARD 论文所使用的 IBD 转录组、治疗响应及临床试验靶点数据的工具。

> **论文**: https://doi.org/10.1101/2024.07.16.602603
> **标题**: FORWARD: A Learning Framework for Logical Network Perturbations to Prioritize Targets for Drug Development

**重要声明：论文 v2 没有公开可验证的完整 FORWARD 代码、TI 公式和全部补充表。**

- Supplemental Dataset 1–3 需要从论文补充材料单独取得
- 当前仓库首先是**"数据索引与预处理项目"**，不是完整模型复现
- 不声称已经复现 FORWARD

## 目录结构

```
forward-ibd/
├── README.md
├── environment.yml
├── requirements.txt
├── .gitignore
├── LICENSE
├── data_manifest/
│   ├── training_cohorts.csv        # 34基因签名训练数据（7个队列）
│   ├── validation_cohorts.csv      # 独立验证数据（9个队列）
│   ├── boolean_network_cohorts.csv  # 原始IBD布尔网络训练数据（3个队列）
│   ├── clinical_trial_sources.csv   # 临床试验和药物靶点数据
│   └── data_dictionary.md
├── data/
│   ├── raw/            # 原始数据（不提交Git）
│   ├── processed/      # 处理后数据（不提交Git）
│   ├── metadata/       # 元数据
│   └── examples/       # 小型示例
├── scripts/
│   ├── download_geo.py
│   ├── download_arrayexpress.py
│   ├── inspect_datasets.py
│   ├── extract_sample_metadata.py
│   ├── check_sample_overlap.py
│   └── harmonize_gene_ids.py
├── notebooks/
│   ├── 01_download_and_inspect.ipynb
│   ├── 02_sample_metadata.ipynb
│   ├── 03_expression_matrix_qc.ipynb
│   └── 04_overlap_check.ipynb
└── results/
    ├── dataset_summary.csv
    └── figures/
```

## 数据分类

### A. 34基因签名训练数据（7个队列）

| dataset_id | n | 治疗 | 来源 |
|------------|---|------|------|
| GSE12251 | 23 | Infliximab | GEO |
| GSE16879 | 61 | Infliximab | GEO |
| GSE14580 | 24 | Infliximab | GEO |
| GSE73661 | 23 | Infliximab | GEO |
| GSE207022 | 101 | Ustekinumab | GEO |
| E-MTAB-7604 | 43 | Infliximab/Adalimumab | ArrayExpress |
| GSE234736 | 47 | Vedolizumab | GEO |

### B. 独立验证数据（9个队列）

GSE23597、GSE115390、GSE73661、GSE49858、GSE59071、GSE37283、GSE83687、GSE20881、GSE193677

### C. 原始IBD布尔网络数据（3个队列）

GSE83687、GSE73661、GSE6731

### D. 临床试验和药物靶点数据

详见 `data_manifest/clinical_trial_sources.csv`

### E. 论文产生的派生数据

Supplemental Dataset 1–3 需从论文补充材料单独取得，当前仓库不包含。

## 快速开始

```bash
# 1. 安装依赖
conda env create -f environment.yml
conda activate forward-ibd

# 2. 下载GEO元数据和处理后文件（不下载大型原始数据）
python scripts/download_geo.py --gse GSE12251 --metadata-only

# 3. 下载ArrayExpress数据（E-MTAB-7604）
python scripts/download_arrayexpress.py --accession E-MTAB-7604

# 4. 检查数据集
python scripts/inspect_datasets.py

# 5. 检查样本重叠（特别检查GSE12251与GSE23597、GSE14580与GSE16879）
python scripts/check_sample_overlap.py

# 6. 查看notebook
jupyter notebook notebooks/
```

## 重复样本检查

特别检查以下可能存在重复样本的队列对：

- **GSE12251 与 GSE23597**：优先比较 GSM 编号；必要时比较表达矩阵相关性或哈希
- **GSE14580 与 GSE16879**：优先比较 GSM 编号；必要时比较表达矩阵相关性或哈希

## 大型数据处理规则

- `data/raw/`、大型表达矩阵、压缩文件和患者级原始数据写入 `.gitignore`，不直接提交 GitHub
- 下载脚本默认只下载元数据和 processed/supplementary 文件，不自动下载全部大型原始数据
- 如确实需要版本管理大型数据，优先使用 DVC，不默认使用 Git LFS 上传全部公开数据
- 原始大文件保留在 GEO、ArrayExpress/EMBL-EBI BioStudies

## 已知限制

- 论文 v2 没有公开可验证的完整 FORWARD 代码
- TI（Topological Impact）公式未完全公开
- Supplemental Dataset 1–3 需要从论文补充材料单独取得
- 部分队列的治疗响应标签可能不完整或格式不一致
- 基因标识类型可能混合（Gene Symbol、Entrez ID、Ensembl ID），需用 `harmonize_gene_ids.py` 统一
