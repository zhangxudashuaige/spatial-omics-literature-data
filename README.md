# 空间组学与单细胞论文数据资料库

这是一个长期维护的个人研究资料库，用来记录值得保留的论文、公开数据集、下载方式、校验值和分析笔记。

## 使用原则

- Git 里保存：元数据、笔记、数据来源、下载脚本、校验值和小型结果。
- 大型数据不直接提交：原始数据放在本机 `data/`，该目录已被忽略。
- 出版商 PDF 默认不公开上传：只记录 DOI 和本机文件校验值；确认许可后再放入 `papers/<id>/attachments/`。
- 每个数据集记录来源、版本、许可证、获取日期和处理过程，以便复现。

## 当前收录

| ID | 论文 | 主题 | 状态 |
|---|---|---|---|
| `wei-2026-spatialvista` | SpatialVista 软件论文 | 3D 空间转录组可视化 | 已建档；13 个展示数据已逐项登记 |
| `zhang-2023-whole-mouse-brain-merfish` | 成年小鼠全脑 MERFISH 图谱 | 小鼠脑、MERFISH | 已建档；对应 3 个展示数据 |
| `han-2025-mouse-brain-stereo-seq` | 小鼠全脑 Stereo-seq 图谱 | 小鼠脑、Stereo-seq | 已建档；对应 1 个展示数据 |
| `cheng-2024-mouse-embryo-3d` | E9.5/E11.5 小鼠胚胎三维转录组 | 小鼠胚胎、Stereo-seq、SBFI | 已建档；论文主数据当前不可公开获取，已建立完整清单与下载工具 |
| `xie-2025-digital-mouse-embryo` | E7.5–E8.0 小鼠数字胚胎 | 小鼠胚胎、三维重建 | 已建档；对应 6 个展示数据 |
| `xiao-2024-human-gastrulation` | 人原肠胚三维重建 | 人胚胎、Stereo-seq | 完整项目；384 个 HRA 文件、作者代码和 5 个补充表已核查 |
| `zhang-2025-single-cell-foundation-model-survey` | 单细胞基础模型综述 | 单细胞基础模型、预训练语料、下游基准 | 完整资源目录；38 个下游数据集及 31 篇可唯一定位的原始论文均已独立登记 |
| `paper-datasets` | GraphSAGE、TABULA 与 HEIST 数据资料 | 图机器学习、单细胞与空间组学基础模型 | 官方来源、固定版本、下载/检查脚本与合规小样例；未公开的精确训练清单均标记 unresolved |
| `fang-2025-cell-graph-compass` | Cell-GraphCompass | 单细胞图基础模型 | Zenodo 处理后数据包、构图先验与评测数据分层登记；50M 预训练语料不冒充公开包 |
| `peng-2026-stvcr` | stVCR | 时空单细胞动力学 | 固定官方代码版本，已实检四套模拟数据，登记蝾螈与果蝇真实数据 |
| `lin-2024-sctrans` | SCTrans | 基因选择式细胞类型注释 | 7 个公开 scRNA-seq 数据集的原论文、来源、下载与跨平台处理记录 |
| `yuan-2025-scmamba` | scMamba | 单细胞多组学基础模型 | 8 套 RNA+ATAC/RNA+ADT/RNA 数据已登记；作者 Dropbox 当前仅有 PBMC.h5mu，检查点为空 |
| `hu-2021-spagcn` | SpaGCN | 空间域识别与空间变异基因 | 7 套论文数据及官方教程数据已登记；两个小型教程输入已实检但不提交 Git |
| `zhao-2025-stofm` | SToFM | 多尺度空间转录组基础模型 | SToCorpus-88M 的 1,869 个真实文件与 979.49 GB 总量已用官方 API 核验；未下载全量语料 |

SpatialVista 数据入口见 [`papers/wei-2026-spatialvista/README.md`](papers/wei-2026-spatialvista/README.md)，单细胞基础模型综述资源入口见 [`papers/single-cell-foundation-model-resources/README.md`](papers/single-cell-foundation-model-resources/README.md)，GraphSAGE/TABULA/HEIST 数据入口见 [`paper-datasets/README.md`](paper-datasets/README.md)。Cell-GraphCompass、stVCR 与 SCTrans 同时保存了 [`papers/`](papers/) 中的论文条目和 [`datasets/`](datasets/) 中的可复现数据模块。

scMamba 的独立数据入口见 [`scmamba-data/README.md`](scmamba-data/README.md)，同时在 [`papers/yuan-2025-scmamba/`](papers/yuan-2025-scmamba/) 保存论文记录。

SpaGCN 的数据入口、下载与检查工具见 [`spagcn-data/README.md`](spagcn-data/README.md)，论文记录见 [`papers/hu-2021-spagcn/`](papers/hu-2021-spagcn/)。

SToFM 的预训练语料清单、下游数据和复现工具见 [`SToFM-data/README.md`](SToFM-data/README.md)，论文记录见 [`papers/zhao-2025-stofm/`](papers/zhao-2025-stofm/)。

## 目录结构

```text
papers/                 每篇论文一个目录
  <paper-id>/
    README.md            论文摘要、价值、代码与数据入口
    metadata/datasets.csv 关联数据集清单（完整项目可采用此扩展结构）
    resources.csv        数据层级、补充材料与代码资源清单
    notes.md             阅读和复现笔记
catalog/
  papers.csv             全库论文索引
  datasets.csv           全库数据索引
  resources.csv          原始数据、处理数据、代码和补充材料入口
  TAGGING.md             标签词表与检索规则
scripts/                 下载与校验辅助脚本
data/                    本机原始数据（不会提交 Git）
datasets/                模型论文的数据模块、manifest、下载/检查脚本
```

## 这里到底存什么

本仓库采用“索引和知识进 Git，大文件留在数据源或本地硬盘”的方式：

- GitHub 保存论文条目、数据集链接、accession、许可证状态、标签、笔记、下载/分析脚本和小型 notebook。
- `.h5ad`、FASTQ、图像等大型文件下载到本机 `data/<paper-id>/raw/`，由 `.gitignore` 阻止上传。
- 下载后计算 SHA-256，写回 CSV；以后即使文件改名，也能用校验值确认是不是同一份数据。
- 同一个数据在 SpatialVista 中是“展示版”，在原论文数据库中可能还有原始序列、表达矩阵、组织图像和处理后对象；本库分别注明，不把它们混成一个概念。

每篇论文按“论文完整数据资产”建档，而不是只记录某个软件使用的子集。`datasets.csv` 记录生物学数据集，`resources.csv` 记录同一研究的原始图像、表达矩阵、元数据、坐标、参考数据、补充表和代码入口。

## 新增一篇论文

1. 复制 `templates/paper/`，将目录名改成 `作者-年份-关键词`。
2. 填写论文 `README.md`、`notes.md`、`datasets.csv` 和 `resources.csv`。
3. 在 `catalog/papers.csv`、`catalog/datasets.csv` 与 `catalog/resources.csv` 增加索引。
4. 数据下载到 `data/<paper-id>/raw/`，保留原文件名。
5. 运行 `scripts/checksum.ps1` 生成 SHA-256，记录到数据清单。
6. 提交 Git：`git add .`、`git commit -m "Add <paper-id>"`。

## 标签与查找

索引中的 `tags` 字段使用分号分隔的标准标签，例如：

```text
topic:spatial-transcriptomics;modality:3d-st;organism:mouse;status:catalog-only
```

标签命名和推荐词表见 [`catalog/TAGGING.md`](catalog/TAGGING.md)。例如，可用下面的命令查找全部 3D-ST 条目：

```powershell
rg "modality:3d-st" catalog papers
```

`rg` 是开源全文搜索程序 **ripgrep**，不是本仓库自创的命令；上面的检索表达式由本仓库编写。请在仓库根目录的 PowerShell 中运行。若电脑没有安装 `rg`，可使用本仓库的兼容脚本：

```powershell
.\scripts\search.ps1 "modality:3d-st"
```

脚本会优先调用 `rg`；找不到 `rg` 时自动改用 Windows PowerShell 自带的 `Select-String`。更详细说明见 [`catalog/TAGGING.md`](catalog/TAGGING.md)。

## 大数据的长期方案

开始阶段用“GitHub + 本地/云盘数据”最简单。以后如果需要版本化大型数据，可以接入 DVC、Git LFS、Zenodo 或 OSF；仓库继续保存索引与复现脚本，而不是复制所有公开原始数据。
