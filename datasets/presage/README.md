# PRESAGE 数据资源

整理论文 "PRESAGE" 的数据资源，用于 GitHub 归档。暂时不要训练模型。

> **论文**: https://doi.org/10.1101/2025.06.03.657653 (2025预印本)
> **官方资源**:
> - 代码: https://github.com/Genentech/PRESAGE
> - Zenodo 缓存: https://zenodo.org/records/15587986
> - 缓存包: https://zenodo.org/records/15587986/files/cache.tar.gz?download=1
> - scPerturb: https://zenodo.org/records/7041849
> - GEO: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE264667
> - 下载脚本: https://github.com/Genentech/PRESAGE/blob/main/src/prep_dataset_utils/download_datasets.sh

**归类**: 基因扰动响应预测／多来源基因先验融合

## 资源复用（不重复下载大文件）

本仓库已有以下资源，通过链接和清单关联，不重复下载或复制大文件：
- **Replogle**: `datasets/gears/`, `datasets/xcell/`
- **scPerturb**: `datasets/scperturb/`
- **DepMap**: `datasets/xcell/`

复用关系记录在 `data_manifest/reuse_resource_map.csv`。

## 分类整理

### 1. 实验表达数据
- Zenodo 缓存包中的 h5ad 文件（5个）
- GSE264667
- scPerturb 数据（复用已有）

### 2. 来源嵌入
- 基因语义嵌入（GenePT等）
- 记录基因ID类型、维度、来源名称、覆盖范围及缺失处理

### 3. 处理后的平均响应
- 从归一化对数表达减去对照均值，再按扰动求平均
- HVG之外可能补回被扰动基因，输出不一定只有5,000列

### 4. 基因映射与缺失信息掩码
- 输入基因与输出响应基因的区别
- 缺失基因掩码

### 5. 训练验证测试划分
- 官方划分
- 跨数据集先验的使用关系
- 目标系统测试扰动的真实响应不加入训练

### 6. 代码与评估工具
- https://github.com/Genentech/PRESAGE

## 数据核验要点

- 核验五个 h5ad 文件及作者缓存包
- 记录实际文件名、来源、版本、大小、校验值、用途、许可和下载状态
- **不猜测包内有模型权重**
- 检查每份 h5ad 的 shape、X、layers、obs、var
- 确认表达是否为原始计数，哪个字段记录扰动基因、非靶向对照及实验背景
- 输出少量真实预览，避免把大矩阵整体转成稠密矩阵
- 检查嵌入文件的基因ID类型、维度、来源名称、覆盖范围及缺失处理
- 记录输入基因与输出响应基因的区别

## 预处理核验

- 从归一化对数表达减去对照均值，再按扰动求平均
- HVG之外可能补回被扰动基因，因此输出不一定只有5,000列
- 保留官方划分，并记录跨数据集先验的使用关系
- 不要把目标系统测试扰动的真实响应加入训练
- 同一基因在其他允许使用的数据集中出现，应明确记为外部先验

## GitHub 保存范围

- 中文说明、资源清单、下载和检查脚本
- 许可允许的小样例
- 大文件保存在本地数据目录，加入 .gitignore，不直接提交普通 Git
- 不自动启用付费存储

## 许可证

- 分别遵守源码、嵌入和上游数据许可
- 需要登录、链接限流或下载失败时，标记待处理，不写成已完成

## 目录结构

```
presage/
├── README.md
├── environment.yml
├── requirements.txt
├── .gitignore
├── data_manifest/
│   ├── datasets.csv
│   ├── reuse_resource_map.csv
│   └── data_dictionary.md
├── scripts/
│   ├── download_presage_cache.py
│   ├── inspect_h5ad.py
│   ├── check_gene_embedding.py
│   └── verify_preprocessing.py
├── notebooks/
│   └── 01_minimal_sample_view.ipynb
├── data/
│   ├── raw/          (不提交Git)
│   ├── processed/    (不提交Git)
│   └── examples/
└── results/
    └── gene_mask_summary.csv
```
