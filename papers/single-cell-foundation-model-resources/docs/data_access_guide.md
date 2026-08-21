# 数据访问指南

## 推荐顺序

1. 在 `metadata/downstream_datasets.csv` 找到 `dataset_id`、accession 和 `official_url`。
2. 阅读 `license`、`access_type` 和 `notes`。
3. 打开原始论文确认样本、物种、版本和实验设计。
4. 先下载处理后矩阵和元数据，确认任务能复现后再考虑FASTQ等原始数据。
5. 下载到 `data/external/<dataset_id>/`，记录来源日期和校验值。

## 常见平台

- GEO：GSE页提供补充矩阵；原始reads通常链接到SRA。
- CELLxGENE：下载标准化H5AD或用Census API按条件查询。
- 10x Genomics：页面常提供矩阵、BAM、FASTQ或仪器输出包；同名PBMC数据有多个化学版本。
- HCA：许可与下载方式按项目不同。
- ImmPort：通常要注册。
- GSA-Human、dbGaP、GDC controlled tier：必须申请，不能把受控的人类个体级数据上传GitHub。

## 访问状态含义

- `direct`：官方页面可直接获得至少一种可用文件。
- `partial`：只公开子集、处理脚本、来源清单或部分文件。
- `mixed`：开放和受控内容并存。
- `registration may be required`：需要账号或点击接受条款。
- `not publicly located`：未找到完整公开下载入口，不代表数据一定不存在。
- `not uniquely located`：综述未给足信息，不能确定唯一数据集。

## 为什么不提供一个“下载全部”按钮

这些资源跨多个数据库和许可体系，总体数据量可能达到数十TB。自动批量下载可能违反平台条款、造成重复数据和巨额存储浪费。项目只提供结构化入口与检查脚本；用户应根据研究问题按需下载。
