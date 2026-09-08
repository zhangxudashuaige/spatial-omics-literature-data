# 数据字典

## Chen / PopAlign PBMC 药物扰动数据

| 字段 | 说明 |
|------|------|
| cell_id | 细胞唯一标识 |
| sample_id | 样本标识 |
| donor_id | 供体标识（如有） |
| condition | 实验条件（药物处理或对照） |
| drug | 药物名称 |
| dose | 药物剂量（如有） |
| cell_type | 细胞类型注释 |
| batch | 批次信息 |
| n_genes | 每个细胞检测到的基因数 |
| total_counts | 每个细胞总计数 |

## Perez SLE PBMC 疾病队列

| 字段 | 说明 |
|------|------|
| cell_id | 细胞唯一标识 |
| sample_id | 样本标识（354个样本） |
| donor_id | 供体标识（261名供体）；不能将重复样本当作独立供体 |
| disease_status | 疾病状态（SLE / healthy） |
| cell_type | 细胞类型注释 |
| batch | 批次信息 |
| n_genes | 每个细胞检测到的基因数 |
| total_counts | 每个细胞总计数 |

## RISE 预处理后参考规模（仅用于核对）

| 数据集 | 细胞数 | 基因数 | 条件数 |
|--------|--------|--------|--------|
| Chen / PopAlign PBMC | 29,433 | 9,461 | 46 |
| Perez SLE PBMC | 1,263,673 | 2,161 | N/A |

注意：这些规模是 RISE 预处理后的参考值，不代表原始下载文件维度。实际维度以下载文件检查结果为准。

## 表达值类型区分

- **原始计数 (raw counts)**: 整数，非负，来自测序reads计数
- **归一化表达 (normalized)**: 可能为小数，可能含负值（log2/z-score），来自作者处理
- 转换为 AnnData 时必须记录原始表达值类型，不将归一化表达误存成原始计数
