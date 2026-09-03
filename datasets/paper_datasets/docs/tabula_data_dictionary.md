# TABULA 数据字典与复现边界

## 预训练数据

论文称预训练数据来自 CELLxGENE Census，并报告：

- 约 15,000,000 个细胞；
- 196 个 studies；
- 133 个 tissues；
- 422 个 cell types；
- 23,156 个基因的训练词表；
- 每项研究约 1,200 个高变基因（HVG）；
- 8 个按组织划分的联邦客户端。

但论文使用的精确 Census build、完整 cell ID 清单和逐研究筛选结果尚未公开。因此这些数值是“论文报告的汇总”，不是本仓库已经下载并核验的数据资产。

## CELLxGENE 查询样例

`query_tabula_cellxgene.py` 只创建一个可审计的小型切片：

- `census_version`：用户必须显式指定日期版本；
- `organism`：固定支持 `Homo sapiens`；
- `tissue`、`cell_type`：可选的精确字符串筛选；
- `is_primary_data`：默认 true，排除 Census 中的重复副本；
- `max_cells`：最多导出的细胞数；
- 输出 `sample.h5ad` 和 `sample_manifest.json`。

`sample_manifest.json` 记录查询条件、版本、细胞数、基因数、创建时间和输出 SHA256。这个样例是 API 测试材料，不应称为论文精确预训练子集。

## `vocab.json`

固定来源：`aristoteleo/tabula@65b5f7ebf36a534da42de94570c108539af05541/resource/vocab.json`。

结构是：

```json
{
  "GENE_OR_FEATURE_NAME": 12345
}
```

它只是一份 token 字典。当前文件有 60,697 个映射；与论文报告的 23,156 基因训练词表存在差异，原因尚未由官方复现材料解释，故标记为待解析。

## 下游任务名称

| 用途 | 论文中的数据名 | 当前处理 |
|---|---|---|
| Imputation | PBMC5K、Jurkat、Melanoma、hPancreas | 只登记；精确来源/版本/预处理 unresolved |
| Perturbation | Adamson、Norman、Replogle | 只登记；精确来源/版本/预处理 unresolved |
| Annotation | hPancreas、Myeloid、Cell Lines | 只登记；精确来源/版本/预处理 unresolved |

同名数据集可能存在多个发布版、不同细胞筛选和不同归一化结果。在官方复现仓库给出明确映射前，自动下载任意“看起来相同”的版本会破坏可追溯性，因此本项目禁止这样做。

## 使用限制

- TABULA 代码仓库当前许可证是 **Non-Commercial License**，不是 MIT；使用代码或复制资源前需遵守非商业限制。
- CELLxGENE Census 汇聚许多来源数据，具体数据的许可证/使用条件可能因源数据集而不同。公开任何查询样例前仍要核对对应 source dataset 的条款。
- 官方 Census Python API 当前支持 Linux/macOS Python 3.10–3.12，不支持原生 Windows；Windows 用户应使用 WSL2、容器或 Linux 计算环境。
