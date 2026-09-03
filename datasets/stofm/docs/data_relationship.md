# 数据关系

```text
多技术空间转录组切片（SToCorpus-88M）
  ├─ 表达矩阵与细胞/spot元数据
  ├─ 二维空间坐标
  └─ 人基因词表；小鼠基因先映射为人同源基因
          ↓ preprocessing/preprocess.py
      data.h5ad + hf.dataset
          ↓ cell encoder
        ce_emb.npy
          ↓ 构建多尺度sub-slice并输入SE(2)-Transformer
       stofm_emb.npy（每细胞256维）
          ↓ 任务头
  区域分割 / 注释 / 零样本聚类 / 解卷积 / 基因补全
```

SToCorpus-88M 是预训练语料；六个下游入口是评测资源；Google Drive 中的 demo 是程序演示；两个 checkpoint 是模型参数。它们不能混写成同一种“数据”。
