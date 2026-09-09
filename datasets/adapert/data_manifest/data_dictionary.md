# 数据字典

## 扰动实验数据

| 字段 | 说明 |
|------|------|
| cell_id | 细胞唯一标识 |
| sample_id | 样本标识 |
| perturbation | 扰动基因（guide靶基因） |
| guide_id | sgRNA标识 |
| cell_line | 细胞系（K562/RPE1/JURKAT/HEPG2） |
| condition | 实验条件（perturbed/control） |
| n_genes | 每个细胞检测到的基因数 |
| total_counts | 每个细胞总计数 |
| batch | 批次信息 |

## 知识图（STRING）

| 字段 | 说明 |
|------|------|
| protein1 | 蛋白1（Ensembl蛋白ID或Gene Symbol） |
| protein2 | 蛋白2 |
| combined_score | 综合置信度（0-1000） |
| evidence_channels | 证据来源（neighborhood/fusion/cooccurrence/coexpression/experimental/database/textmining） |

## 基因语义嵌入（GenePT）

| 字段 | 说明 |
|------|------|
| gene_key | 基因标识（Gene Symbol或Entrez ID） |
| embedding_dim | 嵌入维度 |
| model_name | 预训练模型名称 |
| resource_version | 资源版本 |

## 表达值类型区分

- **原始计数 (raw counts)**: 整数，非负
- **归一化表达 (normalized)**: 可能为小数，可能含负值
- **AdaPert处理子集**: 从原始数据筛选/预处理后的子集，与原始数据分开记录

## DEG 标签区分

- **实验标签**: 来自实验设计的扰动/对照标签
- **计算产生的DEG**: 通过差异表达分析计算得到
- **训练DEG**: 仅用于训练，不能借用测试扰动响应
- **测试DEG**: 单独保存，仅用于评价

## 基因角色区分

- **表达输出基因**: 用于表达矩阵输出的基因
- **图节点基因**: 仅作为知识图节点的基因（可能不在表达矩阵中）
- **嵌入键基因**: GenePT嵌入覆盖的基因
- 三者交集统计保存在 `results/gene_intersection_summary.csv`
