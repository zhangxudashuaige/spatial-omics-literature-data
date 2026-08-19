# H5AD 结构检查

## 当前状态

六个真实 H5AD 尚未在本机下载成功，因此下列项目仍待 `inspect_h5ad.py` 实际读取：

- `adata.shape`
- `X` 的 dtype、稀疏/稠密状态
- `obs`、`var`、`obsm`、`uns`、`layers` 的键
- `raw` 是否存在
- 细胞类型、胚层、切片、阶段、cluster 候选字段
- 二维与三维坐标位置
- 原始 UMI 或归一化表达层

## 为什么不能根据 GEO 文字直接判断

GEO 样本页说 H5AD 的“行是基因、列是单细胞”，但 AnnData API 通常把第一维定义为 `obs`、第二维定义为 `var`，常见语义是细胞 × 基因。实际文件可能经过转置、使用非标准对象或网页描述不严谨；只有 `anndata.read_h5ad(..., backed='r')` 的真实 `shape`、`obs_names` 和 `var_names` 能解决这个问题。

下载后运行 `python scripts/inspect_h5ad.py` 会自动重写本文件，写入逐样本验证结果。
