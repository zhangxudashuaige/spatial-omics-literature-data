# FORWARD 论文

论文：**FORWARD: A Learning Framework for Logical Network Perturbations to Prioritize Targets for Drug Development**。

- 论文：<https://doi.org/10.1101/2024.07.16.602603>
- 本仓库数据模块：[`datasets/forward-ibd/`](../../datasets/forward-ibd/)

FORWARD 是一个基于逻辑网络扰动的学习框架，用于优先排序药物开发靶点。它整合了 IBD（炎症性肠病）转录组数据、治疗响应数据和临床试验靶点数据，通过布尔网络拓扑影响（TI）分析来识别潜在的药物靶点。

**重要声明：论文 v2 没有公开可验证的完整 FORWARD 代码、TI 公式和全部补充表。**

- Supplemental Dataset 1–3 需要从论文补充材料单独取得
- 当前仓库首先是**"数据索引与预处理项目"**，不是完整模型复现
- 不声称已经复现 FORWARD

本条目保存 FORWARD 论文使用的 34 基因签名训练数据（7个队列）、独立验证数据（9个队列）、原始 IBD 布尔网络数据（3个队列）、临床试验和药物靶点数据，以及下载、检查、预处理和样本重叠检查工具。
