# 数据关系

## 主键关系

| 实体 | 推荐主键 | 作用 |
|---|---|---|
| 小鼠 | `mouse_id` | 区分 mouse1、mouse2 和发育样本 |
| 切片 | `mouse_id + section_id` | 防止两只动物出现同名切片 |
| 细胞 | `mouse_id + section_id + cell_id` | 合并表达、坐标和细胞注释 |
| 基因 | `gene_id` 或 `gene_symbol` | 合并表达和基因注释 |
| 脑区 | `region_id` | 连接 CCFv3 名称、缩写和层级 |

仅使用 `cell_id` 可能发生跨切片重复。真实数据分析应先检查唯一性，再构造复合键。

## 处理流程

1. FASTQ 经过比对、去重和空间条形码解析，得到 DNB 表达。
2. ssDNA/DAPI 图像经过 StereoCell 分割，产生细胞边界和 `cell_label`。
3. 将细胞边界内 DNB 的 UMI 聚合为细胞 × 基因矩阵。
4. snRNA-seq 单独聚类，定义 19 个 subclass 和 308 个 cluster。
5. Spatial-ID 把 cluster 标签映射到 Stereo-seq 细胞。
6. 切片旋转、配准并映射到 Allen CCFv3，获得统一三维坐标和脑区。
7. 在统一空间中进行基因、细胞类型、TF regulon、基因模块和 lncRNA 分析。

## 目录映射

| 上游数据 | 本地目录 |
|---|---|
| CNGB FASTQ、原始图像和官方元数据 | `data/raw/` |
| BSDC 表达矩阵、分割和 Spatial-ID 结果 | `data/processed/` |
| Allen CCFv3 或其他外部参考 | `data/external/` |
| 可提交 GitHub 的合成测试数据 | `data/sample/` |
