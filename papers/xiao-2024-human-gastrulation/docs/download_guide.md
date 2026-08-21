# 下载指南

## 先看大小，再下载

`metadata/files_manifest.csv` 已记录官方 HTTPS 目录中的 384 个真实文件。HRA 部分合计 1,997,710,489,661 bytes，其中 FASTQ 为 1,997,710,185,424 bytes，XML 为 304,237 bytes。

```powershell
python scripts/list_hra_files.py
```

这条命令只重新列目录，不下载 FASTQ。输出会再次显示文件数和总大小。

## 抓取小型项目元数据

```powershell
python scripts/fetch_hra_metadata.py
```

输出位于 `data/external/HRA005567/metadata/`，因为它是从外部数据库取得的本地副本，所以不会进入 Git。

## 选择性下载

先预览：

```powershell
python scripts/download_selected_files.py --file HRR1375369_sta.xml
```

确认后下载：

```powershell
python scripts/download_selected_files.py --file HRR1375369_sta.xml --download
```

也可以指定 run：

```powershell
python scripts/download_selected_files.py --run HRR1375369
python scripts/download_selected_files.py --run HRR1375369 --download
```

`--run` 会选择该 run 下的两条 FASTQ 和 XML，请先看预览中的合计大小。脚本使用 `.part` 临时文件、HTTP Range 续传、重试和 SHA-256。它不会提供“下载全部”的默认开关。

## 作者代码

```powershell
python scripts/download_zenodo_code.py
```

脚本通过 DataCite 解析 DOI，固定到 GitHub 标签 `STO-analysis`，下载到 `data/external/zenodo_code/`。该快照没有仓库内 `LICENSE` 文件；请遵循 Zenodo 元数据中声明的 CC BY 4.0，并保留原始引用。

## 处理后数据

当前 HRA 下载目录和作者代码快照都未提供论文最终的处理后表达矩阵或三维坐标文件。若作者、期刊或在线网站将来公开这些文件，请把原文件放入：

```text
data/processed/expression/
data/processed/coordinates/
data/processed/annotations/
```

然后用 `scripts/inspect_spatial_files.py` 检查；不要先改名或转换，以保留来源可追溯性。

## 人类数据注意事项

下载或分析前检查 HRA 项目页的开放状态和最新使用条款。不要把 FASTQ、个体序列、切片图像或未经确认可再分发的数据提交到 GitHub、issue、Notebook 输出或小样本文件中。
