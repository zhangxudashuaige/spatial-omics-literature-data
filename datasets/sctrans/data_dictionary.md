# SCTrans 数据字典

不同平台的原始结构并不相同，因此本模块不规定一个虚构的统一列名。

| 概念 | 可能位置 | 核验规则 |
|---|---|---|
| 表达矩阵 | H5AD `X`、10X MTX、CSV 或 SingleCellExperiment assay | 检查 shape、稀疏性、dtype、非零基因和总表达 |
| 基因 ID | H5AD `var_names`、10X features/genes、CSV 首列 | 记录 Ensembl/符号类型；重复基因不静默合并 |
| cell ID | H5AD `obs_names`、10X barcode、CSV 列名 | 检查重复；跨文件连接前保留原 ID |
| cell type | `cell_type`/`label`/原研究注释表 | 保存原标签和统一标签两列 |
| donor | `donor`/`patient`/`individual` | 不从 barcode 猜测 |
| batch | `batch`/`sample`/`library` | 必须记录平台、样本和供体的区别 |

四套跨平台胰腺实验只保留 alpha、beta、delta、gamma 时，应另存一张标签映射表，并记录被排除细胞数。`align_genes.py` 默认对基因名取严格交集；发现重复基因会中止，要求用户明确选择 sum/mean/first 等聚合规则。`create_splits.py` 使用标签分层、默认 80/20、固定种子 `20260829`，这是本仓库的透明实现，不冒充论文未披露的原始划分。

