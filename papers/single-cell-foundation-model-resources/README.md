# 单细胞基础语言模型资源目录（ACL 2025）

本目录整理 ACL 2025 综述 **A Survey on Foundation Language Models for Single-cell Biology** 中涉及的预训练语料、下游数据、数据平台和模型仓库，并补充每个下游数据集的原始论文或“无独立数据论文”说明。

- 综述主页：https://aclanthology.org/2025.acl-long.26/
- DOI：https://doi.org/10.18653/v1/2025.acl-long.26
- 本项目是整个 `spatial-omics-literature-data` 综合仓库的一部分，不是另一个独立仓库。

## 最重要的概念

这篇综述**没有发布一个新的统一单细胞数据集**。它比较的是不同模型各自使用的资料：

1. `pretraining_corpus`：训练基础模型的海量细胞语料。
2. `downstream_benchmark`：做注释、扰动、空间、多组学、药物反应等实验的数据。
3. `data_platform`：用于搜索和下载许多研究的网站，本身不是一个实验数据集。
4. `model_repository`：模型代码、权重、安装文档，不是数据平台。

预训练语料可达上亿细胞，普通 GitHub 不适合保存完整矩阵、原始测序或模型权重。因此这里保存的是经过核验的目录、来源论文、官方链接、访问状态、脚本和统计 Notebook；大型文件仍从原始平台下载到本地。

## 已整理内容

| 类别 | 文件 | 条目数 | 作用 |
|---|---|---:|---|
| 预训练语料 | [`metadata/pretraining_corpora.csv`](metadata/pretraining_corpora.csv) | 15 | 历史语料规模、当前规模、来源和公开程度 |
| 下游数据 | [`metadata/downstream_datasets.csv`](metadata/downstream_datasets.csv) | 38 | 数据任务、accession、官方入口、原始论文 |
| 原始论文 | [`metadata/original_papers.csv`](metadata/original_papers.csv) | 31 | 可唯一追溯的下游数据来源论文及论文—数据关系 |
| 数据平台 | [`metadata/data_platforms.csv`](metadata/data_platforms.csv) | 9 | 平台用途、API、登录和访问限制 |
| 模型仓库 | [`metadata/model_repositories.csv`](metadata/model_repositories.csv) | 22 | 官方仓库、论文、权重、许可和安装状态 |
| 模型—数据关系 | [`metadata/task_model_matrix.csv`](metadata/task_model_matrix.csv) | 74 | 哪个模型如何使用哪个语料或数据集 |

<!-- GENERATED_SUMMARY_START -->
当前目录包含 **15** 个预训练语料、**38** 个唯一的下游数据集、**31** 篇下游数据原始论文、**9** 个数据平台、**22** 个模型（其中 **20** 个确认官方仓库）和 **74** 条模型—数据—任务关系。完整自动表格见 [`docs/resource_tables.md`](docs/resource_tables.md)。
<!-- GENERATED_SUMMARY_END -->

## “原始论文”是怎么记录的

`downstream_datasets.csv` 中新增了：

- `original_paper_id`
- `original_paper_title`
- `original_paper_doi`
- `original_paper_url`

如果数据来自正式研究，这些字段指向产生数据或首次系统发表数据的论文。如果条目是 10x Genomics、Vizgen 等厂商公开示例，且没有独立数据论文，则明确写为 `no independent dataset paper`，不会拿平台方法论文冒充数据论文。若综述只写了技术类别（例如“CyTOF data”）而没有唯一 accession，也会明确标记 `not uniquely specified by survey`。

31 篇可唯一定位的来源论文同时保存为 [`paper_records/`](paper_records/) 下的独立中文条目，并登记在全库 `catalog/papers.csv`。每个条目记录论文元数据、官方入口、关联数据和 PDF 保存状态。另有 6 个厂商示例数据没有独立数据论文，项目保留官方数据页并明确说明，不虚构论文。

## 怎么查和下载

### 1. 先查目录

```powershell
cd "C:\Users\l\Documents\Codex\2026-08-15\github\spatial-omics-literature-data\papers\single-cell-foundation-model-resources"

# 查某模型用过哪些数据
Select-String -Path .\metadata\task_model_matrix.csv -Pattern "scGPT"

# 查所有可直接下载的下游数据
Import-Csv .\metadata\downstream_datasets.csv |
  Where-Object { $_.access_type -eq "direct" } |
  Select-Object dataset_name, accession, official_url
```

### 2. 检查链接，不下载大文件

```powershell
python .\scripts\check_urls.py --timeout 20
```

输出写入 `results/url_check.csv`。`403` 会记为 `access_restricted`，不会被错误判断为链接失效。

### 3. 下载时使用 CSV 中的官方入口

这里没有“一键下载所有数据”的脚本，因为来源横跨 GEO、CELLxGENE、HCA、10x、Zenodo、ImmPort 等平台，许可和登录条件不同。下载前请阅读 [`docs/data_access_guide.md`](docs/data_access_guide.md)，并把文件保存到：

```text
data/external/<dataset_id>/
```

该目录被 `.gitignore` 排除，不会误上传 GitHub。

### 4. 检查本地 H5AD

```powershell
python .\scripts\inspect_h5ad.py D:\your-data\example.h5ad
```

脚本默认使用 `backed="r"`，只检查结构，不把完整大矩阵载入内存。

## Notebook

- `01_resource_inventory.ipynb`：统计四类资源的数量和访问状态。
- `02_model_dataset_relationships.ipynb`：分析模型—数据—任务多对多关系。
- `03_dataset_statistics.ipynb`：统计物种、模态、任务、原始/处理数据可用性。

Notebook 只读取本仓库的 CSV，不需要先下载大型表达矩阵。

## 规模数字怎么理解

- `survey_reported_size` 固定保留 ACL 综述当时报告的历史规模。
- `current_model_size` 只在官方当前资料明确给出时填写。
- 例如 GeneFormer 的综述历史语料是 27.4M，而当前 V2 模型卡约为 104M；两者同时记录，不能覆盖。
- Nicheformer 的综述表写约 57M，而更新后的论文描述 57M 解离细胞加 53M 空间细胞、总计超过 110M；两种口径分别保存。

## 为什么不能直接比较模型谁“最好”

不同模型使用的预训练语料、数据切分、评价指标、零样本/微调设定和数据版本并不一致。表格可以回答“谁在什么数据上做了什么”，不能直接据此给模型做统一总排名。

## 许可

本目录中原创代码按 MIT License 发布。目录中的链接、论文、数据和模型权重仍受各自来源许可约束；本仓库不重新许可第三方材料，也不保存受控的人类个体级数据。

## 引用

首先引用 ACL 综述；实际使用某个模型或数据集时，还必须引用 `model_repositories.csv` 或 `downstream_datasets.csv` 中对应的原始论文。BibTeX 汇总见 [`metadata/sources.bib`](metadata/sources.bib)。
