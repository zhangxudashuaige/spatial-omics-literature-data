# DynaCLR 数据资源管理

整理论文 "DynaCLR" 的数据资源，用于 GitHub 归档和后续复现。当前先整理数据，不要求训练完整模型。

> **论文**: https://arxiv.org/abs/2410.11281v2

## 三类数据（分别建立记录，不混合）

### A. ALFI 细胞周期数据
- **来源**: https://doi.org/10.6084/m9.figshare.23798451
- **对应论文**: https://doi.org/10.1038/s41597-023-02540-1
- **内容**: 细胞周期相关的活细胞成像数据
- **本地路径**: `data/alfi_cellcycle/`

### B. Microglia / DynaMorph 数据
- **来源**: https://github.com/mehta-lab/dynamorph
- **示例**: https://drive.google.com/drive/folders/11GoWDwaBo1PE5FO5tcnGCOzA4pzjf-Tk
- **内容**: 小胶质细胞动态形态学数据
- **本地路径**: `data/microglia_dynamorph/`

### C. DynaCLR 感染与细胞器演示资源
- **来源**: https://drive.google.com/drive/folders/1SeQcWQcTF3Xfvz4XU_2DzMzGSxc-Hkgb
- **内容**: 感染与细胞器相关的演示数据
- **本地路径**: `data/dynaclr_infection/`

**重要**: 必须区分完整训练数据、测试数据、示例数据、模型权重和演示视频。不能因为下载了示例包，就报告已获得论文全部数据。

## 数据核验原则

- 先核验，再下载：核对官方文件清单、大小、格式、版本、许可证和访问权限
- 无法访问或需要申请的内容标为待获取，不编造下载链接，也不自动向作者发送邮件
- 优先下载一套可查看的小样本及配套轨迹
- 超过30GB的资源先列出文件大小和可选择的子集，再确认下载范围

## 图像与元数据关系

尽可能保存：
- 原始或处理后的图像
- 分割掩膜、边界框或细胞中心位置
- 轨迹ID、帧号和亲子关系
- 感染、分裂等标签及标签来源
- 细胞系、处理、病毒类型、视野、显微镜信息
- 通道名称、轴顺序、像素尺寸、时间间隔和深度间隔
- 人工标签、模型预测标签和伪标签必须分开记录
- 登革病毒与Zika数据不得未经核对混合

## 最小查看示例

读取脚本或Notebook能够：
- 输出图像形状、类型和轴含义
- 展示一个时间点的不同通道
- 展示同一细胞连续几个时间点的图像
- 显示对应轨迹ID及已有状态标签
- 检查图像、追踪文件和标签是否正确关联
- 使用适合多维图像的读取方式，避免把全部大型图像一次性加载进内存
- 不默认转换成单细胞转录组使用的h5ad

## 软件版本（单独记录）

| 软件 | 链接 | 用途 |
|------|------|------|
| VisCy | https://github.com/mehta-lab/VisCy | 代码 |
| napari-iohub | https://github.com/czbiohub-sf/napari-iohub | 可视化 |
| ultrack | https://github.com/royerlab/ultrack | 追踪 |
| waveorder | https://github.com/mehta-lab/waveorder | 相位重建 |

核对论文v2对应的代码版本与配置，不能将最新仓库的默认配置当成原论文配置。

## GitHub 归档要求

- 保存README、资源清单、下载脚本、检查脚本、查看示例、依赖配置和引用信息
- 大型图像、权重及缓存放本地并加入.gitignore
- 小样本能否上传需核对再分发许可
- 代码许可证不代表数据许可证
- 数据清单至少包含来源、网址、文件类别、大小、版本、用途、下载状态、本地路径和可获得的校验值

## 目录结构

```
dynaclr/
├── README.md
├── .gitignore
├── manifests/
│   ├── alfi_cellcycle.csv
│   ├── microglia_dynamorph.csv
│   ├── dynaclr_infection.csv
│   ├── software_versions.csv
│   └── data_dictionary.md
├── data/
│   ├── alfi_cellcycle/      (不提交Git)
│   ├── microglia_dynamorph/ (不提交Git)
│   └── dynaclr_infection/   (不提交Git)
├── scripts/
│   ├── download_alfi.py
│   ├── download_google_drive.py
│   ├── inspect_image.py
│   ├── check_tracking.py
│   └── verify_checksums.py
├── notebooks/
│   └── 01_inspect_dynaclr_data.ipynb
├── results/
└── code_refs/
    └── versions.md
```
