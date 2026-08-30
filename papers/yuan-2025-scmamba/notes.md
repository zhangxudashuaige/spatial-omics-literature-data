# 阅读与复现笔记

- 论文数据规模来自附录数据集描述；实际 shape 必须以下载文件检查结果为准。
- 官方 RNA+ATAC 代码要求 `rna`/`atac` 模态，RNA+ADT 要求 `rna`/`adt`，默认标签列为 `cell_type`。
- 官方代码 commit 中 README 提及 `train_script.py`，但仓库没有该文件。
- 作者 Dropbox 在 2026-08-30 只列出 `PBMC.h5mu`（775,504,179 bytes），`checkpoints/` 为空。
- Dropbox 未附独立数据许可证；真实小样本不公开再分发。
