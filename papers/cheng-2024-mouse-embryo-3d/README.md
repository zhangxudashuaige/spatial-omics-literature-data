# Cheng et al. (2024)：E9.5/E11.5 小鼠胚胎三维转录组

## 文献信息

- 题目：Three-dimension transcriptomics maps of whole mouse embryo during organogenesis
- 类型：bioRxiv 预印本（2024）
- DOI：https://doi.org/10.1101/2024.08.17.608366
- 对应 SpatialVista 数据：`4D_mouse_embryo_E9.5`、`4D_mouse_embryo_E11.5`

## 数据是什么

研究补充小鼠器官发生阶段 E9.5 与 E11.5 的三维空间转录组图谱，并通过连续切片重建胚胎三维结构。这里的“4D”指多个发育时间点上的三维空间图谱，并不是实时拍摄同一个胚胎的四维电影。

## 数据入口和已知大小

- [MOSTA 下载页](https://db.cngb.org/stomics/mosta/download/)
- `Mouse_E9.5_embryo.h5ad`：下载页标注约 821 MB
- `Mouse_E11.5_embryo.h5ad`：下载页标注约 6.68 GB

这些是处理后 AnnData 文件；同一下载页还包含切片表达矩阵、图像和其他更大的文件，下载前应逐项评估磁盘空间。

## 标签

`organism:mouse` · `tissue:embryo` · `modality:stereo-seq` · `stage:e9.5` · `stage:e11.5` · `source:mosta`
