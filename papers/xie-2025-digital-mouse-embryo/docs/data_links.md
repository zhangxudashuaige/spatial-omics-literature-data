# 可用数据链接

核查日期：2026-08-20。以下链接均来自 NCBI GEO/SRA 官方页面，不是第三方转载地址。

## 处理后数据总入口

- GEO 项目页：https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE278603
- NCBI 下载网关：https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE278603&format=file
- NCBI FTP HTTPS 镜像：https://ftp.ncbi.nlm.nih.gov/geo/series/GSE278nnn/GSE278603/suppl/GSE278603_RAW.tar

下载网关和 FTP 镜像指向同一个 `GSE278603_RAW.tar`。总包约 802.8 MB，内部应包含六个 H5AD。脚本下载完成后会检查 TAR 是否可读取以及是否正好包含六个 H5AD，然后计算 SHA256。

## 六个独立 H5AD

| GEO | 阶段 | 官方样本页 | 官方 H5AD 下载端点 |
|---|---|---|---|
| GSM9046243 | E7.5 rep1 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM9046243 | https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSM9046243&file=GSM9046243_Embryo_E7.5_stereo_rep1.h5ad&format=file |
| GSM9046244 | E7.5 rep2 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM9046244 | https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSM9046244&file=GSM9046244_Embryo_E7.5_stereo_rep2.h5ad&format=file |
| GSM9046245 | E7.75 rep1 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM9046245 | https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSM9046245&file=GSM9046245_Embryo_E7.75_stereo_rep1.h5ad&format=file |
| GSM9046246 | E7.75 rep2 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM9046246 | https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSM9046246&file=GSM9046246_Embryo_E7.75_stereo_rep2.h5ad&format=file |
| GSM9046247 | E8.0 rep1 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM9046247 | https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSM9046247&file=GSM9046247_Embryo_E8.0_stereo_rep1.h5ad&format=file |
| GSM9046248 | E8.0 rep2 | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM9046248 | https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSM9046248&file=GSM9046248_Embryo_E8.0_stereo_rep2.h5ad&format=file |

这些端点会返回二进制 H5AD，不是用于阅读的网页。浏览器打开时通常会直接触发下载；代码则使用流式请求保存到本地。

## 原始测序数据

- BioProject：https://www.ncbi.nlm.nih.gov/bioproject/PRJNA1168072
- SRA Run Selector：https://www.ncbi.nlm.nih.gov/Traces/study/?acc=PRJNA1168072

FASTQ 体积很大，仓库不自动下载。先在 Run Selector 导出实际 SRR 清单，再使用 SRA Toolkit。

## “链接存在”和“本机能连接”是两件事

GEO 官方项目页明确列出六个样本、总 TAR 和每个独立 H5AD；官方下载按钮也解析到了上述二进制端点，因此链接结构是有效的。当前 Codex 运行环境访问 NCBI 时出现 Schannel/SSL EOF，属于本机网络传输失败。下载脚本会记录这种失败，不会把它误写为数据不存在。
