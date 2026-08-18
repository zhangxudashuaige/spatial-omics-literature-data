# 数据下载指南

## 1. 先查看清单

```powershell
python scripts\download_processed_data.py --dry-run
```

脚本只对 `manifests/files.csv` 中 `direct_download=yes` 且有明确官方直链的条目执行下载。没有文件名、直链或大小的项目不会被猜测下载。

## 2. CNGB 原始数据

入口：https://db.cngb.org/data_resources/project/CNP0003837

CNGB 页面报告项目总量约 125.58 TB，只开放部分文件直接下载：

1. 打开项目页面并选择 **Download metadata** 或 **Get FTP links of all files**。
2. 若页面要求登录，使用自己的 CNGBdb 账户登录。
3. 将官方导出的 metadata/FTP 清单保存在 `data/raw/metadata/`。
4. 先评估磁盘空间，再按样本选择 FASTQ 或图像。
5. 需要完整项目时联系 `datasubs@genomics.cn`。

`download_raw_metadata.py` 尝试读取 CNGB 公开项目元数据 API，但网络或站点策略可能导致 TLS/登录错误；脚本失败时不会转而猜测下载地址。

## 3. BSDC 处理后数据

入口：https://doi.org/10.12412/BSDC.1699433096.20001

若页面要求登录或不显示文件：

1. 登录 BSDC/脑科学数据中心。
2. 打开数据文件下载区并导出元数据。
3. 将官方文件清单保存到 `data/processed/metadata/`。
4. 对照 `manifests/datasets.csv` 决定下载哪些模态。

## 4. 在线图谱的已确认文件

在线图谱：https://mouse.digital-brain.cn/spatial-omics

本仓库已确认两个真实直链：

- `stereoseq.celltypeTransfer.2mice.all.tsv.gz`
- `section_id_used_in_paper.tsv`

下载：

```powershell
python scripts\download_processed_data.py --download
```

脚本使用 `.part` 临时文件，下载完成后再改名，避免把中断文件误当作完整文件。

## 5. 文件校验

```powershell
python scripts\verify_files.py
```

官方没有公布 SHA256 时，脚本会计算本地 SHA256 并生成 `results/tables/local_file_inventory.csv`，用于以后复查；它不会把本地校验值冒充官方校验值。
