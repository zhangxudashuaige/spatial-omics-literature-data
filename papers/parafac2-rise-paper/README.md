# PARAFAC2-RISE 论文

论文：**PARAFAC2-RISE**（基于PARAFAC2张量分解和RISE预处理的单细胞扰动分析方法）。

- 论文：https://doi.org/10.1016/j.cels.2025.101294
- 本仓库数据模块：[`datasets/parafac2-rise/`](../../datasets/parafac2-rise/)

PARAFAC2-RISE 结合 RISE（Robust Integration of Single-cell Experiments）预处理和 PARAFAC2 张量分解，用于分析跨条件/跨样本的单细胞转录组扰动数据。

本条目保存论文使用的两套实验数据：
1. **Chen / PopAlign PBMC 药物扰动数据**（figshare 11837097）：29,433细胞、9,461基因、46条件（RISE预处理后参考规模）
2. **Perez SLE PBMC 疾病队列**（GSE174188）：261供体、354样本、1,263,673细胞、2,161基因（RISE预处理后参考规模）

代码资源：RISE（包名 `scrise`）和 PARAFAC2，分开归档在 `code_refs/`。
