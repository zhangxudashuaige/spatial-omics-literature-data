# PRESAGE 论文

论文：**PRESAGE**（多来源基因先验融合的扰动响应预测方法）。

- 论文：https://doi.org/10.1101/2025.06.03.657653 (2025预印本)
- 官方代码：https://github.com/Genentech/PRESAGE
- Zenodo 缓存：https://zenodo.org/records/15587986
- 本仓库数据模块：[`datasets/presage/`](../../datasets/presage/)

**归类**: 基因扰动响应预测／多来源基因先验融合

PRESAGE 融合多来源基因先验（语义嵌入、知识图、DepMap等）进行基因扰动响应预测。

本条目分类整理：
1. 实验表达数据（5个h5ad + GSE264667 + scPerturb）
2. 来源嵌入（GenePT等）
3. 处理后的平均响应
4. 基因映射与缺失信息掩码
5. 训练验证测试划分
6. 代码与评估工具

**资源复用**：Replogle（gears/xcell）、scPerturb（scperturb）、DepMap（xcell）、GenePT/STRING（adapert），通过 `reuse_resource_map.csv` 关联，不重复下载大文件。

暂时不训练模型。
