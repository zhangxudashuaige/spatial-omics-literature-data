# 数据总索引：数据在哪里、是否已下载、如何取得

这个仓库不是大型数据镜像。GitHub 保存论文记录、真实下载地址、文件清单、校验值和脚本；大型表达矩阵、FASTQ、图像和权重保存在本机被忽略的 `raw/`、`external/` 或 `processed/` 目录。

状态含义：

- **已校验**：完整文件已下载，大小和 SHA256/MD5 已核对。
- **部分下载**：本机有 `.part` 或不完整文件，不能用于分析。
- **仅建档**：已经确认官方入口和数据关系，但没有下载大文件。
- **待确认**：论文没有公布精确版本、cell ID 清单或许可证，不能用同名第三方数据冒充。

## 当前数据状态

| 论文/模型 | GitHub 资料入口 | 本机完整数据 | 当前缺口或下一步 |
|---|---|---|---|
| SpatialVista | [`papers/wei-2026-spatialvista/`](papers/wei-2026-spatialvista/) | 无全量副本 | 13 个展示数据以官方链接为主 |
| 全脑 MERFISH（Zhang 2023） | [`papers/zhang-2023-whole-mouse-brain-merfish/`](papers/zhang-2023-whole-mouse-brain-merfish/) | 无全量副本 | 从 Allen/BIL/CELLxGENE 按动物下载 |
| 小鼠脑 Stereo-seq（Han 2025） | [`papers/han-2025-mouse-brain-stereo-seq/`](papers/han-2025-mouse-brain-stereo-seq/) | 无全量副本 | CNGB/BSDC 按登录和许可获取 |
| 小鼠胚胎 MOSTA3D（Cheng 2024） | [`papers/cheng-2024-mouse-embryo-3d/`](papers/cheng-2024-mouse-embryo-3d/) | 无 | CNP0005981 当前公共接口不可取，保持未公开状态 |
| 数字小鼠胚胎（Xie 2025） | [`papers/xie-2025-digital-mouse-embryo/`](papers/xie-2025-digital-mouse-embryo/) | 无六个正式 H5AD | 官方链接已确认；本机 TLS 下载失败，可重跑下载脚本 |
| 人 CS8 胚胎（Xiao 2024） | [`papers/xiao-2024-human-gastrulation/`](papers/xiao-2024-human-gastrulation/) | 补充表/清单 | 约 2 TB FASTQ 未下载；384 个官方文件已逐项登记 |
| GraphSAGE | [`paper-datasets/`](paper-datasets/) | PPI ZIP 与官方 toy PPI 已校验 | Reddit 仅部分下载；WoS Citation 需要许可 |
| TABULA | [`paper-datasets/`](paper-datasets/) | 无论文精确 15M 训练集 | 精确 Census 版本和完整 cell ID 清单未公开 |
| HEIST | [`paper-datasets/`](paper-datasets/) | 只有资源元数据 | 22.3M 预训练集不是统一包；多数精确文件仍待确认 |
| Cell-GraphCompass | [`datasets/cell_graph_compass/`](datasets/cell_graph_compass/) | 无完整 scData.zip | 已下载约 224.9 MB/2.642 GB；继续运行 `download_zenodo.py --download` |
| stVCR | [`datasets/stvcr/`](datasets/stvcr/) | 四套官方模拟数据 | 果蝇 E7–9h 部分下载，E9–10h 未开始；蝾螈门户需人工操作 |
| SCTrans | [`datasets/sctrans/`](datasets/sctrans/) | Zheng68K 官方矩阵 | 论文 68,450 标签子集仍缺；其余六套尚未完整取得 |
| scMamba | [`scmamba-data/`](scmamba-data/) | PBMC.h5mu 已校验 | 其余七套论文精确处理输入未定位/未下载 |
| SpaGCN | [`spagcn-data/`](spagcn-data/) | 151673 表达矩阵与坐标 | 图像、邻接矩阵及其余论文数据未下载 |
| SToFM | [`SToFM-data/`](SToFM-data/) | 无语料文件 | 已保存 1,869 文件、979.49 GB 官方清单；按文件选择下载 |

## 最常用的下载入口

```powershell
# GraphSAGE PPI/Reddit
cd paper-datasets
.\scripts\download_graphsage.ps1 -Dataset PPI
.\scripts\download_graphsage.ps1 -Dataset Reddit

# Cell-GraphCompass：续传2.64 GB官方Zenodo包
cd ..\datasets\cell_graph_compass
python scripts\download_zenodo.py --download

# stVCR：续传两套果蝇H5AD
cd ..\stvcr
python scripts\download_drosophila.py --download

# SToFM：先看清单，再只下载明确选择的文件
cd ..\..\SToFM-data
python scripts\list_huggingface_files.py
python scripts\download_selected_files.py --pattern "10x/human_brain.h5ad"
```

每个模块自己的 README 是最终准则。不要仅根据目录存在就判断数据已经下载；应查看 manifest 中的 `download_status`、文件大小和 checksum。

