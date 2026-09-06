# 阅读与复现笔记

- 三类训练数据的关系：LINCS 提供药物诱导基因表达变化；PharmacoDB 提供药物剂量-细胞抑制率；PubChem 提供药物结构。三者联合用于训练 LightGBM。
- AML 患者原始数据在 SRA（SRR30720406/407/408），download_sra.ps1 默认只显示文件和预计大小，需用户明确确认后才真正下载。
- EGA 数据（AML: EGAS00001004614/4444；HGSC: EGAS00001005010/5066）属于受控人类数据，只记录编号、链接和申请流程，不尝试绕过权限下载，不上传到 GitHub。
- 处理后 Seurat 对象在 Zenodo（13340927），优先下载；inspect_seurat.R 可展示对象大小、细胞/基因数、metadata、患者分布、细胞类型、UMAP 等。
- 作者提供 Docker 镜像（kmnader/sctherapy 和 kmnader/sctherapy_v5），可用于复现分析环境。
- 大型二进制数据（FASTQ、BAM、Seurat RDS）不进入普通 Git，data/raw 和 data/processed 加入 .gitignore。
