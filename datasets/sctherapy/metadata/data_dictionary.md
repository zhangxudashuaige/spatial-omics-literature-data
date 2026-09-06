# 数据字典 (Data Dictionary)

## 概述

本文档定义 scTherapy 数据项目中使用的关键字段、数据类型和文件格式。

## 单细胞数据字段

### Seurat 对象元数据 (.meta.data / .obs)

| 字段 | 类型 | 说明 |
|------|------|------|
| patient | character | 患者编号 (如 Patient_5, Patient_6, Patient_12) |
| cancer_type | character | 癌种 (AML / HGSC) |
| cell_type | character | 细胞类型注释 |
| malignant | logical | 是否为恶性细胞 (TRUE/FALSE) |
| clone | character | 克隆编号 (恶性细胞亚群) |
| nCount_RNA | numeric | 每个细胞的总 UMI 数 |
| nFeature_RNA | integer | 每个细胞检测到的基因数 |
| percent.mt | numeric | 线粒体基因比例 (%) |
| batch | character | 批次/样本编号 |
| treatment | character | 处理条件 (如药物名称) |
| dose | numeric | 药物剂量 |
| timepoint | character | 时间点 |

### 表达矩阵

| 字段 | 说明 |
|------|------|
| counts | 原始 UMI 计数矩阵 (基因 × 细胞) |
| data | 归一化后的表达矩阵 (log-normalized) |
| scale.data | 缩放后的表达矩阵 (z-score) |

## 模型训练数据字段

### LINCS (药物诱导表达)

| 字段 | 说明 |
|------|------|
| pert_iname | 药物名称 |
| cell_id | 细胞系 |
| pert_dose | 药物剂量 (μM) |
| pert_time | 处理时间 (小时) |
| sig_id | 签名 ID |
| z_scores | 基因表达 z-score 向量 |

### PharmacoDB (剂量-反应)

| 字段 | 说明 |
|------|------|
| drug_name | 药物名称 |
| cell_line | 细胞系 |
| dose | 药物剂量 |
| viability | 细胞存活率 (%) |
| IC50 | 半抑制浓度 |
| AUC | 剂量-反应曲线下面积 |

### PubChem (药物结构)

| 字段 | 说明 |
|------|------|
| CID | PubChem 化合物 ID |
| smiles | SMILES 字符串 |
| molecular_weight | 分子量 |
| fingerprint | 分子指纹 (Morgan/ECFP) |
| descriptors | 分子描述符 |

## 患者预测输出字段

| 字段 | 说明 |
|------|------|
| patient_id | 患者编号 |
| clone_id | 克隆编号 |
| drug_name | 预测药物 |
| predicted_response | 预测响应值 |
| predicted_viability | 预测存活率 |
| combination | 组合治疗方案 |
| synergy_score | 协同作用评分 |
| confidence | 预测置信度 |

## 文件格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| Seurat object | .rds | R Seurat 对象，包含表达矩阵和元数据 |
| AnnData | .h5ad | Python anndata 对象 |
| Gene expression | .gct | LINCS 表达矩阵格式 |
| Sparse matrix | .mtx | Matrix Market 稀疏矩阵 |
| FASTA/Q | .fastq.gz | 原始测序数据 |
| Drug structure | .sdf | PubChem 结构数据 |
| Table | .csv/.tsv | 表格数据 |

## 受控数据

EGA 受控数据不包含在本仓库中。访问需通过 EGA 申请：
- 注册 EGA 账号
- 提交数据访问申请 (DAC)
- 审批后使用 EGA Download Client 下载
