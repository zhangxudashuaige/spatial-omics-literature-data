# 数据字典

## 图像数据字段

| 字段 | 说明 |
|------|------|
| image_shape | 图像形状，如 (T, C, Z, Y, X) 或 (T, Y, X, C) |
| axis_order | 轴顺序，如 TZYXC 或 TCZYX |
| channel_names | 通道名称，如 DAPI, GFP, mCherry, phase |
| pixel_size_um | 像素尺寸（微米） |
| time_interval_s | 时间间隔（秒） |
| z_interval_um | Z层间隔（微米） |
| dtype | 数据类型，如 uint16, float32 |
| microscope | 显微镜信息 |
| cell_line | 细胞系 |
| treatment | 处理条件 |
| virus_type | 病毒类型（登革/Zika，不得混合） |
| field_of_view | 视野编号 |

## 分割与追踪字段

| 字段 | 说明 |
|------|------|
| segmentation_mask | 分割掩膜（每个细胞一个标签值） |
| bounding_box | 边界框 (x, y, w, h) |
| centroid | 细胞中心位置 (x, y, z) |
| track_id | 轨迹唯一标识 |
| frame | 帧号 |
| parent_id | 父轨迹ID（分裂关系） |
| division_label | 分裂标签 |
| infection_label | 感染标签 |

## 标签来源区分

| 标签类型 | 说明 |
|----------|------|
| manual | 人工标注 |
| model_prediction | 模型预测 |
| pseudo_label | 伪标签 |

必须分开记录，不得混淆。

## 数据类别区分

| 类别 | 说明 |
|------|------|
| raw_image | 原始图像 |
| processed_image | 处理后图像 |
| segmentation | 分割掩膜 |
| tracking | 追踪结果 |
| labels | 标签文件 |
| example | 示例数据（小样本） |
| demo | 演示数据/视频 |
| full_training | 完整训练数据 |
| model_weights | 模型权重 |

不能因为下载了示例包，就报告已获得论文全部数据。
