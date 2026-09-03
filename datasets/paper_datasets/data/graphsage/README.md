# GraphSAGE 数据目录

- `raw/`：PPI、Reddit 官方 ZIP 和解压后的完整数据，仅本地保存，Git 忽略。
- `example/`：来自官方 GraphSAGE 仓库固定 commit `a0fdef95dca7b456dab01cb35034717c8b6dd017` 的 `example_data`。上游代码为 MIT License；每个文件的 SHA256 记录在 `manifests/graphsage.yaml`。

官方示例包含 3 个训练图、1 个验证图和 1 个测试图，用于验证数据解析器和 GraphSAGE 输入格式。它不是完整 PPI 数据集。
