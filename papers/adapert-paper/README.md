# AdaPert 论文

论文：**AdaPert**（自适应扰动预测方法）。

- 论文：https://arxiv.org/abs/2602.18885v2
- 本仓库数据模块：[`datasets/adapert/`](../../datasets/adapert/)

AdaPert 是一个结合生物知识图和基因语义嵌入的自适应扰动预测方法。

本条目保存三类资源：
1. **扰动实验数据**：K562/RPE1（GWPS平台），JURKAT/HEPG2（原始编号待确认）
2. **生物知识图**：STRING v11.5 人类蛋白关联
3. **基因语义资源**：GenePT 预计算嵌入

复现状态：当前能做到数据查看 + 方法近似实现；严格论文复现待官方代码/权重公开。JURKAT/HEPG2 原始编号未核实，标为待确认。
