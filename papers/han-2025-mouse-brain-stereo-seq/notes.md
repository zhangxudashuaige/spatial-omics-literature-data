# 阅读与复现笔记

- 处理后数据与原始测序数据分开存：BSDC 是论文给出的处理后数据入口，`CNP0003837` 是原始数据 accession。
- CNGB 页面显示项目约 125.58 TB，完整数据需联系官方；不能把“项目入口”误写成“所有文件都能直接下载”。
- 在线系统确认了 `stereoseq.celltypeTransfer.2mice.all.tsv.gz` 和 `section_id_used_in_paper.tsv` 两个真实直链。
- `total_gene_T*.txt.gz` 与 `regions-mouse*.tsv` 目前只确认到官方文件模式，具体文件名必须从官方清单获得。
- `data/sample/` 是合成测试数据，不可用于论文复现或生物学结论。
