# 数据资料库严格维护规范

本规范适用于所有新建、迁移或更新的数据模块。关键词“必须”“不得”“应该”分别对应 MUST、MUST NOT、SHOULD。若官方资源不足以满足字段要求，必须写 `unresolved`，不得猜测或用同名替代数据补齐。

## 1. 唯一目录职责

```text
papers/<paper-id>/       论文说明、引用、阅读笔记；不保存完整实验数据
datasets/<dataset-id>/   数据模块、来源、manifest、下载与检查脚本；唯一数据入口
catalog/                 跨全库检索表
data/                    旧版兼容占位；不得再建立新项目
```

必须遵守：

1. 不得在仓库顶层新增 `*-data/`、`paper-datasets/` 或以论文名命名的数据目录。
2. 新数据模块必须位于 `datasets/<dataset-id>/`，`dataset-id` 使用小写英文和下划线。
3. 每篇论文必须在 `papers/<paper-id>/` 有独立记录；`paper-id` 使用 `第一作者-年份-关键词`。
4. 同一文件不得复制到多个模块。跨论文复用数据时，只登记同一官方来源和唯一模块路径。
5. `papers/` 负责解释“论文讲什么”，`datasets/` 负责解释“数据在哪里、怎样下载和验证”。

## 2. 数据模块标准结构

```text
datasets/<dataset-id>/
├── README.md
├── manifest.csv 或 manifest.yaml
├── sources.yaml                 # 来源较多时使用
├── checksums.sha256             # 下载完成后生成
├── scripts/
│   ├── download_*.py|ps1|R
│   ├── inspect_*.py|R
│   └── verify_checksums.py
├── raw/                         # 官方原始/处理后大文件，本地保存，不进Git
├── processed/                   # 本仓库生成的完整结果，不进Git
├── sample/                      # 许可允许的小样例
└── results/                     # 小型统计、图和报告
```

`README.md`、manifest 和下载脚本是最低必需项。没有下载脚本时，README 必须说明人工登录、申请或网页下载步骤以及不能自动化的原因。

## 3. Manifest 必需字段

每个可下载文件或逻辑数据集一行，至少记录：

| 字段 | 规则 |
|---|---|
| `resource_id` | 模块内唯一、稳定，不随本地文件名改变 |
| `name` | 官方数据名称，不自行改成相似名称 |
| `category` | `raw`、`processed`、`metadata`、`coordinates`、`image`、`annotation`、`model`、`code`、`reference` 之一 |
| `role_in_paper` | 预训练、评测、注释参考、可视化等用途 |
| `organism`、`tissue` | 不适用写 `not_applicable`，未知写 `unresolved` |
| `modality`、`technology` | 如 `scRNA-seq`、`MERFISH`、`Stereo-seq`、`CODEX` |
| `accession` | GEO/SRA/CNGB/Zenodo/Hugging Face 等稳定编号 |
| `source_url` | 直接官方页面或官方文件URL，不用搜索结果页 |
| `exact_version` | Census版本、Git commit、Zenodo record/revision等；未知写 `unresolved` |
| `file_name`、`file_format` | 必须来自官方清单或实际响应，不得猜测 |
| `expected_size_bytes` | 优先用字节整数；只知道网页显示值时注明 `reported` |
| `checksum_type`、`checksum` | 优先 SHA-256；官方只给 MD5 时同时保留 MD5 |
| `license` | 许可证或使用限制；不明确写 `verify_before_use` |
| `local_path` | 相对仓库根目录，必须位于对应模块 |
| `download_status` | 使用下面的受控状态 |
| `verification_status` | 使用下面的受控状态 |
| `download_date` | ISO 8601：`YYYY-MM-DD`；未下载留空 |
| `notes` | 缺口、登录要求、论文子集差异和不可复现原因 |

禁止把论文报告的细胞数当作已下载文件的实际 shape。两者必须分别记录为 `reported_*` 与 `observed_*`。

## 4. 受控状态词

`download_status` 只能使用：

- `not_started`：未下载。
- `metadata_only`：只取得网页/API清单。
- `partial`：文件不完整，严禁用于分析。
- `downloaded`：文件完整落盘，但尚未校验。
- `verified`：大小和 checksum 已通过。
- `restricted`：需要申请、账号或许可。
- `unavailable`：官方入口当前不可获取。
- `unresolved`：无法确认论文精确版本或文件身份。

`verification_status` 只能使用：

- `not_checked`
- `size_verified`
- `checksum_verified`
- `schema_verified`
- `failed`
- `unresolved`

只有 checksum 匹配后才能写 `download_status: verified`。`.part`、断点文件或仅能打开文件头都不算完整下载。

## 5. 来源和可追溯性

1. 来源优先级：作者/项目官方仓库、正式数据库、论文补充材料、作者指定对象存储。
2. 第三方镜像只能作为镜像登记，必须同时保存原始官方来源。
3. 必须固定 Git commit、Zenodo record、Hugging Face revision、Census version 或软件版本。
4. 论文未给精确 cell ID、切片清单或预处理版本时，标记 `reproducibility_status: unresolved`。
5. 不得静默使用名称相同但版本、物种、样本数或预处理不同的数据。
6. URL 检查通过不等于数据验证通过；必须区分“链接有效”和“文件已校验”。

## 6. 原始、处理后和生成结果必须分开

- `raw/`：从官方来源直接取得且不修改的文件。
- `processed/`：本仓库脚本产生的标准化、过滤、合并或重建结果。
- `sample/`：从已确认数据按固定随机种子抽取的小样例。
- `results/`：统计表、图、schema 报告和Notebook输出。
- 模型权重不是数据；模型预测结果不是真实观测数据。

处理脚本必须记录输入文件 checksum、参数、随机种子、软件版本和输出文件 checksum。不得覆盖 `raw/` 中的文件。

## 7. Git与大文件红线

1. 普通Git中单文件必须小于100 MiB；本仓库进一步规定：未经人工审核，超过10 MiB不得提交。
2. FASTQ、BAM、H5AD、H5MU、H5、GEF、GEM、TIFF、RDS、NPY/NPZ、PT/PTH、ZIP/TAR 和完整大型CSV默认不提交。
3. 大文件必须保存到模块的 `raw/`、`processed/` 或外部对象存储，并由 `.gitignore` 排除。
4. 如需版本管理大文件，先评估 DVC、Git LFS、Zenodo、OSF 或机构对象存储；不得直接 `git add -f`。
5. 不得提交访问令牌、Cookie、账号、受限人类测序片段或个人信息。

提交前必须运行：

```powershell
python .\scripts\validate_repository.py
git status --short
git diff --check
```

## 8. 小样例规范

小样例只有在许可证允许且不含敏感数据时才能提交：

- 每种细胞类型最多10个细胞，通常总计100–1000个细胞；
- 最多500个基因/特征；
- 单文件目标小于10 MiB；
- 固定随机种子并记录抽样代码；
- 保留必要坐标、cell type、sample、batch和donor字段；
- README 必须注明“仅用于读取、CI和结构展示，不用于复现论文指标”；
- 人类原始reads不得作为样例提交。

## 9. 下载与检查脚本规范

下载脚本必须：

- 默认只列清单或下载小样例；预计超过1 GB时先显示总大小并要求显式确认；
- 支持续传、重试、超时和明确失败退出码；
- 保留官方文件名；
- 下载后计算 SHA-256，并更新本地清单；
- 不在代码中硬编码凭据。

检查脚本必须：

- 对稀疏矩阵保持稀疏，不整体转成 dense；
- 输出 shape、dtype、字段、坐标、标签、NaN/Inf、重复ID和稀疏度；
- 使用只读/backed模式检查大型H5AD/H5MU；
- 错误时返回非零退出码，不得用空结果伪装成功。

## 10. README 最低内容

每个模块的中文 README 必须回答：

1. 数据来自哪篇论文、哪个官方项目；
2. 每类文件是什么，不同数据之间是什么关系；
3. 哪些已下载、哪些只建档、哪些受限或未解决；
4. 如何在 Windows PowerShell 中下载、校验、检查和分析；
5. 完整数据为什么不在GitHub；
6. 许可证、引用和使用限制；
7. 当前复现能做到什么、不能做到什么。

## 11. 全库同步规则

新增或修改模块时，必须同步：

1. `datasets/<dataset-id>/README.md` 与 manifest；
2. `papers/<paper-id>/` 论文记录；
3. `catalog/papers.csv`、`catalog/datasets.csv`，需要时更新 `catalog/resources.csv`；
4. `datasets/README.md` 的模块入口与真实状态；
5. `DATA_INDEX.md` 的中文状态摘要；
6. `.gitignore`；
7. 下载/检查脚本的最小测试。

## 12. 完成定义

一个条目只有同时满足以下条件才称为“已整理”：

- 官方论文和数据来源可追踪；
- 精确版本或未解决原因已写明；
- manifest 字段完整；
- 下载脚本或人工下载步骤可执行；
- 大文件未进入普通Git；
- 已下载文件有大小和checksum；
- 数据结构检查结果可复现；
- README、catalog、总索引同步；
- `validate_repository.py` 通过；
- 提交已推送，并报告 commit SHA。

“已建目录”“已保存链接”不得表述为“完整数据已下载”。

## 13. 交给另一个工作区的启动指令

新工作区开始前应执行：

```powershell
git switch main
git pull --ff-only
Get-Content .\docs\DATA_REPOSITORY_STANDARD.md
python .\scripts\validate_repository.py
```

然后只在 `datasets/` 增加或更新数据模块。完成后再次运行验证，报告实际下载文件、大小、checksum、未解决项和Git commit SHA。
