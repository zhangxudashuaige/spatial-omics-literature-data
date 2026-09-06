# 阅读与复现笔记

- GEARS 官方提供 `PertData` 类加载预处理数据，支持 `norman`、`adamson`、`dixit` 等数据名称。
- Replogle 数据的官方加载名称需以 GEARS 当前版本为准，不自行猜测不存在的名称。
- 模型训练使用 `simulation` 划分，seed=1，batch_size=32，epochs=20。
- 评估指标包括 Top-20 DE MSE、Pearson、方向错误率、Precision@10、遗传相互作用 R²、ARI、NMI。
- 知识图谱有两种：GO 条目 Jaccard 相似度图和训练集基因 Pearson 共表达图。
- 大型 h5ad 数据和模型权重不进入普通 Git，通过下载脚本重新获取。
