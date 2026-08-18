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

这些代码块是 PowerShell 命令，不是在 GitHub 网页搜索框里输入。使用方法：

1. 打开仓库文件夹 `spatial-omics-literature-data`。
2. 在文件夹空白处按住 Shift 并单击右键，选择“在终端中打开”，或者先打开 PowerShell 再用 `cd` 进入仓库。
3. 运行 `rg --version`。能显示版本号就可以直接使用下列命令。
4. 如果提示“无法将 rg 识别为命令”，改用 `..\scripts\search.ps1` 的形式，或者在仓库根目录运行 `.\scripts\search.ps1 "标签"`。

命令结构：

```text
rg "要查找的文字" 要搜索的文件夹1 要搜索的文件夹2
```

- `rg`：ripgrep 程序名，是第三方开源工具，不是本仓库编写的。
- `"organism:mouse"`：要寻找的完整标签。
- `catalog papers`：只在总目录和论文目录里搜索。
- 命令只读取文件，不会修改或删除数据。

```powershell
# 找出所有小鼠数据
rg "organism:mouse" catalog papers

# 找出需要核实许可证的数据
rg "license:verify" catalog papers

# 找出已经下载的数据
rg "status:downloaded" catalog papers
```

不安装 `rg` 时，等价的仓库脚本是：

```powershell
.\scripts\search.ps1 "organism:mouse"
.\scripts\search.ps1 "license:verify"
.\scripts\search.ps1 "status:downloaded"
```
