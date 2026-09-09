# AdaPert 数据资源

整理论文 "AdaPert" 的数据资源，用于 GitHub 归档和后续复现。先核验和整理，不要求立即训练模型。

> **论文**: https://arxiv.org/abs/2602.18885v2

## 三类资源（分别整理，不混合）

### A. 扰动实验数据

| 细胞系 | 来源 | 状态 |
|--------|------|------|
| K562 | https://gwps.wi.mit.edu/ | 已登记 |
| RPE1 | https://gwps.wi.mit.edu/ | 已登记 |
| JURKAT | 待确认 | **未核实原始编号** |
| HEPG2 | 待确认 | **未核实原始编号** |

- 作者补充资源: https://plus.figshare.com/articles/dataset/21632564
- 论文: https://pmc.ncbi.nlm.nih.gov/articles/9380471/
- **注意**: 补充资源不等于完整单细胞计数数据。核对实际使用的筛选实验、表达文件和预处理子集。
- JURKAT、HEPG2 的原始编号目前未核实，从 AdaPert 官方材料继续追溯。未找到前标为待确认，不能下载任意同名细胞系数据充当论文数据。

### B. 生物知识图

- **来源**: https://string-db.org/
- **版本**: STRING v11.5 人类数据
- **内容**: 蛋白-蛋白关联边与置信度
- **处理**: 保存原始关联边与置信度，另存 HVG 过滤、top-k 等派生图，不覆盖原始文件
- **注意**: 明确区分论文不同图配置；蛋白ID到基因ID映射需记录

### C. 基因语义资源

- **代码**: https://github.com/yiqunchen/GenePT
- **数据**: https://zenodo.org/records/10833191
- **内容**: 官方预计算语义嵌入
- **记录**: 模型名称、维度、基因键和资源版本
- **注意**: 不要自动调用付费API生成新嵌入

## 统一数据清单

严格区分：
- 原始计数与归一化表达
- 原始数据与 AdaPert 处理子集
- 实验标签与计算产生的 DEG
- 知识图、文本嵌入与模型权重
- 官方文件与我们自行生成的文件

## 三类数据对应检查

核对表达矩阵的基因列表、STRING 节点和 GenePT 嵌入键。保存 ID 映射、重复名称、缺失基因及三者交集统计，不静默丢弃无法匹配的基因。说明哪些基因用于表达输出，哪些只作为图节点。

## 划分与防止泄漏

- 优先寻找官方扰动级划分，不能把同一扰动的细胞随机分到训练和测试
- 如果找不到官方划分，自建划分必须明确标注为自建，不能声称复现论文数值
- 训练用 DEG 和其他数据驱动预处理不能借用测试扰动响应；测试 DEG 单独保存，仅用于评价

## 最小查看示例

脚本或 Notebook 展示：
- 少量对照和处理组细胞的表达
- 一个扰动的标签、细胞数及平均表达变化
- 一个基因的知识图邻居
- 同一基因的语义向量维度
- 三类资源的 ID 对应关系

## GitHub 保存范围

- 上传 README、资源清单、下载与检查脚本、依赖配置、引用信息和允许再分发的小型示例
- 大型表达矩阵、完整知识图和嵌入文件放本地并加入 .gitignore
- 下载前先报告预计大小，不默认下载全部 FASTQ
- 核实许可证后再决定是否上传任何数据；代码许可不能替代数据许可

## 复现状态说明

- 继续核实 AdaPert 官方代码、权重及配置入口，不猜测仓库地址
- 论文的节点筛选、图规模和部分指标定义存在说明差异，记录为复现待核对项
- 当前能做到：数据查看 + 方法近似实现；严格论文复现待官方代码/权重公开

## 目录结构

```
adapert/
├── README.md
├── environment.yml
├── requirements.txt
├── .gitignore
├── data_manifest/
│   ├── datasets.csv
│   ├── id_mapping_stats.csv
│   └── data_dictionary.md
├── scripts/
│   ├── download_resources.py
│   ├── inspect_expression.py
│   ├── check_id_alignment.py
│   └── check_train_test_split.py
├── notebooks/
│   └── 01_resource_preview.ipynb
├── data/
│   ├── raw/          (不提交Git)
│   ├── processed/    (不提交Git)
│   └── examples/
└── results/
    └── gene_intersection_summary.csv
```
