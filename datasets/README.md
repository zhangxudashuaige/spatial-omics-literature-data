# 统一数据目录

这里是本仓库唯一的数据模块入口。论文介绍和阅读笔记在 `papers/`，全库表格索引在 `catalog/`；数据来源、manifest、下载脚本、检查脚本和本地大文件目录统一放在这里。

| 模块 | 内容 | 当前本地状态 |
|---|---|---|
| [`cell_graph_compass/`](cell_graph_compass/) | Cell-GraphCompass | `scData.zip` 部分下载，不能用于分析 |
| [`paper_datasets/`](paper_datasets/) | GraphSAGE、TABULA、HEIST | GraphSAGE PPI 与 toy 已校验；TABULA/HEIST 主要为来源清单 |
| [`scmamba/`](scmamba/) | scMamba | PBMC.h5mu 已校验 |
| [`sctrans/`](sctrans/) | SCTrans | Zheng68K 官方矩阵已下载；精确标签子集待确认 |
| [`spagcn/`](spagcn/) | SpaGCN | 151673 表达矩阵与坐标已下载 |
| [`stofm/`](stofm/) | SToFM | 已生成 979.49 GB 官方文件清单，未下载全量语料 |
| [`stvcr/`](stvcr/) | stVCR | 四套模拟数据完整；真实果蝇/蝾螈数据不完整 |

## 每个模块的统一约定

```text
datasets/<模块>/
├── README.md             数据是什么、怎样获取、能否复现
├── manifest.*            文件、来源、版本、大小、校验值和状态
├── scripts/              下载、检查与抽样脚本
├── raw/                  本地原始大文件，不提交Git
├── processed/            本地处理结果，不提交Git
└── sample/ 或 examples/  许可允许的小型测试数据
```

目录存在不代表完整数据已经下载。开始分析前应同时检查模块 README、manifest 的状态、文件大小和 checksum。全库的中文状态汇总见 [`../DATA_INDEX.md`](../DATA_INDEX.md)。

## Windows PowerShell 使用方式

从仓库根目录进入需要的模块，例如：

```powershell
cd .\datasets\stvcr
python .\scripts\inspect_simulation_data.py --help
```

下载后的大文件仍在对应模块的 `raw/` 内，因此“统一目录”不会把数百 GB 数据塞进普通 Git 历史。
