# Fang et al.（2025）Cell-GraphCompass

论文：**Cell-GraphCompass: modeling single cells with graph structure foundation model**，*National Science Review* 12(10)，nwaf255。

- DOI：https://doi.org/10.1093/nsr/nwaf255
- 正式论文：https://academic.oup.com/nsr/article/12/10/nwaf255/8172492
- 预印本：https://www.biorxiv.org/content/10.1101/2024.06.04.597354v1
- 代码：https://github.com/epang-ucas/Cell-Graph-Compass
- 数据：https://zenodo.org/records/14650474
- 本仓库数据模块：[`datasets/cell_graph_compass/`](../../datasets/cell_graph_compass/)

本记录保存论文、数据来源、固定代码版本和复现边界，不提交 2.6 GB 的 `scData.zip`。公开 `scData.zip` 是处理后的训练/评测资料包，不等同于完整的 ScCompass-h50M 原始预训练语料。

## 数据关系

单细胞表达 + 基因描述/调控/共表达/染色体位置先验 → 细胞内部基因图 → CGCompass 预训练 → 批次校正、细胞注释、GRN 与扰动预测。
