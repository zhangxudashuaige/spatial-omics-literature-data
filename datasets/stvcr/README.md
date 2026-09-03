# stVCR 数据模块

本目录整理 [stVCR 正式论文](https://doi.org/10.1038/s41592-026-03010-3) 的模拟数据、蝾螈脑再生数据和三维果蝇胚胎数据。官方代码固定到提交 `26aa79a63eba7a5e21726b1eb95bf6bb61cfe699`，而不是不稳定的 `main` 分支。

## 五类内容必须区分

1. **实验原始数据**：CNGB `CNP0002068` 的蝾螈数据，以及果蝇 Stereo-seq 的原始来源；它们不是本仓库里的 H5AD。
2. **处理后数据**：ARTISTA 蝾螈数据、Spateo 提供的两个果蝇 H5AD，可直接用于 stVCR 教程的下游分析。
3. **模拟数据**：官方 GitHub `datasets/` 下的 rectangle、heart2duck、bio_prior 和 bio_prior_5pts。
4. **模型权重**：`tutorial/save_model` 的检查点，不是实验数据。
5. **模型生成结果**：`tutorial/save_results` 的插值、预测或分析输出，不是真实观测。

## 官方目录与命名差异

固定提交中的四个模拟目录为：

- `sim_data_rectangle`
- `sim_data_heart2duck`
- `sim_data_bio_prior`
- `sim_data_bio_prior_5pts`

教程为 `00_simulated_data_rectangle.ipynb`、`01_simulated_data_heart2cuck.ipynb`、`02_simulated_data_bio_prior.ipynb`、`03_ARTISTA_dynamics.ipynb` 和 `05_Drosophila3D.ipynb`。第二个教程写作 **heart2cuck**，实际数据目录写作 **heart2duck**；这是上游命名差异，本仓库只记录映射，不擅自重命名上游文件。

官方 `LICENSE` 不是简单 MIT：开放源代码使用 GPL-3.0，闭源或非 GPL 使用需要商业许可。数据本身仍需遵守各数据来源条款。

## 已核验的模拟数据结构

| 数据 | H5AD shape | 观测时间点 | 真实字段 |
|---|---:|---|---|
| rectangle | 9,858 × 3 | 0、0.5、1、1.5、2、2.5 | `obs: time, theta`; `obsm: X_input, spatial, spatial_gt` |
| heart2duck | 3,799 × 3 | 0、0.25、0.5、0.75、1 | 另有 `growth_rate`、`cell_type`、`spatial_velocity` |
| bio_prior | 4,349 × 3 | 0、1 | `obs/type`: type1 349、type2 4,000；`spatial` 与 `spatial_gt` |
| bio_prior_5pts | 10,819 × 3 | 0、0.25、0.5、0.75、1 | `obs/type`: type1 819、type2 10,000 |

每套还包含 `*_exp.pkl`、`*_spa.pkl` 和 `*_time.pkl` 连续真值序列：分别为表达数组、二维空间数组和时间值。序列长度依次为 rectangle 60、heart2duck 101、bio_prior 21、bio_prior_5pts 41。固定教程随机种子为 `19491001`。H5AD 中没有名为 `v`、`p`、`g` 的直接字段；不能把模型计算出的动力学量误写成原始文件变量。

## 获取与检查

```powershell
cd datasets/stvcr
python scripts/fetch_official_repo.py
python scripts/inspect_simulation_data.py raw/simulation
python scripts/download_drosophila.py --metadata-only
```

确认磁盘和来源条款后下载两个果蝇 H5AD：

```powershell
python scripts/download_drosophila.py --download
python scripts/inspect_h5ad.py raw/drosophila_3d --output inspection.local.json
```

蝾螈 ARTISTA 页面可能需要网页交互或登录；脚本只保存公开元数据与下载说明，不绕过权限。完整数据、模型权重和大型结果都被 `.gitignore` 排除。

本次 `E7–9h` 文件续传到 253,214,720 / 513,301,759 bytes 后安全中断，尚不能作为 H5AD 读取；脚本会从 `.part` 继续。`E9–10h` 尚未开始。准确状态见 [`download_status.json`](download_status.json)。

## 生物学时间点

- 蝾螈完整入口含 2、5、10、15、20、30、60 DPI；论文主要使用 2–20 DPI。
- 果蝇 `E7–9h` 在论文中映射为 `t=8`，`E9–10h` 映射为 `t=9.5`。
- 模拟数据的时间点和真实字段以检查脚本读出的 H5AD/PKL 内容为准，manifest 将“论文报告”和“文件验证”分开记录。

`sample/` 中的样例只能用于读取、CI 和结构展示，不能用于复现论文统计结论。
