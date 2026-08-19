# 数据关系

| 对象 | 内容 | 上游 | 下游/用途 |
|---|---|---|---|
| SRA run | 双端原始 reads | Stereo-seq 文库 | SAW 处理 |
| GEO H5AD | 处理后 AnnData | SAW、作者整合 | 坐标图、marker、阶段比较 |
| `X` / layers | 表达矩阵或表达层 | H5AD | marker 表达 |
| `obs` | 细胞或空间单位元数据 | H5AD | 细胞类型、胚层、切片、阶段 |
| `var` | 基因元数据 | H5AD | marker 匹配 |
| `obsm` / obs 坐标列 | 2D/3D 坐标候选 | H5AD | 空间散点图与三维重建 |
| 外部 scRNA-seq | 参考细胞类型 | 其他研究 | 标签转移 |
| coFAST | 空间感知聚类 | 表达和坐标 | cluster 与特征基因 |
| SEU-3D | 网页三维浏览 | 处理后坐标和注释 | 交互探索 |

本项目的自动识别只产生“候选字段”，不会把名字相似的列直接认定为生物学真值。真实分析前必须查看 `results/reports/h5ad_schema.json`。
