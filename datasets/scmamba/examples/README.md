# 小型示例

本目录当前不提交真实 scMamba 数据样本。原因是作者 Dropbox 没有附带明确的数据再分发许可证。

用户在本地下载 `PBMC.h5mu` 并确认用途许可后，可运行：

```powershell
python scripts/create_small_sample.py datasets/multiome_pbmc/raw/PBMC.h5mu examples/PBMC.sample.h5mu --acknowledge-license
```

脚本固定随机种子，默认保留 200 个配对细胞，每个 RNA/ATAC 模态最多 500 个特征。生成文件用于读取和 CI 测试，不用于复现论文指标；`.h5mu` 默认仍被忽略，只有人工确认许可后才能修改 `.gitignore` 显式纳入某个文件。
