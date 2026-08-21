# 下载与检查指南

## 1. 只检查 URL

```powershell
python scripts/download_geo_processed.py --check-url
```

脚本依次检查 NCBI 总包网关、FTP HTTPS 镜像和六个独立 H5AD。它只请求极小字节范围并立即关闭连接，不下载完整文件；结果写入 `results/reports/download_status.json`。

## 2. 下载处理后数据

```powershell
python scripts/download_geo_processed.py
```

默认采用 `--mode auto`：

1. NCBI GEO 总包下载网关；
2. NCBI FTP HTTPS 总包镜像；
3. 如果两个总包端点都失败，逐个下载六个 H5AD。

下载使用 `.part` 临时文件、HTTP Range 续传、指数退避重试、进度条和最终 SHA256。若服务器忽略 Range，脚本会重新开始，避免拼接出损坏文件。TAR 必须包含六个 H5AD；独立文件必须具有有效 HDF5 文件头，校验通过后才会改为正式文件名。

只下载最小样本进行试用：

```powershell
python scripts/download_geo_processed.py --sample GSM9046244
```

直接逐个下载，不尝试总包：

```powershell
python scripts/download_geo_processed.py --mode files
```

## 为什么代码先下载，再读取

可以在代码中保存链接并自动下载，但不建议把 GEO URL 直接传给 `anndata.read_h5ad()`。H5AD/HDF5 读取经常需要随机访问，官方下载网关也可能重定向；先流式下载到本地、校验文件头与 SHA256，再用 `backed="r"` 读取最稳定。

例如最小样本下载成功后：

```powershell
python scripts/download_geo_processed.py --sample GSM9046244
python scripts/inspect_h5ad.py data/external/GSE278603/h5ad/GSM9046244_Embryo_E7.5_stereo_rep2.h5ad
```

因此仓库里的链接不是“只能人工点击的书签”，而是下载脚本的输入。大文件下载到被 Git 忽略的本地目录，GitHub 只保存链接、代码、校验值和分析流程。

## 3. 解压

```powershell
python scripts/extract_geo_archive.py
```

目标目录：`data/external/GSE278603/h5ad/`。脚本先检查 TAR 成员路径，阻止目录穿越，并只提取清单中的六个 H5AD。

## 4. 检查 H5AD

```powershell
python scripts/inspect_h5ad.py
```

输出：`metadata/h5ad_summary.csv`、`results/reports/h5ad_schema.json` 和 `docs/h5ad_schema.md`。

## 5. SRA 原始数据

本项目不自动下载 FASTQ。先阅读 `metadata/sra_manifest.csv`，在 NCBI Run Selector 导出实际 SRR 清单；需要时使用最新版 SRA Toolkit：

```text
prefetch --option-file SraAccList.txt
fasterq-dump --split-files SRR_ACCESSION
```

## 本次机器上的准确网络错误

2026-08-20 再次实测：GEO 官方网页及其下载按钮可由网络检索服务解析，下载按钮返回 TAR/H5AD 二进制端点；但当前 Windows 命令行出现 `SEC_E_NO_CREDENTIALS`，Python `requests` 出现 `SSL: UNEXPECTED_EOF_WHILE_READING`。因此链接已由官方页面确认，本机数据仍未下载，也没有生成虚假的 SHA256 或 H5AD shape。
