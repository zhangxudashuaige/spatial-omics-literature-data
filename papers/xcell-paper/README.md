# X-Cell 论文

论文：**X-Cell**（单细胞基础模型）。

- 论文：<https://doi.org/10.64898/2026.03.18.712807>
- 官方代码：<https://github.com/Xaira-Therapeutics/X-Cell>
- 官方模型：<https://huggingface.co/Xaira-Therapeutics/X-Cell>
- 官方训练数据：<https://huggingface.co/datasets/Xaira-Therapeutics/X-Atlas-Pisces>
- 本仓库数据模块：[`datasets/xcell/`](../../datasets/xcell/)

X-Cell 是一个用于单细胞扰动预测的基础模型，包含 X-Cell Mini（55M 参数）和 X-Cell Ultra（4.87B 参数）两个规模。核心训练数据 X-Atlas/Pisces 包含 25.6M 细胞、7 个 CRISPRi screen、16 种细胞背景。

**重要：截至当前官方页面，X-Cell 权重、完整推理代码和完整 X-Atlas/Pisces 数据仍标注 Coming Soon。** 不伪造下载成功，不创建假的 .h5ad 文件，也不把只有 24.3 kB 的说明文件误认为 2560 万细胞数据。项目记录资源状态，并提供将来数据公开后可以运行的下载脚本。

本条目保存 X-Atlas/Pisces 训练数据清单、外部评测数据集（Replogle-Nadig、Parse-1M、Tahoe-100M 等）、生物先验（GenePT、ESM-2、STRING、DepMap、JUMP Cell Painting、scGPT）、模型资源状态和下载/检查脚本。
