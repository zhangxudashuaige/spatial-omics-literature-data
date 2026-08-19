# 下载与检查指南

## 1. 只检查 URL

```powershell
python scripts/download_geo_processed.py --check-url
```

脚本请求极小字节范围，不下载完整文件；输出 HTTP 状态、服务器是否支持 Range、报告文件大小和错误。

## 2. 下载处理后数据

```powershell
python scripts/download_geo_processed.py
```

默认保存到 `data/external/GSE278603/GSE278603_RAW.tar`。下载使用 `.part` 临时文件、HTTP Range 续传、指数退避重试、进度条和最终 SHA256。若服务器忽略 Range，脚本会重新开始，避免拼接出损坏文件。

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

2026-08-19 实测：Windows curl HTTPS 为 `schannel: failed to receive handshake, SSL/TLS connection failed`；HTTP 为 `Empty reply from server`；FTP 为 `response reading failed`；Python `urllib` 为 `SSL: UNEXPECTED_EOF_WHILE_READING`；内置浏览器为 `net::ERR_CONNECTION_CLOSED`。因此没有生成虚假的下载成功状态、SHA256 或 H5AD shape。
