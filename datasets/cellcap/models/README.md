# 模型目录

存放 CellCap 训练后的模型权重。

**重要：模型权重文件（.pt, .pth, .ckpt）不提交到普通 Git 历史。**

## 预期模型

- `CellCap_1MPBMC_Mono/model.pt` — 在单核细胞数据上预训练的 CellCap 模型

## 如何获取

1. 从官方 CellCap 仓库或配套资源下载预训练模型
2. 或使用 `configs/monocytes.yaml` 自行训练

## 导出内容

加载模型后可导出：
- `Z_basal` — 基础表达潜变量
- `H` — 响应程序矩阵
- `beta` — 扰动系数
- `h` — 程序活性
- 响应程序 top 基因
