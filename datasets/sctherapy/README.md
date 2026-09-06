# scTherapy Data

为论文 "Single-Cell Transcriptomes Identify Patient-Tailored Therapies for Selective Co-Inhibition of Cancer Clones" 建立的数据项目。

> **论文**: https://www.nature.com/articles/s41467-024-52980-5
> **作者代码**: https://github.com/kris-nader/scTherapy
> **处理后数据 (Zenodo)**: https://doi.org/10.5281/zenodo.13340927
> **代码 (Zenodo)**: https://doi.org/10.5281/zenodo.13340796
> **Docker**: https://hub.docker.com/r/kmnader/sctherapy
> **Seurat v5 Docker**: https://hub.docker.com/r/kmnader/sctherapy_v5

## 项目结构

```
scTherapy-data/
├── README.md
├── LICENSE
├── CITATION.cff
├── data/
│   ├── README.md
│   ├── raw/           # 原始数据 (SRA/EGA，不进 Git)
│   ├── processed/     # 处理后 Seurat 对象 (不进 Git)
│   ├── external/      # 外部参考数据
│   └── source_data/   # 论文图表源数据
├── metadata/
│   ├── dataset_catalog.csv    # 数据目录
│   ├── accession_manifest.tsv # accession 清单
│   └── data_dictionary.md     # 数据字典
├── scripts/
│   ├── download_zenodo.py     # 下载 Zenodo 处理后数据
│   ├── download_sra.ps1       # 下载 SRA 原始数据 (默认仅显示)
│   ├── inspect_seurat.R       # 检查 Seurat 对象
│   └── verify_checksums.py    # 校验文件
└── notebooks/
    └── inspect_processed_data.ipynb
```

## 数据分类

### A. AML 原始单细胞数据 (SRA)

| 患者 | SRA accession |
|------|---------------|
| Patient 5 | SRR30720408 |
| Patient 6 | SRR30720407 |
| Patient 12 | SRR30720406 |

### B. AML 受控数据 (EGA)

- EGAS00001004614
- EGAS00001004444

### C. HGSC 受控数据 (EGA)

- EGAS00001005010
- EGAS00001005066

### D. 处理后 Seurat 对象 (Zenodo)

- https://doi.org/10.5281/zenodo.13340927

### E. 模型训练数据库

| 数据库 | 用途 | 链接 |
|--------|------|------|
| LINCS 2020 | 药物诱导基因表达变化 | https://clue.io/data |
| PharmacoDB | 药物剂量-细胞抑制率 | https://pharmacodb.ca/ |
| PubChem | 药物结构 | https://www.ncbi.nlm.nih.gov/pccompound |

### F. 泛癌单细胞数据

- 3CA: https://www.weizmann.ac.il/sites/3CA

### G. 代码和运行环境

- GitHub: https://github.com/kris-nader/scTherapy
- Zenodo 代码: https://doi.org/10.5281/zenodo.13340796
- Docker: https://hub.docker.com/r/kmnader/sctherapy
- Seurat v5 Docker: https://hub.docker.com/r/kmnader/sctherapy_v5

## 三类训练数据的关系

LightGBM 模型训练使用三类数据联合：

1. **LINCS** 提供药物诱导的基因表达变化（转录组响应）
2. **PharmacoDB** 提供药物剂量-细胞抑制率（药物敏感性表型）
3. **PubChem** 提供药物结构（分子指纹/描述符）

三者联合用于训练 LightGBM，预测患者特异性的药物响应和组合治疗方案。

```
LINCS (表达变化) ──┐
                    ├──→ LightGBM 训练 ──→ 患者特异性药物响应预测
PharmacoDB (剂量-抑制率) ──┤
PubChem (药物结构) ──┘
```

## 数据类型区分

| 类型 | 说明 |
|------|------|
| 模型训练数据 | LINCS、PharmacoDB、PubChem |
| 患者预测数据 | AML/HGSC 单细胞转录组 |
| 实验验证数据 | 体外药物筛选验证 |
| 处理后数据 | Zenodo Seurat 对象 |
| 受控数据 | EGA 受控人类数据（需申请） |
| 软件和在线平台 | GitHub、Docker、3CA、CLUE |

## 快速开始

```bash
# 1. 下载处理后 Seurat 对象 (优先)
python scripts/download_zenodo.py

# 2. 检查 Seurat 对象
Rscript scripts/inspect_seurat.R data/processed/<seurat_object>.rds

# 3. 查看处理后数据
jupyter notebook notebooks/inspect_processed_data.ipynb

# 4. (可选) 下载 SRA 原始数据 (默认仅显示，需确认后下载)
powershell -File scripts/download_sra.ps1
```

## 受控数据说明

EGA 数据属于受控人类数据：
- 只记录编号、链接和申请流程
- 不尝试绕过权限下载
- 不上传任何受控患者数据到 GitHub

申请流程：
1. 访问 EGA Archive (https://ega-archive.org/)
2. 注册 EGA 账号
3. 提交数据访问申请 (DAC)
4. 等待审批后使用 EGA Download Client 下载

## 大文件处理规则

- `data/raw` 和 `data/processed` 加入 `.gitignore`
- GitHub 只保存：数据目录结构、下载脚本、accession 和链接、元数据、数据字典、示例输出、小型演示数据
- 大型二进制数据不直接提交 Git 历史
- 必要时使用 DVC 或 Git LFS

## 许可证

本项目代码仅供学术研究使用。数据版权归原始作者所有。
