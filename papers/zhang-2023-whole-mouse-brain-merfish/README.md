# Zhang et al. (2023)：成年小鼠全脑 MERFISH 图谱

## 文献信息

- 题目：Molecularly defined and spatially resolved cell atlas of the whole mouse brain
- 期刊：Nature（2023）
- DOI：https://doi.org/10.1038/s41586-023-06808-9
- 对应 SpatialVista 数据：`Zhuang-ABCA-1`、`Zhuang-ABCA-2`、`Zhuang-ABCA-3`

## 数据是什么

研究在成年小鼠脑连续薄切片上进行 MERFISH，直接原位检测约 1,100 个目标基因，并结合单细胞转录组参考进行细胞类型注释和全转录组层面的推断。因而“MERFISH 实测基因”和“模型推断基因”不是同一种证据，分析具体基因时必须区分。

SpatialVista 将连续二维切片的细胞坐标整理为三维点云；它展示的是处理后对象，不是显微镜原始图像。

## 数据入口

- [Zhuang-ABCA-1 数据说明与下载](https://alleninstitute.github.io/abc_atlas_access/descriptions/Zhuang-ABCA-1.html)
- [Zhuang-ABCA-2 数据说明与下载](https://alleninstitute.github.io/abc_atlas_access/descriptions/Zhuang-ABCA-2.html)
- [Zhuang-ABCA-3 数据说明与下载](https://alleninstitute.github.io/abc_atlas_access/descriptions/Zhuang-ABCA-3.html)
- [Allen 数据读取教程](https://alleninstitute.github.io/abc_atlas_access/notebooks/zhuang_merfish_tutorial.html)
- [Brain Image Library 原始图像和处理文件](https://doi.org/10.35077/act-bag)

## 标签

`organism:mouse` · `tissue:brain` · `modality:merfish` · `atlas:whole-brain` · `source:allen-brain-cell-atlas`
