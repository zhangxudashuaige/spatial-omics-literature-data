# Cheng et al. (2024)：E9.5/E11.5 小鼠胚胎三维转录组

本目录是总资料库中这篇论文的完整数据资产记录。它保存数据说明、来源状态、文件清单、字段契约、下载/校验工具和小型结构样本；论文的 FASTQ、表达矩阵、SBFI 和显微图像等大文件应下载到总仓库根目录的 `data/cheng-2024-mouse-embryo-3d/`，不会提交 GitHub。

> 截至 2026-08-18，本目录不含真实论文数据。CNSA `CNP0005981` 不能通过 CNGB 公共项目接口取得；论文给出的 MOSTA3D 地址返回 404。

## 文献信息

- 题目：*Three-dimension transcriptomics maps of whole mouse embryo during organogenesis*
- 类型：bioRxiv 预印本 v1（尚未同行评审）
- DOI：https://doi.org/10.1101/2024.08.17.608366
- 原始数据 accession：`CNP0005981`
- 论文给出的处理后入口：https://db.cngb.org/stomics/mosta/3d/ （当前 404）

## 论文报告的数据

| 阶段 | Stereo-seq 切片 | 细胞数 | 细胞类型 | 器官/空间区域 | 取样 |
| --- | ---: | ---: | ---: | ---: | --- |
| E9.5 | 94 | 915,901 | 88 | 14 | 连续切片全部测序 |
| E11.5 | 91 | 7,830,602 | 100 | 23 | 间隔切片测序，相邻未测序切片做 H&E |

每次切片前采集 SBFI（Serial Block-Face Imaging）。Stereo-seq 切片使用 ssDNA 染色辅助细胞分割；切片配准到对应 SBFI 后堆叠成三维胚胎，最终细胞质心 x/y/z 坐标写入逐切片 H5AD。

## 需要收集的完整数据

- 每张切片的 FASTQ R1（CID + MID/UMI）和 R2（cDNA）。
- 每张切片的 GEF、GEM 或 H5AD 表达矩阵。
- 二维坐标、三维坐标、细胞边界/掩膜与细胞表达向量。
- 细胞类型、cluster、marker、置信度和 scRNA-seq 参考标签。
- 器官、空间域与亚域注释。
- 完整 SBFI、ssDNA，以及 E11.5 相邻切片 H&E 图像。
- 刚性/仿射/非线性配准参数、z 位置和最终变换结果。
- 作者提供时保存胚胎/器官 mesh、轮廓、体积、细胞数量与密度。

逐项状态和目标位置见 [`metadata/data_manifest.csv`](metadata/data_manifest.csv)，字段含义见 [`data-dictionary.md`](data-dictionary.md)。

## 新用户怎样使用

在总仓库 `spatial-omics-literature-data` 根目录运行：

```powershell
python papers\cheng-2024-mouse-embryo-3d\scripts\validate_data_contract.py
python papers\cheng-2024-mouse-embryo-3d\scripts\check_availability.py
python papers\cheng-2024-mouse-embryo-3d\scripts\download_data.py --dry-run
```

当前下载预演会显示 0 个可下载文件级条目。这表示权威来源尚未给出公开文件清单，不表示真实数据大小为 0。

来源恢复后，先把每个真实文件的 `download_url`、`size_bytes`、`sha256` 和具体 `local_path` 写入 manifest，再下载：

```powershell
python papers\cheng-2024-mouse-embryo-3d\scripts\download_data.py --download --accept-large-files
```

脚本默认不下载；如果大小未知或超过默认 20 GiB 还会再次阻止。保存原理见 [`storage-plan.md`](storage-plan.md)。

## 小型样本与 Jupyter

`sample_data/synthetic_*.csv` 是合成字段示例，不是论文数据。可双击 [`notebooks/launch_jupyter.cmd`](notebooks/launch_jupyter.cmd)，打开 `01_data_inventory.ipynb` 查看清单和表之间的连接关系。

得到真实 H5AD 后，可抽取 1,000 个细胞：

```powershell
python papers\cheng-2024-mouse-embryo-3d\scripts\make_h5ad_sample.py `
  data\cheng-2024-mouse-embryo-3d\E9.5\expression\某张切片.h5ad `
  --stage E9.5 --cells 1000
```

## 一个必须避免的混淆

STOmicsDB 的旧版 MOSTA 下载页包含 `Mouse_E9.5_embryo.h5ad` 和 `Mouse_E11.5_embryo.h5ad` 等 2022 年数据。它们不是本预印本声明的 94/91 张切片数据，不能用来替代 `CNP0005981` 或 MOSTA3D。旧条目已从本论文的数据关联中移除。

## 标签

`organism:mouse` · `tissue:embryo` · `modality:stereo-seq` · `imaging:sbfi` · `stage:e9.5` · `stage:e11.5` · `source:cnsa` · `status:catalog-only` · `license:verify`
