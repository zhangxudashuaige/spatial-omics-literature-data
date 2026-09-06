# GEARS Perturbation Data

整理 GEARS 论文的数据、下载脚本和复现流程。

> **论文**: GEARS: Predicting transcriptional outcomes of novel multi-gene perturbations
> **官方代码**: https://github.com/snap-stanford/GEARS
> **官方包**: `pip install cell-gears`

## 项目结构

```
gears-perturbation-data/
├── README.md
├── environment/
│   ├── environment.yml
│   └── requirements.txt
├── metadata/
│   ├── datasets.csv       # 数据清单
│   ├── accessions.csv     # GEO/SRA accession
│   └── checksums.csv      # 校验值
├── scripts/
│   ├── download_gears_processed.py   # 下载官方预处理数据
│   ├── download_geo.py               # 从 GEO 下载原始数据
│   ├── inspect_anndata.py            # 检查 AnnData 结构
│   ├── build_coexpression_graph.py   # 构建共表达图
│   ├── build_go_graph.py             # 构建 GO 相似度图
│   └── verify_data.py                # 数据验证
├── notebooks/
│   ├── 01_inspect_norman.ipynb
│   ├── 02_train_gears_norman.ipynb
│   ├── 03_predict_unseen_combinations.ipynb
│   └── 04_inspect_graphs.ipynb
├── data/
│   ├── raw/
│   ├── processed/
│   ├── external/gene_ontology/
│   └── README.md
├── graphs/
│   ├── coexpression/
│   └── go_similarity/
├── models/
└── results/
    ├── predictions/
    ├── figures/
    └── metrics/
```

## 数据清单

### 实验表达数据

| 数据 | accession | 细胞类型 | 扰动技术 | 单/组合 | 用途 |
|------|-----------|----------|----------|---------|------|
| Replogle 2022 RPE-1 | GSE196826 | RPE-1 | CRISPRi | 单 | 训练/评估 |
| Replogle 2022 K562 | GSE196826 | K562 | CRISPRi | 单 | 训练/评估 |
| Norman 2019 | GSE133344 | K562 | CRISPRa | 单+组合 | 组合扰动预测 |
| Adamson 2016 | GSE90546 | K562 | CRISPRi | 组合 | 训练/评估 |
| Dixit 2016 | GSE90063 | K562 | CRISPRi | 单 | 训练/评估 |
| Jost 2020 | GSE132080 | mESC | CRISPRi | 单 | 训练/评估 |
| Tian 2019 | GSE124703 | K562 | CRISPRi | 组合 | 训练/评估 |
| Replogle 2020 | GSE146194 | K562 | CRISPRi | 单 | 训练/评估 |
| Horlbeck 2018 | GSE116198 | K562 | CRISPRi | 组合 | 训练/评估 |

### 知识图谱数据

| 数据 | 来源 | 用途 |
|------|------|------|
| Gene Ontology | https://geneontology.org/ | 构建 GO 相似度图 |
| Tabula Sapiens | https://tabula-sapiens-portal.ds.czbiohub.org/ | 参考细胞类型 |

### 训练生成的图

- `graphs/coexpression/` — 由训练集基因 Pearson 相关性构建
- `graphs/go_similarity/` — 由 GO 条目 Jaccard 相似度构建

### 模型权重

- `models/` — GEARS 训练后的模型权重（不进普通 Git）

### 模型预测结果

- `results/predictions/` — 未见组合扰动的预测结果
- `results/metrics/` — 评估指标

## 快速开始

```bash
# 1. 安装环境
conda env create -f environment/environment.yml
conda activate gears

# 2. 安装 GEARS 和 PyTorch Geometric
pip install cell-gears
# 根据 PyTorch/CUDA 版本安装 PyG:
# pip install torch_geometric

# 3. 下载官方预处理的 Norman 数据
python scripts/download_gears_processed.py --dataset norman

# 4. 检查数据
python scripts/inspect_anndata.py data/processed/norman/norman_perturb_processed.h5ad

# 5. 构建图
python scripts/build_coexpression_graph.py --dataset norman
python scripts/build_go_graph.py

# 6. 训练（见 notebook）
jupyter notebook notebooks/02_train_gears_norman.ipynb
```

## GEARS 官方数据加载

```python
from gears import PertData

pert_data = PertData("./data")
pert_data.load(data_name="norman")      # Norman 2019
pert_data.load(data_name="adamson")     # Adamson 2016
pert_data.load(data_name="dixit")       # Dixit 2016
# Replogle 数据名称请以官方当前支持为准，不自行猜测
```

## 最小复现 (Norman)

```python
from gears import PertData, GEARS

pert_data = PertData("./data")
pert_data.load(data_name="norman")
pert_data.prepare_split(split="simulation", seed=1)
pert_data.get_dataloader(batch_size=32, test_batch_size=128)

model = GEARS(pert_data, device="cuda")
model.model_initialize(hidden_size=64)
model.train(epochs=20)

# 预测未见组合
model.predict([
    ["CBL", "CNN1"],
    ["FEV"]
])
```

## 评估指标

| 指标 | 说明 |
|------|------|
| Top-20 差异基因 MSE | 预测与真实 top-20 DE 基因的均方误差 |
| Pearson 相关系数 | 预测与真实表达变化的相关性 |
| 表达变化方向错误率 | 预测方向与真实方向不一致的比例 |
| Precision@10 | top-10 预测 DE 基因中的准确率 |
| 遗传相互作用 (R²) | 组合扰动效应的拟合优度 |
| ARI | 聚类调整兰德指数 |
| NMI | 归一化互信息 |
| 模型不确定性 | 模型预测的置信度/方差 |

## 大文件处理规则

- `.h5ad`、`.h5`、`.mtx`、`.fastq.gz` 和模型权重加入 `.gitignore`
- GitHub 只保存代码、元数据、下载脚本和小型示例
- 大型文件使用 DVC 或 Git LFS
- README 写明如何重新下载和生成
- 不把无法确认来源的第三方处理数据上传 GitHub

## 许可证

本项目代码仅供学术研究使用。数据版权归原始作者所有。
