# 阅读与复现笔记

- CellCap 官方仓库可能包含 simulation_data.h5ad、CellCap_1MPBMC_Mono.h5ad、CellCap_1MPBMC_Mono/model.pt。
- 如果文件不存在或需要 Git LFS，不伪造下载链接，在 README 中明确记录缺失情况和官方教程引用的预期路径。
- Norman GSE133344 下载公开补充文件，保留原始计数矩阵、基因列表、细胞 barcode、sgRNA/扰动标签、单扰动与组合扰动信息、质控元数据。
- 整理为 AnnData：.X 或 layers["counts"] 保存原始整数计数；.obs 保存扰动标签；.var 保存基因信息；.obsm["X_target"] 保存 multi-hot 扰动矩阵；.obsm["X_covar"] 保存协变量矩阵。
- EGA 数据（EGAS00001005376、EGAD00001007764）属于受控访问，只保存数据说明、accession、申请步骤、元数据和下载脚本模板。没有用户凭证和授权时，不尝试绕过访问控制，也不把受控人类数据上传到 GitHub。
- 大型文件（.h5ad、.h5、.mtx、.fastq.gz、.pt）不直接进入普通 Git，使用 .gitignore 排除。
- 论文 DOI 和第一作者待确认。
