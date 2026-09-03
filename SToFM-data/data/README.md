# 本地数据目录

- `raw/`：未经本项目修改的下载文件。
- `processed/`：标准化、基因映射、tokenization 或模型输入。

两者均被 Git 忽略。每次下载后把远程路径、revision、本地路径、大小、SHA256 和日期写入 `manifests/downloaded_files.csv`。
