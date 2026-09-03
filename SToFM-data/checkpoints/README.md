# 模型权重

官方入口：<https://drive.google.com/drive/folders/1mHE8gf8MAPwzZoEB0vwOOfQ4lz3H_-xo?usp=sharing>

官方代码固定 commit `2354d5799347867578793752e8c2dd93ae6587b7` 的 `get_embeddings.py` 需要：

- cell encoder 目录：`cell_bert/` 与 `cell_proj.bin`；
- SE(2)-Transformer：`config.json` 与 `se2transformer.pth`；
- 处理后数据：每个样本目录下 `data.h5ad` 与 `hf.dataset`。

Drive 静态 README 未列出文件大小与 checksum，因此本项目不猜测。下载后应写入 `manifests/downloaded_files.csv`。所有权重路径均被 Git 忽略。
