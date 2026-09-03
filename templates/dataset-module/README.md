# 数据模块名称

## 论文与官方来源

- 论文：
- DOI：
- 数据入口：
- 代码与固定commit：

## 数据关系

说明原始数据、处理后矩阵、坐标、注释、参考数据、模型输入和模型输出之间的关系。

## 当前获取状态

明确区分 `not_started`、`metadata_only`、`partial`、`downloaded`、`verified`、`restricted` 和 `unresolved`。

## Windows PowerShell

```powershell
cd .\datasets\<dataset-id>
python .\scripts\download_data.py --help
python .\scripts\inspect_data.py --help
```

## 许可证与引用

记录数据许可证、使用限制和正确引用方式。链接有效不等于许可允许重新分发。

## 复现边界

说明当前公开资源可以复现什么、不能复现什么，以及缺少哪些精确输入。
