# 数据目录

## 已核实

- SToCorpus-88M：Hugging Face 数据集，MIT，revision `6f699f128416e8d55d6ab74976e964caec98b157`。
- 官方代码：GitHub commit `2354d5799347867578793752e8c2dd93ae6587b7`，MIT。
- 下游数据入口：HEST、spatialLIBD、STDS0000139、SpatialOmics 184、STDS0000239、10x Xenium skin。

## 清单解释

`pretraining_sources.csv` 记录语料级事实；`huggingface_files.csv` 记录 1,869 个仓库对象；`downstream_datasets.csv` 记录论文任务入口；`downloaded_files.csv` 只记录真正落盘并计算 SHA256 的文件。清单中的 URL 不等于文件已经下载。

不同来源的许可证可能不同。Hugging Face 数据集卡的 MIT 标签不能自动替代每个上游生物数据集的原始使用条款，二次发布前仍需逐项核验。
