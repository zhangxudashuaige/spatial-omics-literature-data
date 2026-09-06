# X-Cell 资源公开状态

> 本文件由 `scripts/check_resource_status.py` 自动生成。
> 最后更新: 待运行脚本后填充

## 检查结果摘要

| 资源 | 类型 | 状态 | 检查时间 |
|------|------|------|----------|
| X-Atlas/Pisces 训练数据 | HuggingFace Dataset | **Coming Soon** | 待检查 |
| X-Cell Mini 55M 模型 | HuggingFace Model | **Coming Soon** | 待检查 |
| X-Cell Ultra 4.87B 模型 | HuggingFace Model | **Coming Soon** | 待检查 |
| X-Cell 官方代码 | GitHub | 已公开 | 待检查 |
| Replogle-Nadig | HuggingFace Dataset | 已公开 | 待检查 |
| Parse-1M | HuggingFace Dataset | 已公开 | 待检查 |
| Tahoe-100M | HuggingFace Dataset | 已公开 | 待检查 |

## 详细检查

### X-Atlas/Pisces (https://huggingface.co/datasets/Xaira-Therapeutics/X-Atlas-Pisces)

- **数据仓库是否仍写着 Coming Soon**: 待检查
- **实际文件列表**: 待检查
- **每个文件大小**: 待检查
- **完整数据文件是否存在**: 待检查
- **检查时间**: 待检查

### X-Cell 模型 (https://huggingface.co/Xaira-Therapeutics/X-Cell)

- **模型权重文件是否存在**: 待检查
- **是否存在 .safetensors**: 待检查
- **是否存在 .bin**: 待检查
- **是否存在 .pt / .ckpt**: 待检查
- **实际文件列表**: 待检查
- **每个文件大小**: 待检查
- **检查时间**: 待检查

## 运行检查

```bash
python scripts/check_resource_status.py
```

脚本会访问官方 GitHub 和 Hugging Face API，检查资源状态并更新本文件。

**注意**: 如果资源仍为 Coming Soon，脚本不会报错退出，会输出"尚未公开"并保留官方链接。
