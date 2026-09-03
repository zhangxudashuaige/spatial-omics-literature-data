# scMamba 数据资料模块

本目录为论文 **scMamba: A Scalable Foundation Model for Single-Cell Multi-Omics Integration Beyond Highly Variable Feature Selection** 保存可复现的数据入口、下载/检查脚本、模型配置摘要和数据清单。论文为 [arXiv:2506.20697](https://arxiv.org/abs/2506.20697)，官方代码为 [23AIBox/scMamba](https://github.com/23AIBox/scMamba)。

## 这里保存什么

- Git 保存：来源、版本、清单、脚本、说明和可公开的小型示例。
- 本机保存：完整 H5MU/H5AD、FASTQ、BAM、fragment、模型检查点和分析结果。
- 截至 2026-08-30，作者 Dropbox 共享目录中实际可见的数据只有 `datasets/PBMC.h5mu`（775,504,179 bytes）；`checkpoints/` 为空。该文件已下载到本地 ignored `raw/` 并实检，SHA-256 为 `d7989b7d733b3267a533f5a6ba946ff96845b9b6b198a1bb114c562520b9b42e`。未把其他论文数据或检查点写成“已提供”。
- 官方代码固定为 commit `4887c0a8ab060b2482384d2294fe265b633d2406`（AGPL-3.0）。数据许可未在共享目录中明确给出，因此本仓库不重新分发真实细胞样本。

## 八套数据及关系

| 数据 | 模态 | 论文用途 | 当前状态 |
|---|---|---|---|
| SHARE-seq BMMC | 成对 RNA+ATAC | 基础整合、聚类、配对评估 | accession 已核对；精确处理文件未公开定位 |
| Human Brain | 成对 snRNA+snATAC | 脑多组学整合、迁移注释 | accession 已核对；精确处理文件未公开定位 |
| 10x Multiome PBMC | 成对 RNA+ATAC | 跨技术验证 | 作者 Dropbox 有 `PBMC.h5mu` |
| Human Fetal Atlas | 成对 RNA+ATAC | 图谱级扩展性 | 上游项目入口已登记；精确处理文件未公开定位 |
| 10x Multiome BMMC | 成对 RNA+ATAC | 造血/红系轨迹 | GSE194122；精确处理文件未公开定位 |
| CITE-seq BMMC S1/S4 | 成对 RNA+ADT | 细胞类型与困难亚型注释 | GSE194122；精确处理文件未公开定位 |
| Human Brain 3k | RNA only | 多组学模型向 RNA 数据迁移 | 10x 页面已登记；论文使用的是处理后 3,233 nuclei |

### PBMC.h5mu 实测结构

- 模态：`rna`、`atac`。
- RNA：9,631 cells × 36,601 genes，CSR float32；`var` 含 `gene_ids`、`feature_types`、`genome`、`interval`。
- ATAC：9,631 cells × 108,377 peaks，CSR float32；相同 `var` 字段。
- 两个模态的 9,631 个 cell ID 完全同序；无重复、无单侧缺失。
- `obs` 唯一字段为 `cell_type`；没有 `batch` 或 `donor`；没有 `layers`、`obsm`、`uns`。
- 论文报告 29,095 genes 和 107,194 regions，属于论文预处理后的维度；本文件 `X` 的实测维度不能被该数字替代。

“paired”表示同一个细胞 barcode 同时具有两种模态。RNA+ATAC 是基因表达与染色质可及性；RNA+ADT 是基因表达与抗体衍生蛋白信号。原始测序数据、论文处理后的 H5MU、scMamba 输入对象和训练检查点是四种不同资产，不能互相替代。

## Windows PowerShell 使用

```powershell
cd scmamba-data
conda env create -f environment.yml
conda activate scmamba-data

# 先看清单，不下载
python scripts/download_processed_data.py --list

# 只下载作者公开的 PBMC.h5mu；支持续传和重试
python scripts/download_processed_data.py --dataset multiome_pbmc --download

# 检查结构和跨模态配对
python scripts/inspect_h5mu.py datasets/multiome_pbmc/raw/PBMC.h5mu --output datasets/multiome_pbmc/inspection.local.json
python scripts/validate_paired_cells.py datasets/multiome_pbmc/raw/PBMC.h5mu --modality-a rna --modality-b atac

# 许可确认后才生成本地小样本；默认不进入 Git
python scripts/create_small_sample.py datasets/multiome_pbmc/raw/PBMC.h5mu examples/PBMC.sample.h5mu --acknowledge-license
```

`download_processed_data.py` 默认只列出或检查，不会自动下载八套大数据。没有精确官方文件 URL 的条目保持 `unresolved`，绝不以同名第三方文件替代。

## H5MU/H5AD 是什么

H5MU（MuData）把多个 AnnData 模态放在一个文件中：例如 `mdata.mod['rna']` 与 `mdata.mod['atac']`。每个模态内，`X` 是细胞×特征矩阵，`obs` 是细胞元数据，`var` 是基因/peak/蛋白元数据，`layers` 保存变换后的矩阵，`obsm` 保存低维表示。检查脚本只读取稀疏结构，不把大型矩阵整体转成稠密数组。

## 官方推理接口

官方 RNA+ATAC 推理脚本要求模态名 `rna`、`atac`，细胞标签默认列名 `cell_type`；RNA+ADT 脚本要求 `rna`、`adt`。官方示例命令引用 `results/checkpoints/PBMC.pt`，但当前 Dropbox 的 `checkpoints/` 为空，所以不能声称该检查点已经可下载。配置摘要见 [`checkpoints/README.md`](checkpoints/README.md)。此外，官方 README 提到 `train_script.py`，固定 commit 中没有该文件，这是待作者补全的复现缺口。

## 官方代码环境与本资料环境

本目录的环境仅用于数据检查。真正运行 scMamba 请按照固定 commit 的官方说明安装 CUDA 12.1、PyTorch 2.3.1、Mamba、flash-attention 等 GPU 依赖。官方 `requirements.txt` 中出现 `scikit-learn==0.4.0`，该版本看起来不可用，本资料没有静默照抄或替换，需由使用者结合作者环境确认。

## 许可与引用

代码使用 AGPL-3.0；各数据的许可和使用限制以 GEO、10x、scGLUE、scCLIP 和作者共享页面为准。Dropbox 文件当前没有单独许可文本，因此仅供来源明确的本地科研检查，不在本仓库重新发布。使用时应引用 scMamba 论文以及实际下载数据对应的原始研究/数据库 accession。
