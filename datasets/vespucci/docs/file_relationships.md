# Visium 数据文件关系说明

本文档解释 10x Visium 空间转录组标准输出中各文件之间的关系和依赖。

## 标准输出文件结构

```
sample_id/
├── filtered_feature_bc_matrix/
│   ├── matrix.mtx              # 基因×spot 稀疏计数矩阵
│   ├── features.tsv            # 矩阵行（基因）注释
│   └── barcodes.tsv            # 矩阵列（spot）注释
├── spatial/
│   ├── tissue_positions.csv    # spot 坐标（阵列坐标）
│   ├── scalefactors_json.json  # 阵列坐标 ↔ 图像坐标 缩放因子
│   ├── tissue_hires_image.png  # 高分辨率组织图像
│   ├── tissue_lowres_image.png # 低分辨率组织图像
│   └── tissue_positions_list.csv (旧版)
└── raw_feature_bc_matrix/      # 未过滤矩阵（包含所有spot）
    ├── matrix.mtx
    ├── features.tsv
    └── barcodes.tsv
```

## 各文件详细说明

### 1. matrix.mtx — 基因×spot 稀疏计数矩阵

- **格式**: Matrix Market 稀疏矩阵格式
- **维度**: 基因数 × spot数
- **内容**: 每个 spot 中每个基因的 UMI 计数（整数）
- **读取**: `scipy.io.mmread("matrix.mtx")` 或 `scanpy.read_mtx()`
- **关系**: 行对应 `features.tsv` 中的基因，列对应 `barcodes.tsv` 中的 spot

### 2. features.tsv — 矩阵行（基因）注释

- **格式**: TSV（制表符分隔），通常3列
- **列**: `gene_id` \t `gene_name` \t `feature_type`
- **示例**: `ENSG00000243485` \t `MIR1302-2HG` \t `Gene Expression`
- **关系**: 第 i 行对应 `matrix.mtx` 的第 i 行
- **注意**: 10x Visium 可能包含额外 feature type（如 Custom）

### 3. barcodes.tsv — 矩阵列（spot）注释

- **格式**: 单列，每个 spot 的 barcode
- **示例**: `AAACAAGTAGACCAAC-1`
- **关系**: 第 j 行对应 `matrix.mtx` 的第 j 列
- **注意**: barcode 末尾的 `-1` 是文库编号（GEM well）

### 4. tissue_positions.csv — spot 坐标（阵列坐标）

- **格式**: CSV
- **列**:
  - `barcode`: spot barcode（对应 barcodes.tsv）
  - `in_tissue`: 是否在组织内（0/1）
  - `array_row`: 阵列行号
  - `array_col`: 阵列列号
  - `pxl_row_in_fullres`: 全分辨率图像中的行像素
  - `pxl_col_in_fullres`: 全分辨率图像中的列像素
- **关系**: 通过 `barcode` 列与 `barcodes.tsv` 关联
- **用途**: 将表达数据映射到空间位置

### 5. scalefactors_json.json — 阵列坐标 ↔ 图像坐标 缩放因子

- **格式**: JSON
- **字段**:
  - `tissue_hires_scalef`: 高分辨率图像缩放因子
  - `tissue_lowres_scalef`: 低分辨率图像缩放因子
  - `fiducial_diameter_fullres`: 基准点直径（全分辨率像素）
  - `spot_diameter_fullres`: spot 直径（全分辨率像素）
- **关系**: 连接 `tissue_positions.csv` 中的阵列坐标和图像像素坐标
- **用途**: 在图像上正确绘制 spot 位置和大小

### 6. tissue_hires_image.png — 高分辨率组织图像

- **格式**: PNG 图像
- **内容**: 组织切片的高分辨率图像（通常 2000px 宽）
- **关系**: 与 `tissue_positions.csv` 的 `pxl_row_in_fullres`/`pxl_col_in_fullres` 配合使用
- **用途**: 空间表达可视化的底图

### 7. FASTQ — 最原始测序 reads

- **格式**: FASTQ（通常 gzip 压缩，`.fastq.gz`）
- **内容**: 测序仪输出的原始 reads
- **关系**: 是所有处理后数据的源头
- **处理**: 通过 `spaceranger count` 处理后生成上述矩阵和图像文件
- **存储**: 通常非常大（每个样本几十 GB），不提交 Git

### 8. Seurat RDS — 作者处理后的 R 对象

- **格式**: R 序列化对象（`.rds`）
- **内容**: Seurat 对象，包含表达矩阵、元数据、降维、空间坐标等
- **关系**: 作者从原始矩阵进一步处理（归一化、聚类、注释）后的结果
- **读取**: `readRDS("object.rds")` in R
- **用途**: 直接复现论文分析结果

### 9. h5ad — Python/Scanpy 常用对象

- **格式**: HDF5 格式（`.h5ad`）
- **内容**: AnnData 对象，包含 `.X`（表达矩阵）、`.obs`（细胞/spot元数据）、`.var`（基因元数据）、`.obsm`（多维注释如空间坐标）
- **关系**: Python 生态中的标准格式，可从 Seurat 对象转换
- **读取**: `anndata.read_h5ad("object.h5ad")`
- **用途**: Python 环境下的空间转录组分析

## 文件依赖关系图

```
FASTQ (原始测序)
    │
    ▼ spaceranger count
matrix.mtx + features.tsv + barcodes.tsv  (表达矩阵三件套)
    │
    ├──→ tissue_positions.csv (spot坐标) ──→ scalefactors_json.json ──→ tissue_hires_image.png
    │
    ▼ 进一步处理 (R/Python)
Seurat RDS / h5ad (作者处理后对象)
    │
    ▼ 分析
结果图表
```

## 读取示例

### Python (Scanpy)
```python
import scanpy as sc

# 读取 Visium 数据
adata = sc.read_visium("sample_id/")
# 自动读取 matrix.mtx, features.tsv, barcodes.tsv, tissue_positions.csv, scalefactors, image

print(adata.shape)  # (spot数, 基因数)
print(adata.obsm["spatial"])  # spot 坐标
print(adata.uns["spatial"]["images"]["hires"])  # 组织图像
```

### R (Seurat)
```r
library(Seurat)

# 读取 Visium 数据
obj <- Load10X_Spatial(
  data.dir = "sample_id/filtered_feature_bc_matrix",
  filename = "matrix.mtx",
  slice = "slice1"
)

# 或读取处理后的 RDS
obj <- readRDS("processed_object.rds")
```
