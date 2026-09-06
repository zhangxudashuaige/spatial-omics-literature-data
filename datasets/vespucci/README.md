# Vespucci 空间转录组扰动数据

整理论文 "Identification of Perturbation-Responsive Regions and Genes in Comparative Spatial Transcriptomics Atlases" 的数据。

> **论文**: https://doi.org/10.1101/2024.06.13.598641
> **方法代码**: https://github.com/neurorestore/Vespucci
> **论文复现代码**: https://github.com/neurorestore/vespucci-analysis

**所有数据来源必须从作者代码仓库、GEO、SRA、Zenodo、Broad Single Cell Portal或原始论文核实，不得根据名称猜测。**

## 目录结构

```
vespucci/
├── README.md
├── .gitignore
├── catalog/
│   └── datasets.csv
├── docs/
│   └── file_relationships.md
├── scripts/
│   ├── download_geo_metadata.py
│   ├── download_geo_processed.py
│   ├── download_vespucci_demo.R
│   └── verify_sha256.py
├── notebooks/
│   └── inspect_visium.ipynb
├── data/
│   ├── simulated/    # Vespucci 模拟数据（小型示例）
│   ├── external/     # 外部参考数据
│   └── processed/    # 处理后数据
└── checksums/        # SHA256 校验值
```

## 收录数据集

### 1. 作者新产生的数据 — GSE268779
- 小鼠脊髓损伤、衰老与再生治疗
- 技术：10x Visium
- 保存 GEO、SRA 和 BioProject 链接
- 记录每个 GSM 样本的名称、实验条件、文件列表和文件大小
- **不根据样本编号猜测 young、old 和 treated 标签，必须从官方元数据或论文补充表核对**

### 2. Vespucci 模拟数据
- `spatial_sim`
- `spatial_sim_distance_metrics_df`
- 来源：https://github.com/neurorestore/Vespucci
- **优先把这一小型数据作为项目的可运行示例**

### 3. 脑损伤数据 — GSE226208
- Intact 和 3 dpi 小鼠大脑皮层 Visium 数据

### 4. 心肌梗死数据 — GSE214611
- 小鼠心脏 Visium 和配套单细胞/单核数据

### 5. ALS 数据 — GSE120374
- 在线平台：https://als-st.nygenome.org/

### 6. 脊髓损伤康复数据
- GSE184369：空间转录组
- GSE184370：snRNA-seq
- 论文：https://doi.org/10.1038/s41586-022-05385-7

### 7. 阿尔茨海默病 STARmap PLUS 数据
- SCP1375：https://singlecell.broadinstitute.org/single_cell/study/SCP1375
- Zenodo：https://doi.org/10.5281/zenodo.7332091

## 快速开始

```bash
# 1. 下载 Vespucci 模拟数据（小型示例）
Rscript scripts/download_vespucci_demo.R

# 2. 下载 GEO 元数据（不下载 FASTQ）
python scripts/download_geo_metadata.py --gse GSE268779

# 3. 下载 GEO 处理后文件
python scripts/download_geo_processed.py --gse GSE268779

# 4. 校验文件
python scripts/verify_sha256.py

# 5. 查看 Visium 数据
jupyter notebook notebooks/inspect_visium.ipynb
```

## 下载脚本行为约定

- 默认只下载元数据和小型处理后文件
- 不默认下载 SRA FASTQ
- 支持按 GSE 或 GSM 编号选择样本
- 下载前显示预计文件大小
- 已存在文件不得重复下载
- 下载后计算 SHA256
- 记录下载来源和日期
- 下载地址无法核实时停止，不得编造
- 需要登录的数据只写访问说明，不绕过权限

## GitHub 存储规则

- 不将大型 FASTQ、GSE120374、GSE214611 或完整 GSE268779 直接提交普通 Git 历史
- GitHub 保存元数据、下载脚本、校验和和小型示例
- 大于 50 MB 的数据谨慎使用 Git LFS
- 原始大文件保留在 GEO、SRA、Zenodo 和 Single Cell Portal
- `.gitignore` 排除 FASTQ、完整 MTX、H5、RDS 和大型图像
- README 说明如何重新下载数据

## 数据文件关系

详见 [docs/file_relationships.md](docs/file_relationships.md)，解释 Visium 标准输出各文件之间的关系。
