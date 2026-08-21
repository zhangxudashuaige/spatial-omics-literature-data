# Xiao et al. (2024)：CS8 人原肠胚三维空间转录组

本目录是统一资料库中的一个论文项目，不是独立仓库。它保存论文、数据源、真实文件清单、下载与检查脚本、Notebook 和可复现性记录；不会把约 2 TB 的人类原始测序数据提交到 GitHub。

## 论文与研究对象

- 论文：*3D reconstruction of a gastrulating human embryo*
- 期刊：Cell 187(11), 2855–2874.e19（2024）
- DOI：[10.1016/j.cell.2024.03.041](https://doi.org/10.1016/j.cell.2024.03.041)
- 样本：一枚男性 Carnegie stage 8（CS8）人胚胎，约受精后 17–19 天
- 实验：62 张横向 Stereo-seq 组织切片；切片厚度 10 µm，相邻上机切片约间隔 20 µm
- 分析单位：38,562 个通过质控的 bin50 空间点。bin50 是固定空间网格，不是分割出的严格单细胞；论文近似视为一个细胞尺度，在组织密集处可能混合多个细胞的信号。

## 关键结论：公开数据目前到哪一层

| 层级 | 公开位置 | 当前核查结果 |
|---|---|---|
| 原始测序 | [HRA005567](https://ngdc.cncb.ac.cn/gsa-human/browse/HRA005567) | 256 个 FASTQ（128 对）+ 128 个统计 XML，总计 1,997,710,489,661 bytes，约 1.998 TB / 1.817 TiB |
| 项目元数据 | HRA 页面与接口 | 1 个个体、1 个样本、128 个 run、12 个实验分组；未提供 62 张组织切片与 run 的完整对应表 |
| 作者代码 | [Zenodo 10851179](https://doi.org/10.5281/zenodo.10851179) | 对应 GitHub 标签 `STO-analysis`，含 SAW 5.4、PASTE、SCC、regulon 和绘图代码；不含表达矩阵、三维坐标或注释数据 |
| 补充表 | Cell 附件 | 5 个 XLSX：marker、缩写、细胞数、TF 模块、跨物种同源基因；不含坐标或表达矩阵 |
| 在线结果 | [cs8.3dembryo.com](https://cs8.3dembryo.com) | 交互式查看论文处理后的三维结果，不等同于可下载的数据文件 |

因此，本项目现在可以可靠地完成：数据资产盘点、选择性下载原始 FASTQ、校验文件、检查用户自行取得的 GEM/GEF/H5AD/坐标文件、运行安全的 Notebook 框架。仅凭当前公开文件，不能完整从 FASTQ 重建论文的空间表达矩阵和最终三维坐标，原因见 [复现说明](docs/reproduction_notes.md)。

## 目录

```text
metadata/     数据源、数据集、真实文件和外部参考清单
scripts/      元数据抓取、目录列举、选择性下载、格式检查和校验
notebooks/    数据盘点、表达数据检查、坐标检查和 3D 可视化
docs/         数据、格式、下载和复现边界说明
data/         本机数据目录；内容默认被 Git 忽略
results/      不含个体序列的小型统计结果和测试图片
```

## Windows PowerShell 快速开始

在本目录打开 PowerShell：

```powershell
conda env create -f environment.yml
conda activate human-cs8-spatial-embryo

# 只取元数据，不下载 FASTQ
python scripts/fetch_hra_metadata.py
python scripts/list_hra_files.py

# 查看清单中的总大小
Import-Csv metadata/files_manifest.csv |
  Where-Object {$_.source_id -eq "HRA005567"} |
  Measure-Object -Property size_bytes -Sum
```

选择性下载必须明确写出文件名，并显式加 `--download`：

```powershell
python scripts/download_selected_files.py --file HRR1375369_f1.fq.gz
python scripts/download_selected_files.py --file HRR1375369_f1.fq.gz --download
```

第一条只是预览；第二条才会下载，并支持 `.part` 续传。不要在没有评估磁盘和数据库条款时批量选择全部文件。

启动 Notebook：

```powershell
jupyter lab notebooks
```

Notebook 02–04 会优先读取你放在 `data/processed/` 的真实处理后文件；若没有真实数据，只运行明确标注为“合成测试”的代码路径，以验证环境和绘图流程，不会把测试点误称为论文结果。

## 数据、代码与许可

- 本仓库新写的脚本和文档采用 MIT License，见 [LICENSE](LICENSE)。
- HRA005567 的人类数据仍受 GSA-Human 数据条款、原论文伦理审批和引用要求约束；本仓库不重新分发原始序列。
- Zenodo 元数据声明 CC BY 4.0，但对应 GitHub 快照没有 `LICENSE` 文件，因此本仓库只保存版本、链接和下载脚本，不复制作者源码。
- 出版社补充表仍受出版商和论文许可约束，本仓库只记录文件清单与说明，不再次上传附件。

使用数据时至少引用原论文、HRA005567、PRJCA019863，以及实际采用的作者代码版本。外部参考数据各自需要单独引用，见 [reference_datasets.csv](metadata/reference_datasets.csv)。
