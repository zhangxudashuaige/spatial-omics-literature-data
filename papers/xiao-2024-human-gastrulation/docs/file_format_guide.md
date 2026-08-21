# 文件格式指南

| 格式 | 预期内容 | 本项目怎样检查 |
|---|---|---|
| `*.fq.gz` / `*.fastq.gz` | 成对测序 reads；Stereo-seq R1/f1 常含 CID/UMI，R2 为 cDNA | 只统计前 N 条 read 的长度和结构，不输出序列 |
| `*_sta.xml` | GSA-Human 每个 run 的 read 数、碱基数、长度、GC 和质量统计 | XML 节点概览 |
| GEM/CSV/TSV | 基因、x、y、计数或注释的文本表 | 分隔符、表头、行数、坐标/基因/计数字段候选 |
| GEF/HDF5 | SAW 或其他流程产生的层次化表达数据 | HDF5 组、数据集、shape、dtype，不加载完整矩阵 |
| H5AD | AnnData：`X` 表达矩阵、`obs` 空间点元数据、`var` 基因、`obsm` 坐标 | `backed="r"`，列出 shape、稀疏性和各键 |
| 坐标表 | 至少含 x、y；三维文件还应有 z；通常还需 slice_id/bin_id | 自动寻找候选列并绘制 2D/3D 点图 |
| 注释表 | 唯一 ID、cluster、组织/细胞类型 | 统计类别，并检查能否与表达/坐标通过唯一 ID 连接 |

示例：

```powershell
python scripts/inspect_spatial_files.py data/processed/example.h5ad --json results/tables/example_schema.json
python scripts/inspect_spatial_files.py data/processed/example.gem.gz --json results/tables/example_gem.json
```

检查脚本只报告结构，不会把人类原始 read 或完整表达内容写进仓库。
