# Xiao et al. (2024)：人原肠胚三维重建

## 文献信息

- 题目：3D reconstruction of a gastrulating human embryo
- 期刊：Cell（2024）
- DOI：https://doi.org/10.1016/j.cell.2024.03.041
- 对应 SpatialVista 数据：`2024_cell_human_gastrulation`

## 数据是什么

研究对一个 Carnegie stage 8（CS8）人胚胎进行连续横切，使用 Stereo-seq 获得 62 个切片的空间转录组，并通过切片配准生成三维点云。论文质控后报告 38,562 个 spots；SpatialVista 当前展示 37,226 个点，说明展示版还存在筛选或版本差异。

## 数据和代码入口

- [GSA-Human：HRA005567](https://ngdc.cncb.ac.cn/gsa-human/browse/HRA005567)
- [分析代码：Zenodo](https://doi.org/10.5281/zenodo.10851179)

本条采用论文 Data and code availability 明确写出的 `HRA005567`。人胚胎数据涉及伦理和使用条件，即使页面显示公开，也应在再分析和再分发前阅读数据库条款。

## 标签

`organism:human` · `tissue:embryo` · `stage:cs8` · `modality:stereo-seq` · `development:gastrulation`
