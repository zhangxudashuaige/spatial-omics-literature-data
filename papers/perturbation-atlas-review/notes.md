# 阅读与复现笔记

- 这是2024年Cell综述，不是新发布的统一数据集。项目定位为"综述引用数据的分类索引、下载与查看工具"。
- 已有数据优先复用：Norman（cellcap/gears/perturbnet/scperturb）、Replogle（gears/xcell）、sci-Plex（perturbnet）、Dixit（gears）、scPerturb（scperturb模块）。
- 新增登记：Perturb-CITE-seq（SCP1064）、Funk 2022图像（S-BIAD394）、CHOOSE类器官（Zenodo 7083558）、Saunders/zscape（GSE202639）、Compressed Perturb-seq（FR-Perturb）、CausalBench。
- 通过 `manifests/provenance.csv` 记录 original→processed→subset→harmonized→benchmark 关系，特别关联 Norman、Replogle、sci-Plex 与 scPerturb 中的对应版本，以及 CausalBench 与 Replogle 数据的关系。
- 不默认跨研究去批次，不把缺失标签补成对照，保留供者、样本、胚胎、实验批次及组合扰动信息。
- 只有检查过文件内容后，才能标记原始计数或标准化表达。
- 混合液滴不能默认当成单个细胞（Compressed Perturb-seq）。
- 扩展待核实列表（pending）：Perturb-ATAC、Perturb-SHARE-seq、Perturb-map、Perturb-FISH、E3连接酶Perturb-seq、小鼠脑in vivo Perturb-seq。从综述参考文献定位原论文后核对数据入口。
