# Zhang et al. (2023)：成年小鼠全脑 MERFISH 图谱

## 文献信息

- 题目：Molecularly defined and spatially resolved cell atlas of the whole mouse brain
- 期刊：Nature（2023）
- DOI：https://doi.org/10.1038/s41586-023-06808-9
- 研究范围：4 只成年小鼠、245 张冠状或矢状切片、约 1,000 万个分割细胞

## 完整数据结构

这篇论文不是只有 SpatialVista 展示的三个三维对象。完整公开数据资产包括：

1. 四只小鼠 `Zhuang-ABCA-1/2/3/4` 的 MERFISH 数据。
2. 每只动物的 cell-by-gene 表达矩阵、细胞元数据和 Allen CCF 坐标。
3. Brain Image Library 中的原始/处理成像数据、codebook 和探针信息。
4. 用作参考的全脑 scRNA-seq FASTQ、处理后表达和细胞类型分类体系。
5. 根据 scRNA-seq anchor 计算的 MERFISH 细胞全转录组推断表达。
6. CELLxGENE 可下载/浏览的处理后 MERFISH 集合。
7. Nature 的 6 张补充表、各图 Source Data 和固定版本分析代码。

所有入口逐项记录在 [`resources.csv`](resources.csv)，四只动物记录在 [`datasets.csv`](datasets.csv)。

## 四只小鼠的处理后数据

| 数据集 | 性别 | 切片方向和数量 | 处理后细胞 | 表达矩阵 | 元数据 | CCF 坐标 |
|---|---|---|---:|---:|---:|---:|
| `Zhuang-ABCA-1` | 雌 | 147 张冠状切片 | 约 420 万 | 3.09 GB | 1.33 GB | 0.21 GB |
| `Zhuang-ABCA-2` | 雄 | 66 张冠状切片 | 约 190 万 | 1.30 GB | 0.57 GB | 0.08 GB |
| `Zhuang-ABCA-3` | 雄 | 23 张矢状切片 | 约 210 万 | 1.69 GB | 0.75 GB | 0.12 GB |
| `Zhuang-ABCA-4` | 雄 | 3 张矢状切片 | 约 22 万 | 0.16 GB | 0.08 GB | 0.01 GB |

上述官方处理组件合计约 9.39 GB，采用 CC BY 4.0。原始显微图像、scRNA-seq FASTQ 和推断矩阵不包含在这个合计中。

## MERFISH 与 scRNA-seq 的关系

MERFISH 使用两套非常相似的面板，分别直接检测 1,124 和 1,147 个基因，其中 1,122 个共同基因用于四只动物与 scRNA-seq 的整合。scRNA-seq 参考包含 5,322 个 clusters 和 338 个 subclasses，用于：

- 选择 MERFISH 面板中的标记基因；
- 把细胞类型标签转移到 MERFISH 细胞；
- 推断 MERFISH 没有直接检测的其他基因。

因此下载和分析时必须区分 `measured`（MERFISH 实测）与 `imputed`（根据 scRNA-seq 推断）。

## 数据入口

- [四只动物总说明](https://alleninstitute.github.io/abc_atlas_access/descriptions/Zhuang_dataset.html)
- [Zhuang-ABCA-1](https://alleninstitute.github.io/abc_atlas_access/descriptions/Zhuang-ABCA-1.html)
- [Zhuang-ABCA-2](https://alleninstitute.github.io/abc_atlas_access/descriptions/Zhuang-ABCA-2.html)
- [Zhuang-ABCA-3](https://alleninstitute.github.io/abc_atlas_access/descriptions/Zhuang-ABCA-3.html)
- [Zhuang-ABCA-4](https://alleninstitute.github.io/abc_atlas_access/descriptions/Zhuang-ABCA-4.html)
- [Allen 数据读取教程](https://alleninstitute.github.io/abc_atlas_access/notebooks/zhuang_merfish_tutorial.html)
- [Brain Image Library 原始与处理数据](https://doi.org/10.35077/act-bag)
- [CELLxGENE 处理后集合](https://cellxgene.cziscience.com/collections/0cca8620-8dee-45d0-aef5-23f032a5cf09)
- [NeMO scRNA-seq FASTQ](https://assets.nemoarchive.org/dat-qg7n1b0)
- [分析代码 0.1](https://doi.org/10.5281/zenodo.10050573)

## SpatialVista 只用了什么

SpatialVista 收录了 `ABCA-1/2/3` 的再处理展示版，没有收录只有 3 张切片的 `ABCA-4`，也不等于保存了原始图像、scRNA-seq FASTQ 或全部推断表达。

## 标签

`organism:mouse` · `tissue:brain` · `modality:merfish` · `modality:scrna-seq` · `atlas:whole-brain` · `source:allen-brain-cell-atlas`
