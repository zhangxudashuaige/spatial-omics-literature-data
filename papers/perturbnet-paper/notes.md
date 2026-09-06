# 阅读与复现笔记

- PerturbNet 三个任务的输入输出：
  - 药物：SMILES + 剂量 + 细胞背景 + 噪声 → 扰动后单细胞表达矩阵
  - 基因扰动：GO功能向量 + 细胞背景 + 噪声 → 扰动后单细胞表达矩阵
  - 蛋白质突变：氨基酸序列嵌入 + 细胞背景 + 噪声 → 扰动后单细胞表达矩阵
- 作者 HuggingFace 仓库（cyclopeta/PerturbNet_reproduce）包含 data_paper、example_data、models、pretrained_model。
- 第一阶段只下载 example_data 中的小型教程数据、README和配置文件、必要的数据字典、小型模型配置、BioStudies补充表格。
- 第二阶段根据空间决定是否下载 data_paper、models、pretrained_model、GEO原始数据。没有用户确认不自动下载全部大型文件。
- 大型文件（data/raw/、data/processed/、data/model_weights/）全部加入 .gitignore。
- 如果文件不是 h5ad，先识别格式再使用相应读取库，不通过修改扩展名强行读取。
- data_dictionary.md 重点解释 expression matrix、perturbation label、SMILES、GO vector、protein sequence、dose、cell type/cell line、generated cells、control。
