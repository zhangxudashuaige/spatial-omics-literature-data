# 阅读与复现笔记

- 截至当前官方页面，X-Cell 权重、完整推理代码和完整 X-Atlas/Pisces 数据仍标注 Coming Soon。
- 不伪造下载成功，不创建假的 .h5ad 文件，也不把只有 24.3 kB 的说明文件误认为 2560 万细胞数据。
- check_resource_status.py 访问官方 GitHub 和 Hugging Face API，检查数据仓库是否仍写着 Coming Soon、实际文件列表、每个文件大小、模型权重文件是否存在（.safetensors/.bin/.pt/.ckpt），把结果写入 RESOURCE_STATUS.md。
- 只有确认文件真实存在后才能下载。若不存在，输出"尚未公开"，保留官方链接，不报错退出，不创建伪数据。
- make_small_example.py 只能从真实公开数据抽取小样本（100对照+100扰动，最多500基因）。如果原始数据尚未公开，则跳过，绝对不要生成随机伪数据冒充真实数据。
- 许可证：X-Cell 项目和模型页面标注 CC BY-NC-SA 4.0；每个外部数据和先验保留自身许可证；不统一改成 MIT；如果某资源许可证不明确，标记为"需要人工确认"。
- 大型数据（.h5ad、.h5、.parquet、.zarr、.loom、.safetensors、.bin、.pt、.ckpt）全部加入 .gitignore，data/** 全部排除，只保留 .gitkeep。
- 当前项目首先是数据目录、下载器和检查工具，不宣称已经复现 X-Cell。官方完整数据、权重和推理实现发布后，再更新下载和运行流程。
