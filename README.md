# 空间组学论文与数据集

这是一个长期维护的个人研究资料库，用来记录值得保留的论文、公开数据集、下载方式、校验值和分析笔记。

## 使用原则

- Git 里保存：元数据、笔记、数据来源、下载脚本、校验值和小型结果。
- 大型数据不直接提交：原始数据放在本机 `data/`，该目录已被忽略。
- 出版商 PDF 默认不公开上传：只记录 DOI 和本机文件校验值；确认许可后再放入 `papers/<id>/attachments/`。
- 每个数据集记录来源、版本、许可证、获取日期和处理过程，以便复现。

## 当前收录

| ID | 论文 | 主题 | 状态 |
|---|---|---|---|
| `wei-2026-spatialvista` | SpatialVista as a unified ecosystem for high-performance visualization and exploration of 3D spatial transcriptomics data | 3D 空间转录组可视化 | 已建档；待逐项登记在线平台中的公开数据集 |

详见 [`papers/wei-2026-spatialvista/README.md`](papers/wei-2026-spatialvista/README.md)。

## 目录结构

```text
papers/                 每篇论文一个目录
  <paper-id>/
    README.md            论文摘要、价值、代码与数据入口
    datasets.csv         关联数据集清单
    notes.md             阅读和复现笔记
catalog/
  papers.csv             全库论文索引
  datasets.csv           全库数据索引
scripts/                 下载与校验辅助脚本
data/                    本机原始数据（不会提交 Git）
```

## 新增一篇论文

1. 复制 `templates/paper/`，将目录名改成 `作者-年份-关键词`。
2. 填写论文 `README.md`、`notes.md` 和 `datasets.csv`。
3. 在 `catalog/papers.csv` 与 `catalog/datasets.csv` 增加索引。
4. 数据下载到 `data/<paper-id>/raw/`，保留原文件名。
5. 运行 `scripts/checksum.ps1` 生成 SHA-256，记录到数据清单。
6. 提交 Git：`git add .`、`git commit -m "Add <paper-id>"`。

## 大数据的长期方案

开始阶段用“GitHub + 本地/云盘数据”最简单。以后如果需要版本化大型数据，可以接入 DVC、Git LFS、Zenodo 或 OSF；仓库继续保存索引与复现脚本，而不是复制所有公开原始数据。

