# 数据目录

存放 scPerturb 项目的所有数据文件。

**重要：不把 43 GB 原始数据直接提交到普通 Git 历史。**

## 目录结构

- `raw/` — 从 Zenodo 下载的原始 h5ad 文件
  - `AdamsonWeissman2016_GSM2406675_10X001.h5ad` (~34.6 MB，推荐首先下载)
  - `NormanWeissman2019_filtered.h5ad` (~698.7 MB，根据磁盘空间选择)
- `processed/` — 处理后的数据

## 如何获取数据

```bash
# 1. 获取 Zenodo 文件清单
python scripts/fetch_zenodo_manifest.py --record 13350497

# 2. 下载 Adamson 数据 (推荐首先下载)
python scripts/download_dataset.py --file AdamsonWeissman2016_GSM2406675_10X001.h5ad

# 3. MD5 校验
python scripts/verify_md5.py data/raw/AdamsonWeissman2016_GSM2406675_10X001.h5ad
```

## 数据来源

- **RNA和蛋白质**: https://zenodo.org/records/13350497
- **ATAC**: https://zenodo.org/records/7058382

## 大文件规则

- `.h5ad`、`.h5`、`.zip`、`.mtx` 不进入普通 Git
- 已通过 `.gitignore` 排除
- 如需版本管理，使用 Git LFS 或 DVC
- 不重新分发许可证不明确的数据
