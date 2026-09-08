# DynaCLR 论文

论文：**DynaCLR**（基于动态对比学习的细胞图像表示方法）。

- 论文：https://arxiv.org/abs/2410.11281v2
- 本仓库数据模块：[`datasets/dynaclr/`](../../datasets/dynaclr/)

DynaCLR 是一个基于动态对比学习的细胞图像表示方法，用于活细胞成像数据的自监督学习。

本条目保存三类数据（分别建立记录，不混合）：
1. **ALFI 细胞周期数据**（figshare 23798451，对应论文 s41597-023-02540-1）
2. **Microglia / DynaMorph 数据**（GitHub mehta-lab/dynamorph + Google Drive 示例）
3. **DynaCLR 感染与细胞器演示资源**（Google Drive）

软件版本（单独记录）：VisCy（代码）、napari-iohub（可视化）、ultrack（追踪）、waveorder（相位重建）。

当前先整理数据，不要求训练完整模型。
