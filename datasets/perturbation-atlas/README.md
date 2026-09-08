# Perturbation Cell and Tissue Atlas 综述数据索引

整理论文 "Toward a foundation model of causal cell and tissue biology with a Perturbation Cell and Tissue Atlas" 引用的核心扰动数据资源。

> **综述**: https://doi.org/10.1016/j.cell.2024.07.035 (2024年, Cell)

**定位**: 这是2024年的综述，不是一个新发布的统一数据集。本项目是"综述引用数据的分类索引、下载与查看工具"，不声称复现了一个论文模型。

## 七类核心扰动数据

### 1. 基因扰动
| 数据集 | 编号 | 状态 | 已有模块 |
|--------|------|------|----------|
| Dixit 2016 | GSE90063 | 已登记 | gears |
| Norman 2019 (CRISPRa, 单基因+组合) | GSE133344 | 已登记 | cellcap, gears, perturbnet, scperturb |
| Replogle 2022 (大规模CRISPRi) | gwps.wi.mit.edu | 已登记 | gears, xcell |

- Norman 官方代码: https://github.com/thomasmaxwellnorman/Perturbseq_GI
- Replogle 补充数据: https://plus.figshare.com/articles/dataset/21632564 （不是完整单细胞数据，完整矩阵从作者平台核对）

### 2. 药物扰动
| 数据集 | 编号 | 状态 | 已有模块 |
|--------|------|------|----------|
| sci-Plex | GSE139944 | 已登记 | perturbnet |

- 官方代码: https://github.com/cole-trapnell-lab/sci-plex
- 保留药物、剂量、细胞系、重复与对照标签

### 3. RNA与蛋白多组学扰动
| 数据集 | 编号 | 状态 |
|--------|------|------|
| Perturb-CITE-seq | SCP1064 | 新增登记 |

- 平台: https://singlecell.broadinstitute.org/single_cell/study/SCP1064
- 代码: https://github.com/klarman-cell-observatory/Perturb-CITE-seq
- 处理后矩阵与DUOS受控原始数据分别登记；受控数据只记录申请入口

### 4. 图像表型
| 数据集 | 编号 | 状态 |
|--------|------|------|
| Funk 2022 | S-BIAD394 | 新增登记 |

- 平台: https://vesuvius.wi.mit.edu/
- BioStudies: https://www.ebi.ac.uk/biostudies/bioimages/studies/S-BIAD394
- 论文: https://doi.org/10.1016/j.cell.2022.10.017
- 分别登记原始图像、处理后图像、单细胞特征和基因级表型

### 5. 类器官扰动
| 数据集 | 编号 | 状态 |
|--------|------|------|
| CHOOSE | Zenodo 7083558 + E-MTAB | 新增登记 |

- 处理后Seurat对象: https://zenodo.org/records/7083558
- scRNA与扩增子: https://www.ebi.ac.uk/biostudies/arrayexpress/studies/E-MTAB-13148
- 多组学: https://www.ebi.ac.uk/biostudies/arrayexpress/studies/E-MTAB-13144
- 基因组DNA扩增子: https://www.ebi.ac.uk/biostudies/arrayexpress/studies/E-MTAB-13140

### 6. 胚胎与体内扰动
| 数据集 | 编号 | 状态 |
|--------|------|------|
| Saunders 2023 / zscape | GSE202639 | 新增登记 |

- GEO: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE202639
- 网站: https://cole-trapnell-lab.github.io/zscape/
- 代码: https://github.com/cole-trapnell-lab/sdg-zfish
- 保留胚胎ID、时间、扰动、批次和细胞类型

### 7. 压缩扰动
| 数据集 | 编号 | 状态 |
|--------|------|------|
| Compressed Perturb-seq | FR-Perturb | 新增登记 |

- 论文: https://www.nature.com/articles/s41587-023-01964-9
- 代码: https://github.com/douglasyao/FR-Perturb
- 分别登记conventional、cell-pooling和guide-pooling
- 混合液滴不能默认当成单个细胞

## 平台与工具（单独登记）

| 资源 | 链接 | 用途 | 已有模块 |
|------|------|------|----------|
| scPerturb | https://www.sanderlab.org/scPerturb/ | 扰动数据库 | scperturb |
| CausalBench | https://github.com/causalbench/causalbench | 基因网络推断评测 | 新增 |

- scPerturb RNA: https://doi.org/10.5281/zenodo.7041848
- scPerturb ATAC: https://doi.org/10.5281/zenodo.7058381
- 注意不要混入名称相同的其他CausalBench项目

## 扩展待核实列表（pending）

以下从综述参考文献定位原论文，核对数据入口前标记 pending，不混入已验证下载清单：

- Perturb-ATAC
- Perturb-SHARE-seq
- Perturb-map
- Perturb-FISH
- E3连接酶 Perturb-seq
- 小鼠脑 in vivo Perturb-seq

## 数据处理原则

- 保存原始与标准化标签的映射
- 不默认跨研究去批次
- 不把缺失标签补成对照
- 保留供者、样本、胚胎、实验批次及组合扰动信息
- 只有检查过文件内容后，才能标记原始计数或标准化表达

## GitHub 存储规则

- 保存说明、清单、下载脚本、查看notebook及小型示例
- 大型原始数据、完整表达矩阵和图像放在本地缓存并加入.gitignore
- 已有数据优先复用（见 datasets.csv 的 existing_module 字段）

## 目录结构

```
perturbation-atlas/
├── README.md
├── .gitignore
├── manifests/
│   ├── datasets.csv
│   ├── resources.csv
│   ├── provenance.csv
│   └── pending_verification.csv
├── scripts/
│   ├── list_available_files.py
│   ├── download_selected.py
│   └── inspect_perturbation_data.py
├── notebooks/
│   └── explore_perturbation_atlas.ipynb
├── data/
│   └── examples/
└── results/
    └── figures/
```
