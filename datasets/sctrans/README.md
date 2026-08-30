# SCTrans 数据模块

本目录整理 [SCTrans（IJCAI 2024）](https://www.ijcai.org/proceedings/2024/0658.pdf) 使用的 7 个公开人类 scRNA-seq 数据集。SCTrans 没有产生新的实验数据；本模块保存来源、版本、下载和预处理记录，不把当前数据库里的同名新版悄悄当成论文版本。

## 数据和实验关系

- 主分类：Zheng68K、Baron、Xin、Segerstolpe、Muraro、MacParland、Lung。
- 跨平台胰腺：Baron、Xin、Segerstolpe、Muraro；统一保留 alpha、beta、delta、gamma 四类，每次三套训练、另一套测试。
- 类别不平衡：Zheng68K 选 4 类，训练数为 100、10000、100、10000，每类测试 100。
- 基因选择：Zheng68K，比较注意力选择与随机选择的基因子向量。
- 重建：Zheng68K、MacParland。
- 消融：Zheng68K、MacParland、Lung。

## 可复现边界

论文没有完整报告所有下载文件、基因统一、QC、归一化和标签映射细节。因此：

- `manifest.yaml` 同时记录原数据规模、论文报告规模和实际检查结果；三者不能混写。
- Lung 候选 Figshare 包确实描述 39,778 个健康肺单核且使用 10X Chromium v2，但尚未证明其 9 类映射就是 SCTrans 的精确输入，状态保持 `needs_verification`。
- Bioconductor `scRNAseq` 便于得到四套胰腺的标准对象，但它是一个可追踪的再分发/整理入口，不自动等于作者当年的精确处理版本。R 脚本会记录 Bioconductor 与 `scRNAseq` 版本。
- 原始数据和本仓库处理结果分别保存在 `raw/` 和 `processed/`，都不会进入普通 Git。

## 下载

```powershell
cd datasets/sctrans
python scripts/download_geo.py --accession GSE115469 --list-only
python scripts/download_geo.py --accession GSE115469 --download
Rscript scripts/download_pancreas_bioconductor.R
python scripts/inspect_datasets.py raw --output inspection.local.json
```

Zheng68K 的 10X 历史页面可能改变直链，脚本先解析/验证官方页面；也可以显式传入经核对的官方文件 URL。SRA `SRP073767` 只登记原始测序入口，默认不下载 FASTQ。

本次已从 10X 官方 CDN 下载 Cell Ranger 1.1.0 过滤矩阵压缩包（124,442,812 bytes）。解包后的 Matrix Market 真实维度为 **32,738 基因 × 68,579 barcode**，含 37,323,295 个非零项。论文使用 68,450 个有标签细胞，因此还需要作者当时的标签与筛选清单，不能把 68,579 个 barcode 直接说成 SCTrans 的最终输入。

## 处理记录要求

任何用于复现的处理都必须在运行日志中写清：基因 ID 统一、重复基因合并、无标签细胞、低质量过滤、线粒体比例、library-size normalization、`log1p`、共有基因、标签统一、随机种子和 80/20 划分。`align_genes.py` 与 `create_splits.py` 提供显式、可审计的实现，但不声称它们就是论文未披露的全部流程。

`sample/` 小样例固定随机种子，每类最多 10 个细胞、最多 500 个基因，只用于读写测试和 CI，不用于重现论文结果。
