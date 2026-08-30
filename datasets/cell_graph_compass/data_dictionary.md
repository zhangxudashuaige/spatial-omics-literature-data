# Cell-GraphCompass 数据字典

## 作者处理流程的输入

固定提交的 `scData/process_downstream.py` 要求 AnnData 至少提供：

| 字段 | 作用 |
|---|---|
| `adata.X` | 细胞 × 基因表达矩阵 |
| `adata.var_names` | 基因标识，随后与 `bioFeature_embs/vocab.json` 对齐 |
| `adata.obs['cell_type']` | 删除空标签并编码为下游监督标签 |
| `adata.obs['batch']` | 批次编码 |

默认选 1,200 个 HVG；原始计数是否需要 `log1p` 由 `data_is_raw` 控制。需要拆分时，官方脚本使用 `test_size=0.1`、`random_state=42`。

## 每个 LMDB cell 对象

官方代码将每个细胞序列化为字典：

| 键 | 含义/压缩类型 |
|---|---|
| `gene_list` | 基因词表 ID，转为 `torch.int16` |
| `values` | 表达 token，转为 `torch.int8` |
| `batch_id` | 批次整数 ID |
| `celltype` | 细胞类型整数 ID |
| `edge_index` | 细胞内部基因图的边 |
| `edge_attr_type` | 边类型，`torch.int8` |
| `edge_attr_corr` | 共表达相关性，`torch.float16` |
| `edge_attr_chromo` | 染色体距离属性，`torch.int8` |
| `idx` | 全局样本索引 |

构图组合 TF–靶基因、同染色体邻近和细胞/数据集共表达边；代码中的相关阈值为 `corr_thr=0.6`，染色体距离参数 `max_dis=50.0`。这些字段来自固定代码提交的实际实现，不代表 Zenodo 压缩包中每个成员都已完成运行时验证。

`vocab.json` 是基因词表；它不是表达矩阵。`pretrain_weights` 与 `downstream_weights` 是模型权重；也不是实验数据。

