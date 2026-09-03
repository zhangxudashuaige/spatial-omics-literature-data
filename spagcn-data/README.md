# SpaGCN 数据资料模块

本目录为论文 **SpaGCN: Integrating gene expression, spatial location and histology to identify spatial domains and spatially variable genes by graph convolutional network** 整理七套论文数据和一套官方教程数据。

- 正式论文：<https://doi.org/10.1038/s41592-021-01255-8>
- 官方代码：<https://github.com/jianhuupenn/SpaGCN>
- 固定代码 commit：`dc7a1c26ea0fdf4dfe7064adc7699be141b4871f`
- 官方教程：<https://github.com/jianhuupenn/SpaGCN/blob/dc7a1c26ea0fdf4dfe7064adc7699be141b4871f/tutorial/tutorial.ipynb>
- 代码许可证：MIT；各实验数据许可证分别核实。

## SpaGCN 在做什么

SpaGCN 的主要任务是空间域分割（spatial domain segmentation）和空间变异基因（SVG）检测。空间域是表达、空间邻近关系以及可选组织图像共同定义的组织区域，不等同于细胞类型；同一空间域可以包含多种细胞，一种细胞类型也可能跨越多个域。

数据之间通过 spot/cell ID 连接：

```text
表达矩阵（spot/cell × gene）
       + 坐标表（ID、array x/y、pixel x/y）
       + 可选组织图像和scale factor
       ↓ 以共同ID严格对齐
图节点 = spot/cell
节点特征 = 基因表达
边 = 空间邻近关系
边权重 = 空间距离 + 可选的组织图像像素信息
       ↓ SpaGCN无监督训练
domain标签、domain概率、SVG和meta gene
```

人工皮层层级、病理区域或细胞类型注释只用于评价和解释，不参与无监督训练。

## 数据资产概览

| 数据 | 表达 | 坐标 | 图像 | 人工注释 | 状态 |
|---|---:|---:|---:|---:|---|
| Human pancreatic cancer ST | 是 | 是 | H&E | 病理注释 | GEO真实清单已登记；未下载715 MB归档 |
| Human DLPFC Visium | 是 | array+pixel | H&E | cortical layers | spatialLIBD/ExperimentHub；官方教程切片151673已部分下载检查 |
| Mouse brain posterior Visium | 是 | array+pixel | H&E+scale factors | 可选区域标签 | 10x入口已登记 |
| Mouse cortex Slide-seqV2 | 是 | 2D bead | 否 | 数据集提供 | Broad SCP815入口；下载需按门户条件 |
| Mouse visual cortex STARmap | 是 | 2D cell | 否 | layer/cell type | 官方资源入口已登记 |
| Mouse olfactory bulb ST | 是 | 位置编码 | H&E JPG | 未确认 | 官方Drive列出2个文件 |
| Mouse hypothalamus MERFISH | 是 | µm坐标 | 否 | cell class/cluster | Dryad单CSV约1.03 GB |
| Official tutorial data | 是 | array+pixel | 可选大图 | 教程结果非真值 | 与论文实验数据分开；部分本地下载 |

## 官方教程数据实检

Google Drive 根目录实际包含 `151673/` 与 `Mouse_brain/`：

- `151673`：`adj.csv` 315.7 MB、`expression_matrix.h5` 13.9 MB、`histology.tif` 508.7 MB、`positions.txt` 182 KB、`results.h5ad` 63.8 MB、`sample_data.h5ad` 66.1 MB。
- `Mouse_brain`：`MA1.h5ad` 119.8 MB、`MP1.h5ad` 119.2 MB，以及两张各约386 MB的组织图像。

本机只下载并检查 `151673/expression_matrix.h5` 与 `positions.txt`：

- 10x HDF5 矩阵保存为 gene × spot：33,538 genes × 4,992 barcodes；`data` 为 int32，9,120,826 个非零值。
- `positions.txt` 有4,992行，无表头；列为 barcode、tissue flag、array row、array column、full-resolution pixel row、pixel column。
- 表达 barcode 与坐标 barcode 数量一致。完整校验值见 `checksums.sha256`。
- 论文分析通常把 AnnData 表示为 spot × gene；方向转换必须明确，不能因HDF5内部shape顺序而误读。

## Windows PowerShell 使用

```powershell
cd spagcn-data
conda env create -f environment.yml
conda activate spagcn-data

# 查看GEO官方清单，不下载715MB归档
python scripts/download_geo.py --accession GSE111672 --list

# 检查本地151673表达和坐标
python scripts/inspect_spatial_data.py datasets/official_toy_data/raw/151673/expression_matrix.h5
python scripts/validate_spot_alignment.py `
  --expression-h5 datasets/official_toy_data/raw/151673/expression_matrix.h5 `
  --coordinates datasets/official_toy_data/raw/151673/positions.txt --no-header

# 检查标准Space Ranger/Visium目录并生成低分辨率叠加图
python scripts/inspect_10x_spatial.py <space_ranger_outs目录> --overlay results/spot_overlay.png
```

## 从输入到结果

官方详细教程先读取10x H5和坐标，把空间/像素坐标写入 `adata.obs`；随后用 `calculate_adj_matrix` 建图，`search_l` 与 `search_res` 选参数，`SpaGCN.train()` 训练，`predict()` 得到domain及概率，`refine()`按空间邻域平滑。最后 `rank_genes_groups()` 比较目标域与邻近域以筛选SVG，并可迭代构建meta gene。

结果目录只允许提交小型测试产生的 `domain_labels.csv`、`domain_probabilities.csv`、`svg_results.csv`、`meta_gene_results.csv`、`metrics.json` 和低分辨率示意图。`results.h5ad`、大邻接矩阵和论文完整输出不进入普通Git。

## 可复现性边界

- 原始实验数据与SpaGCN输出结果严格分开。
- Google Drive和部分网站没有独立、机器可读的数据许可证；真实抽样文件不重新分发，直到许可确认。
- Broad Portal可能需要接受条款或登录；脚本不会绕过权限。
- 10x网页下载地址可能随站点版本变化；脚本先列出官方页面候选链接，不猜文件名。
- 官方代码原始测试环境较旧；本目录环境用于数据检查。复现原论文指标建议单独创建兼容环境并固定软件版本。

## 引用

使用本模块时，请引用SpaGCN论文，并根据实际数据分别引用Moncada、Maynard、Stickels、Wang、Ståhl、Moffitt等原始研究及GEO/10x/Broad/Dryad数据入口。具体DOI记录在各数据集README和 `data_manifest.csv`。
