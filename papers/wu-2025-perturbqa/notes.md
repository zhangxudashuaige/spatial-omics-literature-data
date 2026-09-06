# 阅读与复现笔记

- PerturbQA 数据关系：原始单细胞表达矩阵 → 统计检验 → PerturbQA 标签 → 联合知识图谱和基因摘要 → Summer 预测 → 结果评估。
- 官方代码仓库提供加工后的基准数据，不重新处理原始百万级单细胞矩阵。
- 任务类型：differential expression (DE)、direction of change、gene set enrichment (GSE)。
- 细胞系：K562、RPE1、HepG2、Jurkat、K562_set。
- Zenodo 补充数据（14915312）包含 kg.zip、gene_summary.zip、summer_outputs.zip、summer_enrichment.zip、llm-nocot.zip、llm-noretrieve.zip、results.zip。
- 许可证：官方代码为 Genentech Non-Commercial Software License 1.0；PerturbQA 数据和模型输出为 CC BY 4.0；CORUM 为 CC BY-NC 4.0；其他知识图谱保留各自来源许可证。
- 大型 zip 和解压后数据不进入普通 Git，通过 scripts/download_data.py 自动下载。
- 如果下载链接、实际压缩包名称或文件格式与论文描述不一致，以 Zenodo 和官方 GitHub 当前页面为准，并在 README 中记录差异。
