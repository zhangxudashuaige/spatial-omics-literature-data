# 模型与配置记录

- 官方代码：<https://github.com/23AIBox/scMamba>
- 固定 commit：`4887c0a8ab060b2482384d2294fe265b633d2406`
- 代码许可证：AGPL-3.0
- 作者 Dropbox：<https://www.dropbox.com/scl/fo/g64416xvv1fjd36l1z7nx/AKcB6XbOFHLPFHQX68TpGCQ?rlkey=1i3grodznoch33gihjqn74oc9&dl=0>
- 2026-08-30 实检：`checkpoints/` 为空，不能填写模型文件大小或 SHA-256。

官方 `scmamba2_config.json` 的两个编码器均为 `d_model=512`、`patch_size=256`、`d_embedding=64`；RNA 分支 10 层、ATAC 分支 12 层。RNA+ADT 配置使用同样的 `d_model=512` 与 `d_embedding=64`，RNA/ADT 的 `patch_size` 分别为 256/128，层数分别为 8/4。请始终从固定 commit 获取原配置：

<https://raw.githubusercontent.com/23AIBox/scMamba/4887c0a8ab060b2482384d2294fe265b633d2406/config_files/scmamba2_config.json>

官方推理示例引用 `PBMC.pt`，但公开目录当前并无该文件。因此本仓库不生成假检查点，也不填假校验值。
