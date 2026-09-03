# 阅读与复现笔记

- spatial domain不等于cell type；人工层级/病理标签只用于评价。
- 10x HDF5内部shape是gene×barcode，AnnData通常表示spot×gene。
- 官方教程数据含输入、预计算邻接矩阵和模型输出，不能全部称为原始数据。
- Google Drive数据未附独立许可；真实小样本不提交。
- 固定commit中SpaGCN包版本为1.2.7，代码MIT；原论文环境较旧，应单独固定兼容依赖。
