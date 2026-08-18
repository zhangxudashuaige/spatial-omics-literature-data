# 脚本说明

| 脚本 | 用途 | 是否联网 |
| --- | --- | --- |
| `check_availability.py` | 检查 CNP0005981、MOSTA3D 和 GEO 参考入口 | 是 |
| `download_data.py` | 按 manifest 评估大小、筛选和下载公开文件 | 下载时是 |
| `make_h5ad_sample.py` | 从真实 H5AD 抽取 1,000 个细胞 | 否 |
| `validate_data_contract.py` | 检查清单、统一路径、字段和示例引用 | 否 |

所有命令建议从总仓库根目录运行。当前 manifest 没有 `public + download_url` 的论文主数据条目，因此下载脚本会安全退出；这是来源状态，不是程序故障。
