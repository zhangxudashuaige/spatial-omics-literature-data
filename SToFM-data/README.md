# SToFM 数据资源与复现入口

本目录服务于论文 **SToFM: a Multi-scale Foundation Model for Spatial Transcriptomics**（ICML 2025；[arXiv:2507.11588](https://arxiv.org/abs/2507.11588)）。它保存真实来源、固定版本、下载与检查代码，不把近 1 TB 语料或模型权重放入普通 Git。

## 资源分层

### A. 预训练数据：SToCorpus-88M

- 官方入口：[Toycat/SToCorpus-88M](https://huggingface.co/datasets/Toycat/SToCorpus-88M)
- 论文报告：约 1,912 张切片、88,180,000 个细胞或 spot，人和小鼠。
- 技术：MERFISH、Xenium、CosMx、Stereo-seq、Slide-seqV2、SeekSpace。
- 2026-08-31 API 实检：固定 revision `6f699f128416e8d55d6ab74976e964caec98b157`，1,869 个文件，979,490,255,888 bytes；Hugging Face 页面标注 MIT。
- `manifests/huggingface_files.csv` 保存逐文件路径、大小和可用的 LFS SHA256。它是清单，不是表达数据。

### B. 模型与代码

- [官方代码](https://github.com/PharMolix/SToFM)，本项目固定到 commit `2354d5799347867578793752e8c2dd93ae6587b7`（MIT）。
- 权重由两个模块组成：cell encoder 与 SE(2)-Transformer；官方 Google Drive 同时提供 checkpoint 和 demo 入口。
- 权重只在 [`checkpoints/README.md`](checkpoints/README.md) 登记。官方 `get_embeddings.py` 预期 `cell_bert`、`cell_proj.bin`、`config.json` 和 `se2transformer.pth`，输出每个细胞 256 维嵌入。
- 官方 `get_embeddings.sh` 写成 `get_embedding.py`，而仓库真实文件为 `get_embeddings.py`；复现时应使用后者。

### C. 下游数据

| 任务 | 数据 | 官方入口 | 状态 |
|---|---|---|---|
| 人胚胎组织区域分割 | HESTA | [CNGB HESTA](https://db.cngb.org/hesta/) | 公开门户；逐文件许可需核对 |
| 人脑区域分割 | DLPFC | [spatialLIBD](https://research.libd.org/spatialLIBD/) | 公开软件/处理数据入口 |
| 细胞注释 | 小鼠脑 Stereo-seq | [STDS0000139](https://db.cngb.org/stomics/datasets/STDS0000139) | 公开页面；下载规则按 CNGB |
| 零样本聚类 | 小鼠脑 MERFISH | [SpatialOmics dataset 184](https://gene.ai.tencent.com/SpatialOmics/dataset?datasetID=184) | 动态页面；精确文件待核对 |
| 解卷积 | 小鼠肝脏 Stereo-seq | [STDS0000239](https://db.cngb.org/stomics/datasets/STDS0000239) | 公开页面；下载规则按 CNGB |
| 基因补全 | 人皮肤 Xenium | [10x Genomics](https://www.10xgenomics.com/cn/datasets/human-skin-data-xenium-human-multi-tissue-and-cancer-panel-1-standard) | 公开产品数据页 |

没有给 SeekSpace 评测数据虚构独立下载链接；它只作为预训练技术来源登记。

## Windows PowerShell 使用

```powershell
cd "SToFM-data"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 只列清单，不下载
python scripts\list_huggingface_files.py

# 查看匹配文件及预计大小，不下载
python scripts\download_selected_files.py --pattern "10x/human_brain.h5ad"

# 明确确认后才下载所选文件
python scripts\download_selected_files.py --pattern "10x/human_brain.h5ad" --confirm

# 检查已有空间数据
python scripts\inspect_spatial_data.py data\raw\example.h5ad
python scripts\verify_checksums.py manifests\downloaded_files.csv
```

`download_selected_files.py` 禁止空模式和全仓通配；下载前总是先打印文件数量与总大小。`download_demo.py` 只登记/打开作者共享目录，除非明确传入 `--confirm`，不会下载。

## 从数据到嵌入

原始/处理空间表达与坐标 → 作者 preprocessing 生成 `data.h5ad`、`hf.dataset` → cell encoder 生成 `ce_emb.npy` → SE(2)-Transformer 整合空间邻域 → `stofm_emb.npy`。

模型输入、模型权重和模型输出是三类不同对象。完整论文复现还需要 GPU/CUDA、作者权重、与论文一致的预处理和下游任务头；本仓库不声称仅凭小 demo 能重现论文指标。

## Demo Notebook

[`notebooks/inspect_demo.ipynb`](notebooks/inspect_demo.ipynb) 自动寻找本地 demo H5AD，读取 shape/坐标并绘图；若没有数据则清楚提示下载步骤。只有同时提供官方代码、两个权重模块和预处理数据时才运行 `get_embeddings.py`，否则不伪造嵌入结果。

详细关系和复现边界见 [`docs/data_relationship.md`](docs/data_relationship.md) 与 [`docs/reproduction_plan.md`](docs/reproduction_plan.md)。
