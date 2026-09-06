# scPerturb Data

整理 scPerturb 数据库的数据清单、下载脚本、数据检查程序和示例。

> **论文**: scPerturb: An Information-Theoretic Framework to Define and Evaluate Single-Cell Perturbation Data (Nature Methods, 2023)
> **正式论文**: https://www.nature.com/articles/s41592-023-02144-y
> **网站**: https://www.sanderlab.org/scPerturb/
> **代码**: https://github.com/sanderlab/scPerturb
> **RNA和蛋白质数据**: https://zenodo.org/records/13350497
> **ATAC数据**: https://zenodo.org/records/7058382

**重要：不把 43 GB 原始数据直接提交到普通 Git 历史。**

## 项目结构

```
scperturb-data/
├── README.md
├── metadata/
│   ├── datasets.csv       # 数据集清单
│   ├── files.csv          # Zenodo 文件清单
│   └── checksums.csv      # MD5 校验值
├── scripts/
│   ├── fetch_zenodo_manifest.py  # 从 Zenodo API 获取文件清单
│   ├── download_dataset.py        # 下载指定数据集
│   ├── verify_md5.py              # MD5 校验
│   ├── inspect_h5ad.py            # 检查 h5ad 结构
│   └── create_minimal_sample.py   # 创建最小示例
├── notebooks/
│   ├── 01_inspect_adamson.ipynb
│   ├── 02_inspect_norman.ipynb
│   └── 03_edistance_example.ipynb
├── data/
│   ├── raw/
│   ├── processed/
│   └── README.md
├── examples/
│   └── minimal_perturbation.h5ad  # 6细胞×4基因最小示例
└── results/
    ├── summaries/
    └── figures/
```

## 数据分类

| 分类 | 说明 | 示例 |
|------|------|------|
| genetic_rna | 遗传扰动 (CRISPRi/a) 的 RNA 表达 | Adamson 2016, Norman 2019 |
| drug_rna | 药物扰动的 RNA 表达 | 药物筛选数据集 |
| multimodal_rna_protein | RNA + 蛋白质多模态 | CITE-seq 数据集 |
| atac | 染色质可及性 | scATAC-seq 数据集 |
| developmental_or_cytokine | 发育或细胞因子扰动 | 分化、刺激数据集 |

## 数据类型区分

| 类型 | 说明 | 位置 |
|------|------|------|
| 原始论文数据 | 各论文原始发布的数据 | GEO/SRA/EGA |
| scPerturb 统一处理数据 | scPerturb 统一 QC 和标准化后的 h5ad | Zenodo |
| RNA 表达 | 基因表达矩阵 | h5ad .X |
| 蛋白质数据 | 抗体标签 (ADT) 计数 | h5ad .mod or .obsm |
| ATAC 数据 | 染色质可及性 | 单独 Zenodo 记录 |
| 细胞元数据 | 扰动标签、细胞类型、批次等 | h5ad .obs |
| E-distance 分析结果 | 扰动间 E-distance 和统计检验 | results/summaries/ |
| 模型训练数据与输出 | 用于训练或模型预测的数据 | 单独标注 |

## 快速开始

```bash
# 1. 安装依赖
pip install anndata scanpy numpy pandas scipy tqdm requests
# E-distance 分析推荐使用 pertpy
pip install pertpy
# 或使用 scperturb 包
pip install scperturb

# 2. 获取 Zenodo 文件清单
python scripts/fetch_zenodo_manifest.py --record 13350497

# 3. 下载第一个数据集 (Adamson, ~34.6 MB)
python scripts/download_dataset.py --file AdamsonWeissman2016_GSM2406675_10X001.h5ad

# 4. 校验 MD5
python scripts/verify_md5.py data/raw/AdamsonWeissman2016_GSM2406675_10X001.h5ad

# 5. 检查数据结构
python scripts/inspect_h5ad.py data/raw/AdamsonWeissman2016_GSM2406675_10X001.h5ad

# 6. 运行 E-distance 示例
jupyter notebook notebooks/03_edistance_example.ipynb
```

## 推荐下载顺序

1. **首先下载**: `AdamsonWeissman2016_GSM2406675_10X001.h5ad` (~34.6 MB)
2. **根据磁盘空间选择**: `NormanWeissman2019_filtered.h5ad` (~698.7 MB)
3. **不默认下载全部 43 GB**

## E-distance 分析

E-distance (Energy distance) 是 scPerturb 提出的扰动效应度量方法：

- **E-distance**: 衡量两个细胞分布之间的统计距离，基于欧氏距离的 U 统计量
- **E-test**: 基于 E-distance 的置换检验，判断两个分布是否显著不同
- **p 值校正**: 多重检验校正 (Bonferroni / BH)

推荐使用 `pertpy` 包进行 E-distance 计算：
```python
import pertpy as pt
ed = pt.tl.EnergyDistance()
results = ed.compute(adata, groupby='perturbation', contrast='control')
```

如同时使用 `scperturb` 包，记录二者版本及结果差异。

## 最小示例

`examples/minimal_perturbation.h5ad` 包含：
- 6 个细胞 × 4 个基因
- 2 个 control 细胞
- 2 个 GeneA 扰动细胞
- 1 个 GeneB 扰动细胞
- 1 个 GeneA+GeneB 组合扰动细胞

用于测试 E-distance 计算流程，不可用于复现论文指标。

## 大文件处理规则

- `.h5ad`、`.h5`、`.zip`、`.mtx` 加入 `.gitignore`
- GitHub 只保存最小示例、代码、清单和文档
- 大文件使用 DVC 或 Git LFS
- 不重新分发许可证不明确的数据
- README 说明每个文件如何从 Zenodo 重新下载
- 下载后使用官方 MD5 校验

## 许可证

本项目代码仅供学术研究使用。scPerturb 数据版权归原始作者所有。
