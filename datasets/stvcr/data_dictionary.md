# stVCR 数据字典

## 模拟 H5AD

- `X`：3 个模拟基因的观测表达，实际为 float64 HDF5 dataset。
- `obs/time`：被观测的时间点。
- `obs/theta`：模拟旋转角（弧度）。
- `obs/type`：bio-prior 数据的两组细胞。
- `obs/cell_type`、`obs/growth_rate`：heart2duck 的三组细胞及组特异生长率。
- `obsm/X_input`：3 维模型表达输入。
- `obsm/spatial`：模型输入二维坐标。
- `obsm/spatial_gt`：模拟真实二维坐标。
- `obsm/spatial_velocity`：仅 heart2duck 存在的真实/模拟空间速度。

## 连续真值 pickle

- `*_exp.pkl`：每个连续时间值一个 `n_t × 3` float64 表达数组。
- `*_spa.pkl`：每个连续时间值一个 `n_t × 2` float64坐标数组。
- `*_time.pkl`：连续时间值列表。

Pickle 可在加载时执行代码；检查脚本默认只读 opcode，只有对固定官方提交获取的文件显式传 `--trusted-pickle` 才反序列化。

果蝇和蝾螈真实字段必须下载后由 `inspect_h5ad.py`/门户文件清单验证，本字典不预设列名。

