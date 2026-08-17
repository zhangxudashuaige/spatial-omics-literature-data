# 空间组学论文与数据资料库

这是一个长期维护的个人研究资料库，用来记录值得保留的论文、公开数据集、下载方式、校验值和分析笔记。

## 使用原则

- Git 里保存：元数据、笔记、数据来源、下载脚本、校验值和小型结果。
- 大型数据不直接提交：原始数据放在本机 `data/`，该目录已被忽略。
- 出版商 PDF 默认不公开上传：只记录 DOI 和本机文件校验值；确认许可后再放入 `papers/<id>/attachments/`。
- 每个数据集记录来源、版本、许可证、获取日期和处理过程，以便复现。

## 当前收录

| ID | 论文 | 主题 | 状态 |
|---|---|---|---|
| `wei-2026-spatialvista` | SpatialVista 软件论文 | 3D 空间转录组可视化 | 已建档；13 个展示数据已逐项登记 |
| `zhang-2023-whole-mouse-brain-merfish` | 成年小鼠全脑 MERFISH 图谱 | 小鼠脑、MERFISH | 已建档；对应 3 个展示数据 |
| `han-2025-mouse-brain-stereo-seq` | 小鼠全脑 Stereo-seq 图谱 | 小鼠脑、Stereo-seq | 已建档；对应 1 个展示数据 |
| `cheng-2024-mouse-embryo-3d` | E9.5/E11.5 小鼠胚胎三维转录组 | 小鼠胚胎、Stereo-seq | 已建档；对应 2 个展示数据 |
| `xie-2025-digital-mouse-embryo` | E7.5–E8.0 小鼠数字胚胎 | 小鼠胚胎、三维重建 | 已建档；对应 6 个展示数据 |
| `xiao-2024-human-gastrulation` | 人原肠胚三维重建 | 人胚胎、Stereo-seq | 已建档；对应 1 个展示数据 |

总入口见 [`papers/wei-2026-spatialvista/README.md`](papers/wei-2026-spatialvista/README.md)，13 个数据与 5 篇来源论文的对应关系见 [`dataset-sources.md`](papers/wei-2026-spatialvista/dataset-sources.md)。

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
  TAGGING.md             标签词表与检索规则
scripts/                 下载与校验辅助脚本
data/                    本机原始数据（不会提交 Git）
```

## 这里到底存什么

本仓库采用“索引和知识进 Git，大文件留在数据源或本地硬盘”的方式：

- GitHub 保存论文条目、数据集链接、accession、许可证状态、标签、笔记、下载/分析脚本和小型 notebook。
- `.h5ad`、FASTQ、图像等大型文件下载到本机 `data/<paper-id>/raw/`，由 `.gitignore` 阻止上传。
- 下载后计算 SHA-256，写回 CSV；以后即使文件改名，也能用校验值确认是不是同一份数据。
- 同一个数据在 SpatialVista 中是“展示版”，在原论文数据库中可能还有原始序列、表达矩阵、组织图像和处理后对象；本库分别注明，不把它们混成一个概念。

## 新增一篇论文

1. 复制 `templates/paper/`，将目录名改成 `作者-年份-关键词`。
2. 填写论文 `README.md`、`notes.md` 和 `datasets.csv`。
3. 在 `catalog/papers.csv` 与 `catalog/datasets.csv` 增加索引。
4. 数据下载到 `data/<paper-id>/raw/`，保留原文件名。
5. 运行 `scripts/checksum.ps1` 生成 SHA-256，记录到数据清单。
6. 提交 Git：`git add .`、`git commit -m "Add <paper-id>"`。

## 标签与查找

索引中的 `tags` 字段使用分号分隔的标准标签，例如：

```text
topic:spatial-transcriptomics;modality:3d-st;organism:mouse;status:catalog-only
```

标签命名和推荐词表见 [`catalog/TAGGING.md`](catalog/TAGGING.md)。例如，可用下面的命令查找全部 3D-ST 条目：

```powershell
rg "modality:3d-st" catalog papers
```

## 大数据的长期方案

开始阶段用“GitHub + 本地/云盘数据”最简单。以后如果需要版本化大型数据，可以接入 DVC、Git LFS、Zenodo 或 OSF；仓库继续保存索引与复现脚本，而不是复制所有公开原始数据。
