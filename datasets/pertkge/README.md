# PertKGE 数据资源

整理论文 "PertKGE" 的数据资源，用于 GitHub 归档。只进行数据归档与说明，暂时不要训练模型。

> **论文**: https://doi.org/10.1101/2024.04.08.588632 (2024预印本)
> **官方仓库**: https://github.com/myzhengSIMM/PertKGE
> **作者数据与模型**: https://drive.google.com/file/d/1jFo0dDAnUOzMoKHFqPRM4pd_loTFwmMa/view

**归类**: 药物靶点预测／扰动转录组知识图谱（不归入单细胞表达预测或空间转录组）

## 六类资源（分开整理，不混合）

### 1. 作者处理后的图谱数据
- Google Drive 数据包
- 包含三元组文件：cause.txt、process.txt、effect.txt、test.txt 等
- **注意**: 不根据名称猜测文件内容，需实际核验

### 2. 实体与关系映射及数据划分
- 实体编号映射（entity2id）
- 关系编号映射（relation2id）
- 训练/测试划分文件

### 3. 模型权重
- 作者训练的模型权重
- **注意**: 不猜测包内有模型权重，需实际核验

### 4. LINCS 上游表达数据
- **LINCS Phase I**: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE92742
- **LINCS Phase II**: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE70138

### 5. 生物知识数据库来源
- 知识图谱构建所用的生物数据库来源

### 6. 案例与对接资源
- 对接网格: https://drive.google.com/drive/folders/1wPcn7EaQldWbXONrRVd-ZOcBsNo6IXHw
- **注意**: 不默认作者案例目录包含全部湿实验原始数据

## 数据核验要点

- 优先检查官方数据包，核实 cause.txt、process.txt、effect.txt、test.txt 及其他实际文件
- 记录每个文件的路径、格式、大小、内容、用途、来源和校验值
- 检查三元组列顺序、实体编号和关系编号映射、训练测试划分方式
- 提供少量真实数据预览；若使用自制示例，明确标注"示意数据"
- 记录作者仓库 commit、数据版本和访问日期
- 区分 2024 年预印本与当前仓库对应版本；上游数据库最新版不能冒充论文原始版本

## 许可证

- 核实再分发许可。代码许可不能默认覆盖第三方数据
- 受限数据只保存入口与获取说明，不重新上传
- 下载失败、需要登录、文件缺失或大小未知时，明确标注状态，不写成已获取

## GitHub 保存范围

- 中文说明、资源清单、下载与检查脚本
- 许可允许的小型样例
- 大型表达文件、压缩包和模型权重保存在本地缓存，通过下载脚本与清单关联，不直接提交普通 Git

## 目录结构

```
pertkge/
├── README.md
├── environment.yml
├── requirements.txt
├── .gitignore
├── data_manifest/
│   ├── resources.csv
│   ├── file_manifest.csv
│   └── data_dictionary.md
├── scripts/
│   ├── download_pertkge_data.py
│   ├── inspect_kge_triplets.py
│   └── check_partition.py
├── notebooks/
│   └── 01_kge_sample_preview.ipynb
├── data/
│   ├── raw/          (不提交Git)
│   ├── processed/    (不提交Git)
│   └── examples/
└── results/
    └── triplet_stats.csv
```
