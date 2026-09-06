# Wu et al.（2025）PerturbQA

论文：**Contextualizing Biological Perturbation Experiments through Language**。

- 论文：<https://arxiv.org/abs/2502.21290>
- 官方代码：<https://github.com/genentech/PerturbQA>
- 补充数据：<https://doi.org/10.5281/zenodo.14915312>
- 本仓库数据模块：[`datasets/perturbqa/`](../../datasets/perturbqa/)

PerturbQA 是一个将生物扰动实验上下文化的语言模型框架。它将单细胞 CRISPRi 扰动数据转化为问答任务，包括差异表达（DE）、变化方向（direction）和基因集富集（GSE）三类任务，并结合生物知识图谱和基因自然语言摘要，通过 Summer 模型进行检索增强预测。

本条目保存 PerturbQA 基准数据（K562/RPE1/HepG2/Jurkat）、知识图谱、基因摘要、Summer 及消融模型输出、下载脚本和检查工具。大型 zip 和解压后数据不进入普通 Git 历史。
