# 标签规范

标签写在 CSV 的 `tags` 字段中，多个标签用英文分号 `;` 分隔。统一使用小写英文和连字符，避免同义词造成检索遗漏。

## 标签维度

| 前缀 | 用途 | 示例 |
|---|---|---|
| `topic:` | 研究主题 | `topic:spatial-transcriptomics` |
| `modality:` | 数据模态 | `modality:3d-st`, `modality:scrna-seq` |
| `organism:` | 物种 | `organism:human`, `organism:mouse` |
| `tissue:` | 组织/器官 | `tissue:brain`, `tissue:embryo` |
| `disease:` | 疾病或性状 | `disease:atrial-fibrillation` |
| `technology:` | 实验技术 | `technology:stereo-seq` |
| `software:` | 软件或工具 | `software:spatialvista` |
| `source:` | 数据来源类型 | `source:geo`, `source:public-gallery` |
| `license:` | 许可状态 | `license:open`, `license:restricted`, `license:verify` |
| `status:` | 本地处理状态 | `status:catalog-only`, `status:downloaded`, `status:processed` |
| `year:` | 论文年份 | `year:2026` |

## 状态规则

- `status:catalog-only`：只保存元数据与来源，尚未下载。
- `status:downloaded`：原始文件已下载并记录校验值。
- `status:processed`：已生成可复现的处理结果。
- `license:verify`：再使用或公开前必须核实许可。

## 检索示例

```powershell
# 找出所有小鼠数据
rg "organism:mouse" catalog papers

# 找出需要核实许可证的数据
rg "license:verify" catalog papers

# 找出已经下载的数据
rg "status:downloaded" catalog papers
```
