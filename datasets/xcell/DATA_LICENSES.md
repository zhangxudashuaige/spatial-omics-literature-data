# 数据许可证

本文档记录 X-Cell 数据项目中所有资源的许可证。

**重要**: 每个外部数据和先验保留自身许可证，不统一改成 MIT。如果某资源许可证不明确，标记为"需要人工确认"。

## 1. X-Cell 项目本身

| 资源 | 许可证 | 来源 |
|------|--------|------|
| X-Cell 官方代码 | 待确认（GitHub 页面） | https://github.com/Xaira-Therapeutics/X-Cell |
| X-Cell 模型页面 | **CC BY-NC-SA 4.0** | https://huggingface.co/Xaira-Therapeutics/X-Cell |
| X-Atlas/Pisces 数据页面 | **CC BY-NC-SA 4.0** | https://huggingface.co/datasets/Xaira-Therapeutics/X-Atlas-Pisces |

> CC BY-NC-SA 4.0: 署名-非商业性使用-相同方式共享 4.0 国际
> - 允许：共享、改编
> - 限制：非商业性使用、相同方式共享、署名
> - 详情: https://creativecommons.org/licenses/by-nc-sa/4.0/

## 2. 外部评测数据

### Replogle-Nadig
- **链接**: https://huggingface.co/datasets/arcinstitute/Replogle-Nadig-Preprint
- **许可证**: 需要人工确认（HuggingFace 页面查看）
- **备注**: 预印本数据，使用前请确认许可证

### Parse-1M
- **链接**: https://huggingface.co/datasets/arcinstitute/State-Parse-Filtered
- **许可证**: 需要人工确认（HuggingFace 页面查看）
- **备注**: ARC Institute 发布

### Tahoe-100M
- **链接**: https://huggingface.co/datasets/tahoe-bio/Tahoe-100M
- **许可证**: 需要人工确认（HuggingFace 页面查看）
- **备注**: Tahoe Bio 发布

### melanocyte progenitor
- **链接**: 待确认
- **许可证**: 需要人工确认
- **备注**: 数据来源待确认

### primary human CD4+ T cells
- **链接**: 待确认
- **许可证**: 需要人工确认
- **备注**: 数据来源待确认

## 3. 生物先验

### GenePT
- **链接**: https://zenodo.org/records/10833191
- **许可证**: 需要人工确认（Zenodo 页面查看）
- **备注**: GenePT 基因嵌入

### ESM-2
- **链接**: https://github.com/facebookresearch/esm
- **许可证**: MIT（代码）；模型权重可能有额外限制
- **备注**: Facebook AI Research 发布的蛋白质语言模型

### STRING
- **链接**: https://stringdb-downloads.org/download/protein.network.embeddings.v12.0.h5
- **许可证**: 需要人工确认（STRING 网站查看）
- **备注**: STRING 数据库蛋白质网络嵌入

### DepMap 24Q4
- **链接**: https://plus.figshare.com/articles/dataset/DepMap_24Q4_Public/27993248
- **许可证**: 需要人工确认（figshare 页面查看）
- **备注**: Broad Institute DepMap 项目

### JUMP Cell Painting
- **链接**: https://jump-cellpainting.broadinstitute.org/
- **许可证**: 需要人工确认（JUMP 网站查看）
- **备注**: JUMP-CP 细胞绘画数据集

### scGPT
- **链接**: https://github.com/bowang-lab/scGPT
- **许可证**: 需要人工确认（GitHub 页面查看）
- **备注**: 单细胞生成式预训练模型

## 4. 使用注意事项

1. **商业使用**: X-Cell 模型和数据标注 CC BY-NC-SA 4.0，**禁止商业使用**。商业使用请联系 Xaira Therapeutics。
2. **再分发**: 不要重新分发许可证不明确的数据。
3. **署名**: 使用任何资源时，请按照对应许可证要求署名。
4. **相同方式共享**: 如果改编 CC BY-SA 类资源，衍生作品必须使用相同许可证。
5. **人工确认**: 标记为"需要人工确认"的资源，使用前必须到官方页面确认实际许可证。

## 5. 检查许可证

运行以下脚本可以检查 HuggingFace 资源的许可证信息：

```bash
python scripts/check_resource_status.py
```

脚本会访问 HuggingFace API，获取数据集和模型的许可证元数据。
