# Roohani et al.（2022）GEARS

论文：**GEARS: Predicting transcriptional outcomes of novel multi-gene perturbations**。

- 论文：<https://doi.org/10.1038/s41587-023-01905-6>
- 官方代码：<https://github.com/snap-stanford/GEARS>
- 本仓库数据模块：[`datasets/gears/`](../../datasets/gears/)

GEARS 是一个图神经网络模型，用于预测单基因和多基因扰动后的转录组响应。它结合了基因-基因相互作用图和生物学先验知识，能够预测训练集中未见过的扰动组合。

本条目保存 GEARS 论文使用的多套扰动数据集（Norman、Adamson、Dixit 等）、知识图谱（GO 共表达、GO 相似度）、下载脚本、检查工具和最小复现流程。大型表达矩阵和模型权重不进入普通 Git 历史。
