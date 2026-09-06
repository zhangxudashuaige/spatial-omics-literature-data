# PerturbNet 论文

论文：**PerturbNet**（多模态扰动预测模型）。

- 论文：<https://doi.org/10.1038/s44320-025-00131-3>
- 官方代码：<https://github.com/welch-lab/PerturbNet>
- 作者数据和模型：<https://huggingface.co/cyclopeta/PerturbNet_reproduce>
- 本仓库数据模块：[`datasets/perturbnet/`](../../datasets/perturbnet/)

PerturbNet 是一个多模态扰动预测框架，支持三种任务：药物扰动（SMILES+剂量+细胞背景）、基因扰动（GO功能向量+细胞背景）、蛋白质突变（氨基酸序列嵌入+细胞背景）。

本条目保存 PerturbNet 使用的预训练数据（ZINC、GO、UniParc/ESM）、药物扰动数据（LINCS、sci-Plex）、CRISPR基因扰动数据（Norman）、蛋白质突变数据（Ursu TP53/KRAS、Jorge GATA1）、作者处理后的数据和模型（HuggingFace），以及下载脚本和检查工具。大型数据和模型权重不进入普通 Git 历史。
