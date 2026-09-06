# PerturbQA Data

整理和查看论文 "Contextualizing Biological Perturbation Experiments through Language" 的数据项目。

> **论文**: https://arxiv.org/abs/2502.21290
> **官方代码**: https://github.com/genentech/PerturbQA
> **补充数据 (Zenodo)**: https://doi.org/10.5281/zenodo.14915312

**目标**: 建立一个结构清晰、可重复下载、可以查看 PerturbQA 数据内容的项目。不重新训练 Llama。

## 项目结构

```
perturbqa-data/
├── README.md
├── requirements.txt
├── LICENSES.md
├── .gitignore
├── data/
│   ├── benchmark/
│   │   ├── de/                    # differential expression 任务
│   │   ├── direction/             # direction of change 任务
│   │   └── gene_set_enrichment/  # gene set enrichment 任务
│   ├── knowledge_graph/           # 生物知识图谱
│   ├── gene_summaries/            # 基因自然语言摘要
│   ├── model_outputs/             # Summer 及消融模型输出
│   └── results/                   # 最终评价结果
├── scripts/
│   ├── download_data.py           # 从 Zenodo 下载数据
│   ├── inspect_benchmark.py       # 检查基准数据
│   ├── inspect_knowledge_graph.py # 检查知识图谱
│   └── inspect_model_outputs.py   # 检查模型输出
└── notebooks/
    └── explore_perturbqa.ipynb    # 数据探索 notebook
```

## 数据分类

### 原始单细胞 CRISPRi 表达数据
- 来源: 各原始论文 (Norman, Replogle 等)
- 内容: 单细胞基因表达矩阵
- 注意: 本项目不重新处理原始百万级单细胞矩阵，使用官方加工后的基准数据

### PerturbQA 加工后的问答标签
- 来源: 官方 PerturbQA 仓库和 Zenodo
- 细胞系: k562, rpe1, hepg2, jurkat, k562_set
- 任务:
  - **differential expression (DE)**: 预测扰动后的差异表达基因
  - **direction of change**: 预测基因表达变化方向 (上调/下调)
  - **gene set enrichment (GSE)**: 预测富集的基因集合

### 生物知识图谱
- 来源: Zenodo (kg.zip)
- 内容: 基因-基因、基因-通路、基因-疾病等关系
- 包含 CORUM 等数据库

### 基因自然语言摘要
- 来源: Zenodo (gene_summary.zip)
- 内容: 每个基因的自然语言功能描述

### Summer 及消融模型的输出
- 来源: Zenodo
  - summer_outputs.zip: Summer 模型完整输出
  - summer_enrichment.zip: Summer 富集分析结果
  - llm-nocot.zip: 无 Chain-of-Thought 消融
  - llm-noretrieve.zip: 无检索消融
- 内容: 模型对扰动问题的回答、检索到的案例、解析后的标签

### 最终评价结果
- 来源: Zenodo (results.zip)
- 内容: 各模型在各任务上的评估指标

## 数据关系图

```
原始单细胞表达矩阵
    ↓ 统计检验
PerturbQA 标签 (DE / direction / GSE)
    ↓ 联合
知识图谱 + 基因摘要
    ↓ Summer 预测
模型输出 (含检索案例和推理)
    ↓ 结果评估
评价指标 (准确率、AUROC、F1 等)
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 下载数据
python scripts/download_data.py --list          # 列出可用文件
python scripts/download_data.py --all           # 下载所有 (警告: 可能较大)
python scripts/download_data.py --file kg.zip   # 下载指定文件

# 3. 检查基准数据
python scripts/inspect_benchmark.py --task de --cell_line k562

# 4. 检查知识图谱
python scripts/inspect_knowledge_graph.py

# 5. 检查模型输出
python scripts/inspect_model_outputs.py

# 6. 探索 notebook
jupyter notebook notebooks/explore_perturbqa.ipynb
```

## 基准数据任务说明

### Differential Expression (DE)
- 输入: 扰动基因 + 细胞系背景
- 输出: 差异表达基因列表
- 评估: Top-k 准确率、AUROC、F1

### Direction of Change
- 输入: 扰动基因 + 基因列表
- 输出: 每个基因的表达变化方向 (上调/下调/不变)
- 评估: 方向准确率、Macro F1

### Gene Set Enrichment (GSE)
- 输入: 扰动基因 + 细胞系背景
- 输出: 富集的通路/基因集合
- 评估: 富集准确率、Jaccard 相似度

## 大文件处理规则

- 大型 zip 和解压后的大型数据不直接提交进 Git
- 已通过 `.gitignore` 排除
- 通过 `scripts/download_data.py` 自动下载
- GitHub 中只保存: 下载脚本、文件清单、来源 URL、校验信息、小型示例、数据查看代码、文档

## 许可证

详见 [LICENSES.md](LICENSES.md)。
- 官方代码: Genentech Non-Commercial Software License 1.0
- PerturbQA 数据和模型输出: CC BY 4.0
- CORUM: CC BY-NC 4.0
- 其他知识图谱数据: 保留各自来源许可证

## 注意

如果下载链接、实际压缩包名称或文件格式与论文描述不一致，以 Zenodo 和官方 GitHub 当前页面为准，并在 README 中记录差异，不自行猜测。
