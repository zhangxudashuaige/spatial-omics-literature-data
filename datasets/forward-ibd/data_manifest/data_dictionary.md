# 数据字典

本文档解释 FORWARD-IBD 数据项目中各 CSV 文件的字段含义。

## 通用字段（training_cohorts.csv、validation_cohorts.csv、boolean_network_cohorts.csv）

| 字段 | 说明 |
|------|------|
| `dataset_id` | 数据集唯一标识（GEO accession 或 ArrayExpress accession） |
| `repository` | 数据存储库（GEO / ArrayExpress） |
| `species` | 物种（Homo sapiens） |
| `tissue` | 组织类型（colon / rectal mucosa 等） |
| `disease` | 疾病类型（IBD / UC / CD / UC+CD） |
| `treatment` | 治疗药物（Infliximab / Adalimumab / Ustekinumab / Vedolizumab / anti-TNF 等） |
| `cohort_role` | 队列角色（34_gene_signature_training / independent_validation / boolean_network_training） |
| `sample_count_reported` | 论文报告的样本数（如未确认则为 pending） |
| `expression_platform` | 表达检测平台（Affymetrix HG-U133 Plus 2.0 / Illumina 等） |
| `raw_url` | 原始数据下载链接 |
| `processed_url` | 处理后数据下载链接 |
| `response_label_available` | 治疗响应标签是否可用（yes / no / pending） |
| `notes` | 备注信息（重复样本警告、特殊说明等） |

## clinical_trial_sources.csv 字段

| 字段 | 说明 |
|------|------|
| `source_id` | 数据源唯一标识 |
| `source_name` | 数据源名称 |
| `source_type` | 数据源类型（clinical_trial_registry / drug_database / pathway_database 等） |
| `url` | 数据源网址 |
| `data_type` | 数据类型（临床试验信息 / 药物靶点 / 通路注释 等） |
| `access_level` | 访问级别（public / registered / restricted） |
| `license` | 许可证 |
| `notes` | 备注 |

## 数据分类说明

### A. 34基因签名训练数据
用于训练 FORWARD 的 34 基因签名模型，包含 7 个 IBD 治疗响应队列。
- 治疗药物：Infliximab、Adalimumab、Ustekinumab、Vedolizumab
- 总样本数：约 322（23+61+24+23+101+43+47）

### B. 独立验证数据
用于独立验证 34 基因签名和 FORWARD 预测性能，包含 9 个队列。
- 注意：GSE73661 同时出现在训练和验证中，需注意数据泄漏风险

### C. 原始IBD布尔网络数据
用于构建原始 IBD 布尔网络的训练数据，包含 3 个队列。
- GSE83687、GSE73661、GSE6731

### D. 临床试验和药物靶点数据
用于药物靶点优先级和临床试验信息查询的外部数据库。

### E. 论文产生的派生数据
- Supplemental Dataset 1：34 基因签名列表
- Supplemental Dataset 2：布尔网络拓扑
- Supplemental Dataset 3：药物靶点优先级结果
- 以上需从论文补充材料单独取得

## 重复样本检查重点

| 队列对 | 检查方法 | 原因 |
|--------|----------|------|
| GSE12251 vs GSE23597 | GSM 编号比较 → 表达矩阵相关性 → 哈希 | 可能共享 UC Infliximab 患者样本 |
| GSE14580 vs GSE16879 | GSM 编号比较 → 表达矩阵相关性 → 哈希 | 可能共享 UC Infliximab 患者样本 |

## 基因标识类型

不同队列可能使用不同的基因标识：
- Affymetrix 探针 ID（需转换为 Gene Symbol）
- Gene Symbol
- Entrez ID
- Ensembl ID

使用 `scripts/harmonize_gene_ids.py` 统一转换为 Gene Symbol。
