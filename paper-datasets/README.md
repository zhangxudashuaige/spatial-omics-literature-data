# GraphSAGE、TABULA 与 HEIST 论文数据资料项目

本目录属于统一仓库 `spatial-omics-literature-data`，用于保存 GraphSAGE、TABULA 和 HEIST 的**可复现入口**：官方来源、固定版本、下载脚本、文件清单、校验值、数据结构说明和合规的小型样例。它不是大型数据镜像，也不把来源不明或仅仅同名的数据混入论文复现链路。

## 一眼看懂这里保存了什么

| 部分 | GitHub 中保存 | 仅保存在本地 | 当前复现状态 |
|---|---|---|---|
| GraphSAGE | manifest、下载/检查脚本、MIT 许可的官方 `example_data`、说明文档 | 官方 PPI/Reddit ZIP 与解压数据 | PPI、Reddit 官方预处理包可定位；WoS Citation 受许可限制 |
| TABULA | manifest、Census 查询脚本、固定 commit 的 `vocab.json`、说明文档 | Census 查询生成的 `.h5ad` | 论文 15M 预训练细胞的精确 Census 版本与 cell ID 清单未公开，不能宣称完全重建 |
| HEIST | manifest、代码/模型元数据脚本、结构检查脚本、中文数据字典 | `.pt`、`.h5ad`、模型权重和完整生物数据 | 官方代码已固定；完整预训练集不是统一下载包，多数下游数据精确版本与许可仍待确认 |

大型 ZIP、H5AD、完整 NPY 和模型输出被 `.gitignore` 排除。完整数据应放本机磁盘、对象存储、DVC 或 Git LFS；普通 Git 只保存能解释“数据从哪里来、怎样获得、是不是同一版本”的内容。

## 官方论文与资源

### GraphSAGE

- 论文：Hamilton, Ying & Leskovec, *Inductive Representation Learning on Large Graphs*, NeurIPS 2017（[arXiv](https://arxiv.org/abs/1706.02216)）
- [项目主页](https://snap.stanford.edu/graphsage/)
- [官方代码](https://github.com/williamleif/GraphSAGE)，固定 commit：`a0fdef95dca7b456dab01cb35034717c8b6dd017`
- [PPI 预处理包](https://snap.stanford.edu/graphsage/ppi.zip)
- [Reddit 预处理包](https://snap.stanford.edu/graphsage/reddit.zip)

Citation 数据来自 Web of Science。项目主页明确说明只可向持有效 WoS 许可者提供，因此本项目仅登记，不下载、不重新分发。

### TABULA

- 论文：Ding et al., *Tabula: A Tabular Self-Supervised Foundation Model for Single-Cell Transcriptomics*, NeurIPS 2025（[论文页](https://papers.nips.cc/paper_files/paper/2025/hash/95d590995a8722259c61e094b62b25ac-Abstract-Conference.html)）
- [官方代码](https://github.com/aristoteleo/tabula)，固定 commit：`65b5f7ebf36a534da42de94570c108539af05541`
- [CELLxGENE Census](https://chanzuckerberg.github.io/cellxgene-census/index.html)
- [官方复现仓库](https://github.com/aristoteleo/tabula-reproducibility)，核查 commit：`4be23be8b58f4482593af434c7eb5a5debeab495`

截至本项目核查日，复现仓库只有 README，并明确写着 “currently under preparation”。因此 PBMC5K、Jurkat、Melanoma、hPancreas、Adamson、Norman、Replogle、Myeloid 和 Cell Lines 只登记论文用途，全部标记 `reproducibility_status: unresolved`，不下载第三方同名替代版本。

### HEIST

- 论文：Madhu et al., *HEIST: A Graph Foundation Model for Spatial Transcriptomics and Proteomics Data*, ICLR 2026（[OpenReview](https://openreview.net/forum?id=lK82jpa8jr)）
- [官方项目页](https://graph-and-geometric-learning.github.io/projects/heist)
- [官方代码](https://github.com/Graph-and-Geometric-Learning/HEIST)，固定 commit：`b83615df17126581294b0ba3c8a3b30f7860c6ff`
- [Hugging Face 模型](https://huggingface.co/HirenMadhu/HEIST)，官方 API 固定 revision：`e68434fc0b27a3d8dc94e258c26471acb8ffbfb9`
- 原始入口：[10x Genomics](https://www.10xgenomics.com/datasets)、[Vizgen](https://vizgen.com/)、[SEA-AD](https://portal.brain-map.org/explore/seattle-alzheimers-disease)

官方项目报告 22.3M cells、124 slices、15 organs，但没有一个统一预训练下载包，也没有公开完整的 cell ID/文件版本清单。DFCI、UPMC、Charville、Melanoma、Placenta、Lung Cancer 和 SEA-AD 下游条目均按代码用途登记；无法确认精确 URL、版本或许可的项目保持 `status: unresolved`。

## Windows PowerShell 使用方法

### 0. HEIST：先登记版本，再检查自己的数据

```powershell
py -3.13 .\scripts\download_heist_resources.py metadata
py -3.13 .\scripts\inspect_heist_sample.py .\data\heist\raw\your_file.h5ad
```

默认只抓取 GitHub/Hugging Face 元数据，不下载 22.3M 细胞数据。只有明确使用 `code` 或 `model` 子命令时才获取代码或模型；模型下载要求固定 revision。PyTorch `.pt/.pth` 可能执行 pickle 内容，检查时必须显式传入 `--trust-pickle`。

### 1. 下载 GraphSAGE 官方数据

```powershell
cd .\paper-datasets
.\scripts\download_graphsage.ps1 -Dataset PPI
.\scripts\download_graphsage.ps1 -Dataset Reddit
```

若所在 Windows 环境无法与 SNAP 的 HTTPS 端点完成 TLS 握手，可显式允许同一官方主机的 HTTP 回退：

```powershell
.\scripts\download_graphsage.ps1 -Dataset All -AllowHttpFallback
```

下载结果在 `data/graphsage/raw/`，不会进入 Git。脚本生成的本地下载记录包含原始 HTTPS URL、实际传输 URL、时间、文件大小和 SHA256。

### 2. 检查 GraphSAGE 文件结构

检查 GitHub 中的官方小样例：

```powershell
py -3.13 .\scripts\inspect_graphsage.py .\data\graphsage\example
```

也可以直接检查尚未解压的 ZIP：

```powershell
py -3.13 .\scripts\inspect_graphsage.py .\data\graphsage\raw\ppi.zip
```

### 3. 查询一个固定版本的 CELLxGENE 小样例

CELLxGENE Census 官方 Python API 当前只支持 Linux/macOS 的 Python 3.10–3.12；Windows 用户应在 WSL2、Linux 或容器中运行。`--census-version` 是必填项，不能用会随时间变化的隐式默认值。

```bash
python scripts/query_tabula_cellxgene.py \
  --census-version 2025-11-08 \
  --tissue blood \
  --max-cells 100 \
  --output data/tabula/sample/sample.h5ad
```

默认强制 `is_primary_data == True`，并同时生成 `sample_manifest.json`。这个样例来自你明确指定的 Census 版本，但**不是**论文未公开的 15M 精确训练细胞清单。

### 4. 校验已经下载的文件

```powershell
py -3.13 .\scripts\verify_checksums.py
```

脚本读取三个 YAML manifest，对存在于本地且已记录 SHA256 的文件进行核验；缺失的大文件会报告为 `missing`，不会假装已经下载。

## 复现边界

- GraphSAGE 的 PPI/Reddit 是官方预处理包；但 WoS Citation 不公开，且各原始来源的版本/许可要单独核实。
- TABULA 论文报告 15M 细胞、196 studies、133 tissues、422 cell types、23,156 基因词表、每研究约 1,200 HVGs 和 8 个组织客户端。
- 论文没有公开精确 Census 版本和完整 cell ID 清单，所以本项目只提供**固定版本的小规模 Census 查询入口**。
- 当前代码 commit 的 `resource/vocab.json` 有 60,697 个键值映射，与论文报告的 23,156 基因训练词表不是同一个可直接等同的对象；它是代码资源，不是表达矩阵。
- 等 `tabula-reproducibility` 正式发布精确来源与预处理脚本后，再把相关条目从 `unresolved` 更新为可复现状态。
- HEIST 的 10x/Vizgen/SEA-AD 预训练来源和七组下游任务没有统一、逐文件的官方下载表；本仓库不把项目主页数量误写为已经下载的数据。

详细字段解释见 [`docs/graphsage_data_dictionary.md`](docs/graphsage_data_dictionary.md)、[`docs/tabula_data_dictionary.md`](docs/tabula_data_dictionary.md) 和 [`docs/heist_data_dictionary.md`](docs/heist_data_dictionary.md)。
