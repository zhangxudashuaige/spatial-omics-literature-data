# GraphSAGE 数据字典

GraphSAGE 官方输入由共享的 `<train_prefix>` 连接以下文件。节点 ID 在不同文件间必须一致，特征矩阵行号由 `id_map` 决定。

## `*-G.json`

NetworkX node-link JSON 图结构：

- `nodes`：节点列表；每个节点通常包含 `id`、`val`、`test`。
- `links`：边列表；端点通常写为 `source`、`target`。
- `val: true` 表示验证节点；`test: true` 表示测试节点；两者均为 false 的节点作为训练节点。
- PPI 是多图归纳设置，节点还可包含图 ID 等属性。

## `*-id_map.json`

把 JSON 图中的节点 ID 映射到从 0 开始的连续整数。这个整数是 `feats.npy` 的行索引。不要按节点 ID 的字典顺序猜测特征行。

## `*-class_map.json`

把节点 ID 映射为标签：

- 单标签任务可能是整数类别；
- PPI 等多标签任务通常是 0/1 向量，训练时需要 sigmoid 输出。

## `*-feats.npy`

节点特征矩阵，形状一般为 `节点数 × 特征数`。完整 NPY 只保存在本地；本仓库仅跟踪 MIT 许可的官方小样例文件。

## `*-walks.txt`

无监督训练使用的随机游走共现节点对，每行两个节点 ID。它不是图的边表，不能替代 `G.json`。

## 检查器输出

`inspect_graphsage.py` 会输出节点数、边数、训练/验证/测试节点数、特征矩阵 shape、标签条目/类型以及随机游走对数。它既能读目录，也能直接读 ZIP，避免为了检查而永久解压大型包。
