# HEIST 数据字典与可复现边界

## 数据关系

HEIST 把空间组学表示成分层图：上层是**细胞空间图**，下层是每个细胞对应的**基因/蛋白共表达图**。官方项目页报告预训练共 22.3M cells、124 slices、15 organs；来源分别为 10x Genomics Xenium（13.3M）、Vizgen MERFISH（8.7M）和 SEA-AD MERFISH（约 360K）。这不是一个统一下载包。

## 官方代码实际期望的对象

核查固定 commit `b83615df17126581294b0ba3c8a3b30f7860c6ff` 的 `preprocessing.md`、`utils/preprocess.py` 和评估脚本后，预处理输出是 `torch.save()` 保存的 PyTorch Geometric `Data` 对象列表：

- `graphs[0]`：上层细胞图。`X` 是标准化空间坐标，不是表达矩阵；`edge_index` 是 Voronoi 空间邻接；`cell_type` 是编码标签；`cell_types` 保存类别名称。
- `graphs[1:]`：每个细胞一个下层基因/蛋白图。`X` 通常为 `(n_features, 1)` 表达/蛋白强度；`edge_index` 是按互信息构建的共表达边；`cell_type` 继承该细胞标签。
- 原始 AnnData 预处理至少使用 `adata.X`、`adata.obsm[spatial]`；代码默认/实际读取 `adata.obs.cell_type`。
- 预处理执行基因过滤、总量归一化到 `1e4`、`log1p`、MAGIC 插补、Voronoi 空间图和 GPU 互信息共表达图。

## 代码中出现的路径

| 数据 | 表征提取输入 | 评估输入 |
|---|---|---|
| SEA-AD | `data/pretraining/sea_preprocessed/*` | `data/sea_graphs_<model_suffix>.pt` |
| Lung Cancer | `data/merfish_lung_preprocessed/*` | `data/merfish_lung_<model_suffix>.pt` |
| DFCI | `data/space-gm/dfci/*` | `data/dfci_graphs_<model_suffix>.pt` |
| UPMC | `data/space-gm/upmc/*` | `data/upmc_graphs_<model_suffix>.pt` |
| Charville | `data/space-gm/charville/*` | `data/charville_graphs_<model_suffix>.pt` |
| Melanoma | `data/melanoma_lung_preprocessed/*` | `data/melanoma_preprocessed/R10C2.pt` |
| Placenta | `data/placenta_preprocessed/*` | `SCGFM/data/placenta/02021424.pt` |

这些是代码里的**期望路径**，不是公开下载链接。官方仓库没有提供一份把所有路径映射到原始 URL、文件版本、校验值和许可的完整 manifest，因此对应条目保持 `status: unresolved`。

## 检查脚本输出字段

`inspect_heist_sample.py` 统一报告：

- `expression_or_protein_shape`：AnnData `X` 或下层图特征堆叠后的逻辑形状；
- `coordinate_shape`：`obsm['spatial']` 等坐标，或上层图 `X/pos`；
- `cell_type_count`：标签去重数；
- `slice_count`、`patient_count`：从明确字段或对象属性统计；
- `clinical_labels`：只报告实际存在的 `pTR_label`、`primary_outcome`、`recurrence/recurred` 等字段；
- `spatial_graph`：上层图节点数、边数；
- `coexpression_graphs`：下层图个数及节点/边统计。

## 已发现的复现风险

- `preprocessing.md` 给出 `python utils/preprocess.py`，但实际文件主要暴露函数，不能把文档命令视为已验证的完整 CLI。
- 评估 shell 中出现 `eval_gene_inputation.py` 拼写，而实际文件为 `eval_gene_imputation.py`。
- Placenta 评估路径写成另一个项目式的 `SCGFM/data/...`；Melanoma 表征路径中含 `melanoma_lung_preprocessed`。运行前必须核实作者真实目录。
- `.pt/.pth` 使用 pickle，只有信任来源时才用 `torch.load`；优先下载并验证 `safetensors` 模型。
- 代码 README 的 CC BY 4.0 与 Hugging Face 模型卡的 MIT 是两个不同对象的许可声明，不能互相替代；生物数据仍需逐源核实许可。
