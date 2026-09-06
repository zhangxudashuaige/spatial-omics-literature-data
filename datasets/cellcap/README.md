# CellCap Data

整理和复现 CellCap 论文的数据项目。

> **论文**: CellCap: Capturing Cell-Specific Perturbation Responses
> **官方代码**: https://github.com/broadinstitute/CellCap
> **官方代码以 submodule 方式关联**: `git submodule add https://github.com/broadinstitute/CellCap external/CellCap`

## 项目结构

```
cellcap-data/
├── README.md
├── environment/           # 环境配置
│   ├── environment.yml
│   └── requirements.txt
├── metadata/              # 数据清单与校验
│   ├── datasets.csv
│   └── checksums.csv
├── scripts/               # 下载、预处理、检查脚本
│   ├── download_simulation_data.py
│   ├── download_norman_geo.py
│   ├── prepare_norman_anndata.py
│   ├── prepare_cellcap_inputs.py
│   └── inspect_h5ad.py
├── notebooks/             # 分析 notebook
│   ├── 01_simulation.ipynb
│   ├── 02_human_monocytes.ipynb
│   └── 03_norman_crispra.ipynb
├── configs/               # 训练/数据配置
│   ├── simulation.yaml
│   ├── monocytes.yaml
│   └── norman.yaml
├── data/                  # 数据（大文件不进 Git）
│   ├── raw/
│   ├── processed/
│   └── README.md
├── models/                # 模型权重（不进 Git）
│   └── README.md
└── results/               # 结果
    ├── figures/
    └── tables/
```

## 数据说明

### 1. CellCap 模拟数据 (simulation_data.h5ad)

- **是什么**: CellCap 官方教程使用的合成模拟数据，包含已知的扰动响应程序。
- **用途**: 快速测试 CellCap 模型能否正确分解响应程序，验证训练流程。
- **适合**: 快速测试（小规模，可直接运行教程）。
- **预期路径**: `data/raw/simulation_data.h5ad`
- **状态**: 需从官方仓库或配套资源获取。若官方仓库未直接提供，按官方教程中的下载指令获取。

### 2. 人单核细胞数据 (CellCap_1MPBMC_Mono.h5ad)

- **是什么**: 1M PBMC 中单核细胞亚群的处理后 AnnData，用于 CellCap 真实数据演示。
- **用途**: 在真实单细胞数据上训练 CellCap，提取扰动响应程序。
- **适合**: 完整复现（真实数据，需较多计算资源）。
- **预期路径**: `data/raw/CellCap_1MPBMC_Mono.h5ad`
- **状态**: 需从官方配套资源获取。可能需要 Git LFS 或单独下载链接。

### 3. CellCap 单核细胞模型 (CellCap_1MPBMC_Mono/model.pt)

- **是什么**: 在单核细胞数据上预训练的 CellCap 模型权重。
- **用途**: 直接加载已训练模型，导出响应程序，无需重新训练。
- **适合**: 快速查看结果。
- **预期路径**: `models/CellCap_1MPBMC_Mono/model.pt`
- **状态**: 需从官方配套资源获取。模型权重不进普通 Git。

### 4. Norman 2019 CRISPRa 数据 (GEO GSE133344)

- **是什么**: Norman et al. 2019 在 K562 细胞中进行的 CRISPRa 扰动筛选，包含单基因和双基因组合扰动。
- **用途**: 评估 CellCap 在组合扰动预测上的性能。
- **适合**: 完整复现（需从 GEO 下载并预处理）。
- **accession**: GSE133344
- **公开访问**: 是
- **处理后路径**: `data/processed/norman_crispra.h5ad`

### 5. EGA 受控数据

- **EGAS00001005376**: 受控访问，需申请。
- **EGAD00001007764**: 受控访问数据集，需申请。
- **状态**: 仅记录元数据和申请流程，不尝试绕过访问控制。

## 数据之间的关系

```
模拟数据 (simulation_data.h5ad)
    ↓ 用于验证模型分解能力
CellCap 模型训练
    ↓
单核细胞数据 (CellCap_1MPBMC_Mono.h5ad)
    ↓ 训练得到
预训练模型 (model.pt)
    ↓ 导出
Z^basal, H, β, h, 响应程序基因

Norman CRISPRa (GSE133344)
    ↓ 独立评估
组合扰动预测性能
```

## 哪个数据适合什么

| 场景 | 推荐数据 | 原因 |
|------|----------|------|
| 快速测试 | simulation_data.h5ad | 小规模，已知真值，教程级 |
| 完整复现 | CellCap_1MPBMC_Mono.h5ad | 真实数据，论文主要结果 |
| 组合扰动评估 | Norman GSE133344 | 标准基准，含单/双扰动 |
| 受控数据 | EGA EGAS/EGAD | 需申请，仅记录 |

## 如何构造 CellCap 需要的输入

CellCap 需要三个核心矩阵：

1. **X (表达矩阵)**: 细胞 × 基因的原始或归一化表达矩阵。
   - 从 AnnData 的 `.X` 或 `.layers["counts"]` 获取。

2. **X_target (扰动矩阵)**: 细胞 × 扰动基因的 multi-hot 矩阵。
   - 保存在 `.obsm["X_target"]`。
   - 每行表示该细胞接受了哪些基因的扰动（1=扰动，0=未扰动）。
   - 单扰动：只有一个 1；组合扰动：有多个 1。

3. **X_covar (协变量矩阵)**: 细胞 × 协变量的矩阵。
   - 保存在 `.obsm["X_covar"]`。
   - 可包含：细胞周期评分、批次、总计数、检测基因数等。

构造脚本: `scripts/prepare_cellcap_inputs.py`

## 如何运行官方模拟数据教程

```bash
# 1. 克隆官方代码
git submodule update --init --recursive

# 2. 安装环境
conda env create -f environment/environment.yml
conda activate cellcap

# 3. 下载模拟数据
python scripts/download_simulation_data.py

# 4. 检查数据
python scripts/inspect_h5ad.py data/raw/simulation_data.h5ad

# 5. 运行 notebook
jupyter notebook notebooks/01_simulation.ipynb
```

## 如何训练并导出模型参数

训练后 CellCap 导出以下组件：

- **Z^basal**: 基础表达潜变量（细胞 × 隐维度），表示未扰动状态下的细胞状态。
- **H**: 响应程序矩阵（程序 × 基因），每个程序是一组基因的权重。
- **β**: 扰动系数（扰动 × 程序），表示每个扰动激活哪些响应程序。
- **h**: 程序活性（细胞 × 程序），每个细胞中各程序的活性。
- **响应程序基因**: 从 H 中提取每个程序的 top 基因。

```python
import torch
from cellcap import CellCap

# 加载数据
# ... 准备 X, X_target, X_covar ...

# 初始化并训练
model = CellCap(...)
model.fit(X, X_target, X_covar, epochs=...)

# 导出
Z_basal = model.get_z_basal()
H = model.get_response_programs()
beta = model.get_perturbation_coefficients()
h = model.get_program_activities()

# 提取每个程序的 top 基因
top_genes = model.get_top_genes(program_idx, n=50)
```

## 大文件处理规则

- 普通 Git 只保存代码、配置、少量元数据和下载清单。
- `.h5ad`、`.h5`、`.mtx`、`.fastq.gz`、`.pt` 不直接进入普通 Git。
- 使用 `.gitignore` 排除大型数据。
- 如确实需要版本管理，使用 Git LFS 或 DVC。
- README 中写清数据如何从原始来源重新生成。

## 缺失文件记录

以下文件在官方仓库中可能需要单独获取或使用 Git LFS：

| 文件 | 预期路径 | 状态 | 说明 |
|------|----------|------|------|
| simulation_data.h5ad | data/raw/ | 待获取 | 官方教程引用，需确认下载方式 |
| CellCap_1MPBMC_Mono.h5ad | data/raw/ | 待获取 | 可能需要 Git LFS 或单独链接 |
| model.pt | models/CellCap_1MPBMC_Mono/ | 待获取 | 模型权重，不进普通 Git |

> 以上文件不伪造下载链接。以官方仓库和教程当前页面为准。

## 许可证

本项目代码仅供学术研究使用。数据版权归原始作者所有。
