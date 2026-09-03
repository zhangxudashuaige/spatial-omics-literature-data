# Human DLPFC 10x Visium

- 三名供体、12张切片；原始研究 DOI `10.1038/s41593-020-00787-0`。
- `spatialLIBD::fetch_data(type="spe")` 从ExperimentHub取得处理后的SpatialExperiment：33,538 genes × 47,681 spots，含counts/logcounts、array/pixel坐标、样本和人工层级。
- 官方SpaGCN教程使用切片151673。表达、坐标与图像必须按barcode连接；人工layer只用于评价。
