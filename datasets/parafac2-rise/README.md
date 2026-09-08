# PARAFAC2-RISE 数据资源

整理论文 "PARAFAC2-RISE" 的数据资源，用于 GitHub 归档和后续复现。当前任务以数据整理为主，不要求复现全部论文结果。

> **论文**: https://doi.org/10.1016/j.cels.2025.101294

## 两套实验数据（分目录存放，不混合）

### A. Chen / PopAlign PBMC 药物扰动数据
- **来源**: https://doi.org/10.6084/m9.figshare.11837097
- **内容**: 药物处理及对照条件，研究不同药物与细胞表达模式的关联
- **RISE 预处理后参考规模**: 29,433 个细胞、9,461 个基因、46 个条件
- **注意**: 该规模仅用于核对，不代表原始下载文件维度
- **本地路径**: `data/chen_popalign_pbmc/`

### B. Perez SLE PBMC 疾病队列
- **来源**: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE174188
- **内容**: SLE 患者与健康人的细胞表达模式比较
- **论文涉及**: 261 名供体、354 个样本
- **RISE 预处理后参考规模**: 1,263,673 个细胞、2,161 个基因
- **注意**: 保留供体 ID、样本 ID 及批次信息，不能将重复样本当作独立供体
- **本地路径**: `data/perez_sle_pbmc/`

## 代码资源（单独归档，不是数据集）

| 项目 | 链接 | 说明 |
|------|------|------|
| RISE | https://github.com/meyer-lab/RISE | 当前包名为 `scrise`，不要直接套用旧版安装或导入方式 |
| PARAFAC2 | https://github.com/meyer-lab/parafac2 | PARAFAC2 张量分解实现 |

记录实际使用的提交或版本。代码仓库不是数据集，分开归档在 `code_refs/`。

## 数据核验原则

- 先核验资源，再下载：核对官方文件列表、格式、大小、访问权限、许可证及样本说明
- 分别记录原始测序文件、计数矩阵、处理后矩阵和元数据，不混称"原始数据"
- 优先获取可直接分析的表达矩阵和配套元数据；暂不下载 FASTQ 等大型原始测序文件
- 文件大小未知或需要申请访问时，明确报告，不推测下载链接

## 数据检查

- 表达矩阵的行列方向
- 细胞 ID 与元数据是否对应
- 基因 ID 是否完整、有无重复
- 表达值是原始计数还是归一化值
- 样本、供体、处理和批次字段是否完整
- 可以转换为稀疏 AnnData .h5ad，但保留原始文件，并记录转换过程
- 不将归一化表达误存成原始计数

## GitHub 存储规则

- 保存 README、数据清单、下载脚本、读取与检查脚本、依赖配置、许可证与引用信息，以及小规模查看示例
- 完整大矩阵放在本地数据目录并加入 .gitignore，不默认上传 GitHub
- 若需上传完整数据，先报告大小和授权条件，再确认存储方案
- 示例数据也需确认允许再分发

## 目录结构

```
parafac2-rise/
├── README.md
├── .gitignore
├── manifests/
│   ├── chen_popalign_pbmc.csv
│   ├── perez_sle_pbmc.csv
│   ├── code_resources.csv
│   └── data_dictionary.md
├── data/
│   ├── chen_popalign_pbmc/
│   │   ├── raw/          (不提交Git)
│   │   ├── processed/    (不提交Git)
│   │   └── metadata/
│   └── perez_sle_pbmc/
│       ├── raw/          (不提交Git)
│       ├── processed/    (不提交Git)
│       └── metadata/
├── scripts/
│   ├── download_chen_popalign.py
│   ├── download_perez_sle.py
│   ├── inspect_expression.py
│   ├── check_metadata.py
│   └── convert_to_anndata.py
├── notebooks/
│   ├── 01_inspect_chen_pbmc.ipynb
│   └── 02_inspect_perez_sle.ipynb
├── results/
└── code_refs/
    └── versions.md
```
