# 数据来源审计

检查日期：2026-08-18（UTC）

## 原论文声明

论文 `DATA AVAILABILITY` 段落说明：空间胚胎转录组已存入 CNSA，编号 `CNP0005981`，但预印本发表时尚未公开；处理后数据上传至 `https://db.cngb.org/stomics/mosta/3d/`。

论文方法和图 1 还说明：

- E9.5 为 94 张连续 Stereo-seq 切片；E11.5 为 91 张间隔 Stereo-seq 切片。
- 每次切片前拍摄 SBFI；测序切片使用 ssDNA，E11.5 相邻未测序切片使用 H&E。
- 最终细胞质心三维坐标保存在逐切片 H5AD 中。

## CNP0005981 当前状态

入口：https://db.cngb.org/data_resources/project/CNP0005981/

CNGB 网页使用的公共 API 在检查日返回：

```text
GET https://db.cngb.org/cnsa/ajax/project/public_view/?q=CNP0005981
HTTP 200
{"code":2,"error":{"code":2003,"content":"attributes does not exist"}}
```

同一接口对已公开的 `CNP0001543` 能返回 `code=0`、`select_control=Public` 和 FTP 清单，因此本仓库把 `CNP0005981` 标记为 `not_publicly_retrievable`。这只表示当前公共接口不能取得项目和文件，不推断项目已被删除。

## MOSTA3D 当前状态

论文给出的 `https://db.cngb.org/stomics/mosta/3d/` 返回 HTTP 404。

STOmicsDB 当前的旧版 MOSTA 下载页对应 Chen 等 2022 年研究和 `CNP0001543`。其 E9.5/E11.5 H5AD 不能替代本论文 `CNP0005981` 的 94/91 张切片数据。

## 外部 scRNA-seq 参考

论文使用 Qiu 等覆盖 E9-E12 的小鼠胚胎单细胞图谱做细胞类型标签转移：

- DOI：https://doi.org/10.1038/s41586-024-07069-w
- GEO：https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE228590

本仓库只保存 E9-E12 子集规则、标签映射和 marker 表，不复制完整表达矩阵。

## 尚无法确认

- 每张切片真实文件名、大小和 SHA-256/MD5。
- SBFI 的完整图像数、分辨率、格式与切片对应表。
- 是否单独发布细胞边界、分割掩膜、仿射矩阵、形变场和 mesh。
- H5AD 内 `obs`、`var`、`obsm`、`layers` 的真实键名。
- 数据许可是否允许公共镜像和二次分发。
