# 阅读与复现笔记

- scPerturb 数据通过 Zenodo 分发，RNA+蛋白质记录为 13350497，ATAC 记录为 7058382。
- 数据分类包括 genetic_rna、drug_rna、multimodal_rna_protein、atac、developmental_or_cytokine。
- 不默认下载全部 43GB，首先下载 AdamsonWeissman2016_GSM2406675_10X001.h5ad（约34.6MB）。
- NormanWeissman2019_filtered.h5ad 约698.7MB，根据磁盘空间选择。
- E-distance 分析推荐使用维护活跃的 pertpy；如同时使用 scperturb 包，记录二者版本及结果差异。
- 最小示例 6细胞×4基因已生成（examples/minimal_perturbation.h5ad，30KB），包含 control/GeneA/GeneB/组合扰动。
- 下载后使用官方 MD5 校验；大型 h5ad 不进入普通 Git。
