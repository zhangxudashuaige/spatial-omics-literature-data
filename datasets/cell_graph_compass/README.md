# Cell-GraphCompass 数据模块

本目录保存论文 **Cell-GraphCompass: Modeling Single Cells with Graph Structure Foundation Model** 的可复现数据入口。正式论文见 [NSR](https://doi.org/10.1093/nsr/nwaf255)，预印本见 [bioRxiv](https://www.biorxiv.org/content/10.1101/2024.06.04.597354v1)，官方代码固定在提交 `e3a959d143d2930da93c96752ede7940a440f0db`。

## 数据之间是什么关系

```text
单细胞表达数据
  + 基因功能文字、调控关系、共表达关系、染色体位置先验
  -> 为每个细胞构建内部基因图
  -> 预训练 Cell-GraphCompass/CGCompass
  -> 批次校正、细胞注释、GRN 推断和扰动预测
```

这几类资源不能混为一谈：

- `ScCompass-h50M` 是论文报告的 5000 万以上人类细胞预训练语料，也是 ScCompass-126M 的子集；公开页面没有给出可追踪的完整细胞 ID 清单和统一下载包，因此状态是 `external/not-publicly-packaged`。
- `raw/scData.zip` 是 Zenodo 发布的约 2.64 GB **处理后训练/测试数据和权重包**，不是完整的 5000 万细胞原始语料。
- NCBI Gene、TFTG/TRRUST、PCC 共表达边和染色体邻近边是构图先验，不是下游评测数据。
- PCortex、PBMC、COVID-19、MS、Myeloid、hPancreas、Norman 等属于下游任务数据；只有能由官方 README 或代码追踪的入口才登记为可用。

## 使用

只读取 Zenodo 元数据并下载小型 `Readme.txt`：

```powershell
cd datasets/cell_graph_compass
python scripts/download_zenodo.py
python scripts/verify_files.py
```

明确接受约 2.64 GB 下载后再执行：

```powershell
python scripts/download_zenodo.py --include-large
python scripts/verify_files.py --require-large
python scripts/extract_scdata.py
python scripts/inspect_datasets.py raw/scData
```

`raw/`、压缩包、模型权重和大型表达矩阵均被仓库根 `.gitignore` 排除。下载日期、API 返回的真实文件大小和 MD5 会写入 `raw/zenodo_manifest.local.json`，这个本机记录同样不会提交。

本次网络会话已续传到 224,934,924 / 2,642,248,462 bytes 后安全中断；`.part` 可由同一命令继续，不会被误报为完成文件。当前状态见 [`download_status.json`](download_status.json)。

## 许可说明

官方代码仓库与 Zenodo 文件可能采用不同许可。Zenodo 记录页面未明确呈现一个可据此重新分发整个 `scData.zip` 的许可证，所以本仓库不镜像该包；使用或公开小样例前必须再次核对记录与其中数据各自的来源条款。
