# 数据目录

存放 scTherapy 项目的所有数据文件。

**重要：大型二进制数据不直接提交 Git 历史。data/raw 和 data/processed 已加入 .gitignore。**

## 目录结构

- `raw/` — 原始数据
  - SRA 原始测序数据 (fastq.gz) — 需用户确认后下载
  - EGA 受控数据 — 需申请访问权限
- `processed/` — 处理后的数据
  - Zenodo 处理后 Seurat 对象 (.rds) — 优先下载
- `external/` — 外部参考数据
  - LINCS、PharmacoDB、PubChem 模型训练数据
  - 3CA 泛癌参考数据
- `source_data/` — 论文图表源数据

## 如何获取数据

### 1. 处理后 Seurat 对象 (推荐优先)
```bash
# 列出 Zenodo 文件
python scripts/download_zenodo.py --list

# 下载指定文件
python scripts/download_zenodo.py --file <filename.rds>
```

### 2. SRA 原始数据 (需确认)
```powershell
# 仅预览
powershell -File scripts/download_sra.ps1

# 确认下载
powershell -File scripts/download_sra.ps1 -Confirm
```

### 3. EGA 受控数据
- 仅记录 accession 和申请流程
- 不尝试绕过权限下载
- 不上传任何受控患者数据到 GitHub

## 数据来源

| 类型 | 来源 | 链接 |
|------|------|------|
| 处理后 Seurat 对象 | Zenodo | https://doi.org/10.5281/zenodo.13340927 |
| AML 原始数据 | SRA | SRR30720408, SRR30720407, SRR30720406 |
| AML 受控数据 | EGA | EGAS00001004614, EGAS00001004444 |
| HGSC 受控数据 | EGA | EGAS00001005010, EGAS00001005066 |
| 模型训练数据 | LINCS/PharmacoDB/PubChem | 见 dataset_catalog.csv |

## 大文件规则

- `.rds`、`.RData`、`.h5ad`、`.fastq.gz`、`.bam` 不进入普通 Git
- 已通过 `.gitignore` 排除
- 如需版本管理，使用 DVC 或 Git LFS
