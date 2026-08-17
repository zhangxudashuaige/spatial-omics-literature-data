# Jupyter 示例说明

## 文件

- `spatialvista_mouse_brain.ipynb`：逐步检查 `mouse_brain_3_IQ.h5ad`，然后调用 SpatialVista 小组件显示三维点云。
- `launch_jupyter.cmd`：Windows 一键启动脚本，双击后在 `spatialvista` Conda 环境中打开 notebook。

## 本机位置

克隆仓库后，这两个文件位于：

```text
papers/wei-2026-spatialvista/notebooks/
```

当前脚本按这台电脑的环境写成，Jupyter 程序路径是：

```text
D:\anaconda\envs\spatialvista\Scripts\jupyter-lab.exe
```

notebook 中的数据路径是：

```text
D:\test\data\mouse_brain_3_IQ.h5ad
```

如果以后移动 Conda 环境或数据，只需要修改这两个对应路径。`launch_jupyter.cmd` 不包含论文代码；它只是代替手工输入启动命令。notebook 是我们为检查下载文件编写的最小示例，也不是从论文正文复制的分析流程。
