# SpatialVista 的 13 个数据来自哪里

SpatialVista 是可视化软件；下面 13 项是软件平台整理后的展示数据。真正需要下载原始数据或完整处理后数据时，应优先回到原论文的数据仓库。

| # | SpatialVista 数据 | 点/细胞数 | 原始研究 | 数据入口 |
|---:|---|---:|---|---|
| 1 | 成年小鼠 1，MERFISH，冠状切 | 3,812,698 | Zhang et al. 2023 | [Allen Zhuang-ABCA-1](https://alleninstitute.github.io/abc_atlas_access/descriptions/Zhuang-ABCA-1.html) |
| 2 | 成年小鼠 2，MERFISH，冠状切 | 1,654,566 | Zhang et al. 2023 | [Allen Zhuang-ABCA-2](https://alleninstitute.github.io/abc_atlas_access/descriptions/Zhuang-ABCA-2.html) |
| 3 | 成年小鼠 3，MERFISH，矢状切 | 2,055,846 | Zhang et al. 2023 | [Allen Zhuang-ABCA-3](https://alleninstitute.github.io/abc_atlas_access/descriptions/Zhuang-ABCA-3.html) |
| 4 | 成年小鼠全脑 Stereo-seq | 3,996,246 | Han et al. 2025 | [处理后数据](https://doi.org/10.12412/BSDC.1699433096.20001)；原始数据 `CNP0003837` |
| 5 | 小鼠胚胎 E11.5 | 6,866,495 | Cheng et al. 2024 | [MOSTA 下载页](https://db.cngb.org/stomics/mosta/download/) |
| 6 | 小鼠胚胎 E7.5，重复 1 | 12,923 | Xie et al. 2025 | [SpatialVista 展示](https://yanglab.westlake.edu.cn/spatialvista/vis)；原始 accession 待核验 |
| 7 | 小鼠胚胎 E7.5，重复 2 | 7,953 | Xie et al. 2025 | [SpatialVista 展示](https://yanglab.westlake.edu.cn/spatialvista/vis)；原始 accession 待核验 |
| 8 | 小鼠胚胎 E7.75，重复 1 | 20,584 | Xie et al. 2025 | [SpatialVista 展示](https://yanglab.westlake.edu.cn/spatialvista/vis)；原始 accession 待核验 |
| 9 | 小鼠胚胎 E7.75，重复 2 | 23,349 | Xie et al. 2025 | [SpatialVista 展示](https://yanglab.westlake.edu.cn/spatialvista/vis)；原始 accession 待核验 |
| 10 | 小鼠胚胎 E8.0，重复 1 | 10,735 | Xie et al. 2025 | [SpatialVista 展示](https://yanglab.westlake.edu.cn/spatialvista/vis)；原始 accession 待核验 |
| 11 | 小鼠胚胎 E8.0，重复 2 | 26,846 | Xie et al. 2025 | [SpatialVista 展示](https://yanglab.westlake.edu.cn/spatialvista/vis)；原始 accession 待核验 |
| 12 | 小鼠胚胎 E9.5 | 641,290 | Cheng et al. 2024 | [MOSTA 下载页](https://db.cngb.org/stomics/mosta/download/) |
| 13 | 人 CS8 原肠胚 | 37,226 | Xiao et al. 2024 | [GSA-Human HRA005567](https://ngdc.cncb.ac.cn/gsa-human/browse/HRA005567) |

## 五篇来源论文

1. [成年小鼠全脑 MERFISH 图谱](https://doi.org/10.1038/s41586-023-06808-9)
2. [小鼠全脑 Stereo-seq 图谱](https://doi.org/10.1016/j.neuron.2025.02.015)
3. [E9.5/E11.5 小鼠胚胎三维转录组](https://doi.org/10.1101/2024.08.17.608366)
4. [E7.5–E8.0 小鼠数字胚胎](https://doi.org/10.1016/j.cell.2025.05.035)
5. [人原肠胚三维重建](https://doi.org/10.1016/j.cell.2024.03.041)

## 口径提醒

- “点/细胞数”来自 SpatialVista 当前公开接口，是展示对象的数量，不一定等于原论文质控后的细胞数。
- MERFISH 的约 1,100 个直接测量基因与全转录组推断值应区分；查看某个基因前要确认它属于实测还是推断。
- `.h5ad` 通常是已经整理好的 AnnData 对象，不是显微镜原始图像或 FASTQ。
- Zhang et al. 2023 原始论文还有第 4 只小鼠 `Zhuang-ABCA-4` 以及原始图像、scRNA-seq 参考、推断表达等资源；它们不属于 SpatialVista 的 13 个展示条目，已在该论文目录的 `resources.csv` 中另行完整建档。
