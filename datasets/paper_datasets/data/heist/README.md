# HEIST 数据目录

这里不保存 HEIST 的数百万细胞完整数据。`raw/` 用于本地代码快照、模型和生物数据，已被 Git 忽略；`sample/` 只允许放来源、版本和许可均已确认的小样例。

当前没有提交生物学小样例，因为官方仓库没有给出一个可独立追踪、许可明确的小型样本。不要用同名第三方数据替代。

```powershell
# 获取并记录官方仓库/模型元数据，不下载生物数据
py -3.13 ..\..\scripts\download_heist_resources.py metadata

# 检查 H5AD；PT/PTH 必须额外确认 pickle 风险
py -3.13 ..\..\scripts\inspect_heist_sample.py raw\example.h5ad
py -3.13 ..\..\scripts\inspect_heist_sample.py raw\example.pt --trust-pickle
```

每个本地下载文件都应在本地 inventory JSON 中记录 URL、固定 revision、下载时间、字节数、SHA256 和许可说明。详见 `../../docs/heist_data_dictionary.md`。
