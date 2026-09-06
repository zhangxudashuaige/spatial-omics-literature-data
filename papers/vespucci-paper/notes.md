# 阅读与复现笔记

- 所有数据来源必须从作者代码仓库、GEO、SRA、Zenodo、Broad Single Cell Portal或原始论文核实，不得根据名称猜测。
- GSE268779 是作者新产生的数据，包含小鼠脊髓损伤、衰老与再生治疗，10x Visium。必须从官方元数据或论文补充表核对每个 GSM 样本的 young/old/treated 标签，不根据样本编号猜测。
- Vespucci 模拟数据（spatial_sim、spatial_sim_distance_metrics_df）来自官方仓库，优先作为项目可运行示例。
- 下载脚本默认只下载元数据和小型处理后文件，不默认下载 SRA FASTQ。支持按 GSE 或 GSM 编号选择样本。下载前显示预计文件大小，已存在文件不重复下载，下载后计算 SHA256。
- 下载地址无法核实时停止，不得编造。需要登录的数据只写访问说明，不绕过权限。
- docs/file_relationships.md 解释 Visium 标准输出各文件关系：matrix.mtx、features.tsv、barcodes.tsv、tissue_positions.csv、scalefactors_json.json、tissue_hires_image.png、FASTQ、Seurat RDS、h5ad。
- 大型 FASTQ、GSE120374、GSE214611 或完整 GSE268779 不直接提交普通 Git 历史。大于 50 MB 的数据谨慎使用 Git LFS。
- .gitignore 排除 FASTQ、完整 MTX、H5、RDS 和大型图像。
