# 数据字典

这是目标字段契约；真实键名必须在来源公开后映射，不能预先假设。

## 样本和切片

| 字段 | 含义 |
| --- | --- |
| `stage` | `E9.5` 或 `E11.5` |
| `embryo_id` | 胚胎唯一编号 |
| `section_id` | 切片唯一编号 |
| `section_order` | 从第一张开始的切片顺序 |
| `section_thickness_um` | 切片厚度，当前未知 |
| `stereo_seq` | 是否进行 Stereo-seq |
| `has_sbfi`、`has_ssdna`、`has_he` | 是否有对应图像 |
| `qc_status`、`qc_notes` | 质量控制结果和说明 |

## 单细胞和坐标

| 字段 | 含义 |
| --- | --- |
| `cell_id` | 全项目唯一细胞编号 |
| `section_id` | 所属切片 |
| `x_2d`、`y_2d` | 切片内二维坐标 |
| `x_3d`、`y_3d`、`z_3d` | 配准后的三维坐标 |
| `boundary_ref` | 边界或掩膜文件引用 |
| `cluster_id`、`cell_type` | 聚类和正式细胞类型 |
| `annotation_confidence` | 来源提供时记录注释置信度 |
| `reference_cell_type` | scRNA-seq 参考标签 |

## 器官和空间域

最小字段：`cell_id`、`section_id`、`organ`、`spatial_domain`、`subdomain`。E9.5 应能映射到论文报告的 14 个器官/区域，E11.5 应能映射到 23 个。

## 表达矩阵

GEM 最低字段为 `geneID`、`x`、`y`、`MIDCounts`；来源提供时保留 `ExonCount` 和 `IntronCount`。GEF 是 SAW 产生的二进制表达容器。H5AD 应把 `obs` 细胞、`var` 基因、`X/layers` 表达与 `obsm` 坐标关联起来。

## 配准和三维重建

最小字段：`source_image`、`target_image`、`rotation_deg`、`translation_x/y`、`scale_x/y`、`affine_matrix_ref`、`deformation_field_ref` 和 `z_position_um`。

## Mesh 与统计

作者提供时记录 `mesh_id`、`stage`、`organ`、`mesh_path`、`outline_path`、`volume_um3`、`cell_count`、`cell_density_per_um3` 和生成参数。
