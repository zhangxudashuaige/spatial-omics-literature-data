# 数据内容说明

## 成年小鼠 Stereo-seq

论文使用 10 μm 厚的冠状切片构建成年小鼠空间转录组。在线系统说明两只小鼠共 195 张切片：mouse1 123 张、mouse2 72 张。`total_gene_T*.txt.gz` 是官方公布的逐切片文件模式，包含 DNB 层面的：

- `gene`：小鼠基因名
- `x`、`y`：原始 DNB 坐标
- `umi_count`：去重 reads 数量
- `cell_label`：StereoCell 分割得到的细胞编号；0 表示细胞边界外的 DNB
- `gene_area`：脑区编号
- `rx`、`ry`：旋转后坐标，用于统一切片方向

具体的每张切片文件名必须从官方文件清单获得，本仓库不根据模式自行补全。

## 细胞分割和图像

ssDNA/DAPI 图像用于识别细胞核和组织结构，StereoCell 根据图像与表达信息生成细胞边界和 `cell_label`。原始 TIFF 与完整分割产物可能非常大，应放在 `data/raw/` 或 `data/processed/`，不提交 GitHub。

## snRNA-seq

在线系统报告成年雄鼠 7 周龄全脑 snRNA-seq 共获得 378,287 个高质量细胞核，经聚类形成 19 个 subclass 和 308 个 cluster。它提供细胞类型参考，不包含组织切片内的原始空间位置。

## Spatial-ID 映射

Spatial-ID 使用图卷积网络，将 snRNA-seq 定义的 308 个 cluster 转移到 Stereo-seq 细胞。官方文件 `stereoseq.celltypeTransfer.2mice.all.tsv.gz` 至少包含：`mouse`、`section_id`、`cell_id`、`cell_cluster`、`cell_subclass`、`cell_class`、`color`。

## CCFv3 和脑区

研究将切片注册到 Allen Mouse Brain Common Coordinate Framework version 3。CCF 坐标、脑区编号、区域层级及转换参数属于处理后数据。若 BSDC 只展示入口而不列出具体文件，必须先登录或取得官方清单后再下载。

## 发育阶段数据

论文还分析 E12.5、E14.5、E16.5、P1、P7、P14 和 P77 的脑发育空间数据，用于研究 TF regulon、基因模块和 lncRNA 的时空动态。这些数据不能与成年两只小鼠的 195 张连续全脑切片混为一套矩阵。

## 分析结果

论文报告的 TF regulon、脑区特异基因、基因模块和 lncRNA 结果可能位于论文补充表或 BSDC 处理后数据中。只有在来源页面明确给出文件名时，才能加入 `manifests/files.csv` 的可下载文件条目。
