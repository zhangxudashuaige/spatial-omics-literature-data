# Notebook 说明

Notebook 默认优先读取 `data/external/GSE278603/h5ad/` 中的真实文件；若本机没有真实数据，它们会使用 `scripts/create_sample_data.py --synthetic` 生成的本地合成对象完成代码测试，并在标题中明确标注“合成测试数据”。

运行方式：

```powershell
jupyter lab notebooks
```
