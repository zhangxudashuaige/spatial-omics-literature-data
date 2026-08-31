# 复现计划与边界

1. 固定官方代码 commit 与 SToCorpus revision。
2. 先运行文件清单脚本，按技术/组织挑选少量切片。
3. 记录所选文件的 LFS SHA256、下载时间和本地 SHA256。
4. 检查表达矩阵、坐标、物种、基因 ID；小鼠基因按作者说明映射到人类 Geneformer 词表。
5. 使用官方 `preprocessing/preprocess.py` 生成 `hf.dataset`。
6. 下载并校验 cell encoder 和 SE(2)-Transformer 权重。
7. 用 `get_embeddings.py` 生成 256 维嵌入，再运行任务头。

当前不能仅凭公开说明保证完全复现论文所有指标：作者 Drive 没有在静态 README 中给出每个 demo/权重的大小和 checksum，下游任务的精确划分与全部处理参数也需从论文代码进一步核对。GPU 依赖包含 CUDA 版 CuPy/RAPIDS，不能机械安装到所有机器。
