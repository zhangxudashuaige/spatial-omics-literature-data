# Wei et al. (2026) - SpatialVista

## 文献信息

- 题目：SpatialVista as a unified ecosystem for high-performance visualization and exploration of 3D spatial transcriptomics data
- 类型：Correspondence
- 期刊：Nature Genetics
- DOI：https://doi.org/10.1038/s41588-026-02696-7
- 作者：Wenjie Wei, Lounan Li, Liyang Song, Wenhao Chen, Kai Wang, Minmin Guo, Jian Yang
- 机构：西湖大学生命科学学院；西湖实验室

## 这篇文章做了什么

SpatialVista 是面向细胞分辨率 3D 空间转录组数据的可视化生态，提供在线图库、跨平台桌面程序和 Jupyter/Python 小组件。核心功能包括 3D 点云、分类/连续属性着色、2D-3D 联动、ROI 选择、轴向查询和邻域组成汇总。

文章称在线平台当时收录 13 个公开数据集，共约 1,890 万个细胞。本文主要介绍软件和资源平台，并没有声明一个独立的新实验数据集；数据应按平台条目回溯到各原始研究和数据库。

本仓库在 2026-08-17 读取平台公开接口时仍得到 13 项，但合计为 19,166,757 个点/细胞。这里同时保留论文口径与当前平台口径，不强行把两个版本写成同一个数字。

## 代码与资源

- SpatialVista 平台及文档：https://yanglab.westlake.edu.cn/spatialvista
- Python/Jupyter 代码：https://github.com/JianYang-Lab/spatial-vista-py
- 代码许可证：BSD 3-Clause（文章中的声明；使用前仍应以仓库当前 LICENSE 为准）
- 补充材料：https://doi.org/10.1038/s41588-026-02696-7
- 13 个数据的中文对应表：[`dataset-sources.md`](dataset-sources.md)
- Jupyter 示例：[`notebooks/spatialvista_mouse_brain.ipynb`](notebooks/spatialvista_mouse_brain.ipynb)

## 标签

`topic:spatial-transcriptomics` · `topic:visualization` · `modality:3d-st` · `software:spatialvista` · `organism:multiple` · `tissue:multiple` · `year:2026` · `status:cataloged`

## 本地来源记录

- 原文件名：`s41588-026-02696-7.pdf`
- 原 PDF 不提交公开仓库；其版权/再分发许可需单独核实。
- 本地 SHA-256：`FFFD03668DB8C29743D435577D37522E14473F624084E5B2955287BEBF55333F`

## 当前已完成

- 已把在线平台的 13 个数据拆成 13 条记录，并对应到 5 篇原始数据论文。
- 已记录可确认的 accession、原始数据库下载入口、展示点数和检索标签。
- 没有查证到的原始 accession 明确标成“待核验”，没有凭空补写。

## 下一步

- 只下载当前分析真正需要的数据；每次下载后记录获取日期和 SHA-256。
- 为有价值的数据增加最小可运行的读取/质控 notebook 或脚本。
