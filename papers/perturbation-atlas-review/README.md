# Perturbation Cell and Tissue Atlas 综述

论文：**Toward a foundation model of causal cell and tissue biology with a Perturbation Cell and Tissue Atlas**。

- 综述：https://doi.org/10.1016/j.cell.2024.07.035 (2024, Cell)
- 本仓库数据模块：[`datasets/perturbation-atlas/`](../../datasets/perturbation-atlas/)

这是2024年的综述，不是一个新发布的统一数据集。本项目定位为"综述引用数据的分类索引、下载与查看工具"，不声称复现了一个论文模型。

综述涵盖七类核心扰动数据：
1. **基因扰动**：Dixit 2016、Norman 2019（CRISPRa）、Replogle 2022（大规模CRISPRi）
2. **药物扰动**：sci-Plex
3. **RNA与蛋白多组学扰动**：Perturb-CITE-seq
4. **图像表型**：Funk 2022
5. **类器官扰动**：CHOOSE
6. **胚胎与体内扰动**：Saunders 2023 / zscape
7. **压缩扰动**：Compressed Perturb-seq

平台与工具：scPerturb（扰动数据库）、CausalBench（基因网络推断评测）。

已有数据优先复用（Norman/Replogle/sci-Plex/Dixit 已在 gears、perturbnet、scperturb、cellcap、xcell 等模块中登记），新增缺失条目，通过 `manifests/provenance.csv` 记录数据来源关系。
