# 术语表

- **cell**：单细胞表达测量单位；空间数据中也可能是分割细胞或bin，不一定完全等价。
- **corpus**：用于预训练的大规模样本集合。
- **checkpoint / weights**：模型参数文件，不是训练数据。
- **raw data**：FASTQ、BAM、原始影像等初级实验输出。
- **processed data**：表达矩阵、H5AD、注释表、空间坐标等下游对象。
- **AnnData / H5AD**：单细胞常用数据结构；`X`通常是细胞×基因矩阵，`obs`是细胞元数据，`var`是基因元数据，`obsm`保存低维或空间坐标。
- **zero-shot evaluation**：不在目标数据标签上训练，直接评价预训练表示或提示能力。
- **fine-tuning**：在目标任务数据上继续优化模型参数。
- **validation**：用数据评价模型；不一定修改模型参数。
- **external reference**：用于细胞类型映射、先验知识或比较的外部图谱。
- **accession**：数据库中的稳定项目或样本编号，如GSE、GSM、SRP、E-MTAB。
