# 数据字典 (Data Dictionary)

## 核心概念

### expression matrix (表达矩阵)
- 维度: 细胞 × 基因
- 内容: 每个细胞中每个基因的表达量 (原始计数或归一化后的值)
- 存储: AnnData `.X` 或 `.layers["counts"]`
- 注意: 模型权重不是表达数据，模型预测结果也不是真实实验观测

### perturbation label (扰动标签)
- 内容: 该细胞接受的扰动类型
- 格式: 字符串，如 "GeneA"、"GeneA+GeneB"、"drug_X_10uM"、"TP53_M1"
- 存储: AnnData `.obs["perturbation"]` 或 `.obs["condition"]`

### SMILES (药物化学结构字符串)
- 内容: 药物分子的 SMILES 表示
- 用途: ChemicalVAE 的输入，编码药物结构
- 示例: "CC(=O)Oc1ccccc1C(=O)O" (阿司匹林)

### GO vector (基因功能二进制向量)
- 维度: 15988 维
- 内容: 基因的 Gene Ontology 功能注释，二进制表示
- 用途: GenotypeVAE 的输入，编码基因功能
- 来源: https://geneontology.org/

### protein sequence (突变后的氨基酸序列)
- 内容: 突变后的蛋白质氨基酸序列
- 用途: ESM 编码器的输入，编码蛋白质突变
- 示例: "MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGP..." (TP53)

### dose (药物剂量)
- 内容: 药物处理浓度
- 单位: 通常为 μM
- 用途: 药物扰动任务的输入之一

### cell type / cell line (细胞背景)
- 内容: 细胞类型或细胞系名称
- 示例: "K562"、"A549"、"HSPC"、"RPE-1"
- 用途: 所有任务的输入，指定扰动发生的细胞背景

### generated cells (模型生成的扰动后细胞)
- 内容: PerturbNet 模型生成的扰动后单细胞表达谱
- 注意: 这是模型输出，不是真实实验观测
- 用途: 预测未见扰动的响应

### control (对照)
- 内容: 未接受目标扰动的细胞
- 示例: "ctrl"、"control"、"vehicle"、"DMSO"
- 用途: 作为扰动效应的基线参考

## 三个任务的输入输出

### 药物扰动任务
| 输入 | 说明 |
|------|------|
| SMILES | 药物化学结构 |
| dose | 药物剂量 |
| cell background | 细胞类型/细胞系 |
| noise | 随机噪声 |
| **输出** | **扰动后单细胞表达矩阵** |

### 基因扰动任务
| 输入 | 说明 |
|------|------|
| GO vector | 基因功能向量 (15988维) |
| cell background | 细胞类型/细胞系 |
| noise | 随机噪声 |
| **输出** | **扰动后单细胞表达矩阵** |

### 蛋白质突变任务
| 输入 | 说明 |
|------|------|
| protein sequence embedding | 氨基酸序列嵌入 (ESM) |
| cell background | 细胞类型/细胞系 |
| noise | 随机噪声 |
| **输出** | **扰动后单细胞表达矩阵** |

## AnnData 结构约定

| 字段 | 内容 |
|------|------|
| `.X` | 表达矩阵 (细胞 × 基因) |
| `.layers["counts"]` | 原始整数计数 |
| `.obs["perturbation"]` | 扰动标签 |
| `.obs["cell_type"]` | 细胞类型 |
| `.obs["dose"]` | 药物剂量 (药物任务) |
| `.obs["control"]` | 是否对照 |
| `.var["gene_name"]` | 基因名称 |
| `.obsm["X_go"]` | GO 功能向量 (基因任务) |
| `.obsm["X_protein"]` | 蛋白质序列嵌入 (蛋白质任务) |
| `.uns["smiles"]` | SMILES 字符串 (药物任务) |

## 数据来源分类

| 分类 | 说明 | 示例 |
|------|------|------|
| 预训练数据 | 用于训练扰动编码器 | ZINC, GO, UniParc/ESM |
| 药物扰动数据 | 药物处理后的单细胞表达 | LINCS, sci-Plex |
| CRISPR 基因扰动 | CRISPRi/a 基因扰动 | Norman |
| 蛋白质突变数据 | 蛋白质编码突变 | Ursu TP53/KRAS, Jorge GATA1 |
| 作者处理后数据 | Hugging Face 上的整理数据 | data_paper, example_data |
| 模型权重 | 训练好的模型 | models, pretrained_model |
| 源数据 | 论文图表数据 | BioStudies |
