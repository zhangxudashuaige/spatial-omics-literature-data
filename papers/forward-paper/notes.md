# 阅读与复现笔记

- 论文 v2 没有公开可验证的完整 FORWARD 代码，TI（Topological Impact）公式未完全公开。
- Supplemental Dataset 1–3 需要从论文补充材料单独取得，当前仓库不包含。
- 当前仓库首先是"数据索引与预处理项目"，不是完整模型复现。
- 34 基因签名训练数据包含 7 个队列，总样本数约 322（23+61+24+23+101+43+47）。
- 独立验证数据包含 9 个队列，部分队列的样本数和响应标签状态为 pending，需下载后确认。
- GSE73661 同时出现在训练、验证和布尔网络训练中，需注意数据泄漏风险。
- 特别需要检查的重复样本对：
  - GSE12251 与 GSE23597（UC Infliximab 患者可能重叠）
  - GSE14580 与 GSE16879（UC Infliximab 患者可能重叠）
- 检查方法：优先比较 GSM 编号；必要时比较表达矩阵相关性或哈希。
- 基因标识类型可能混合（Affymetrix 探针 ID、Gene Symbol、Entrez ID），需用 harmonize_gene_ids.py 统一转换为 Gene Symbol。
- E-MTAB-7604 从 EMBL-EBI BioStudies 下载，不使用 GEO。
- 大型表达矩阵和原始数据不提交 GitHub，使用 .gitignore 排除。
- 如确实需要版本管理大型数据，优先使用 DVC，不默认使用 Git LFS。
- 小型示例 data/examples/example_expression.csv（10样本×20基因）仅用于演示，不能用于复现论文指标。
