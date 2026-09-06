# Nader et al.（2024）scTherapy

论文：**Single-Cell Transcriptomes Identify Patient-Tailored Therapies for Selective Co-Inhibition of Cancer Clones**。

- 论文：<https://www.nature.com/articles/s41467-024-52980-5>
- 作者代码：<https://github.com/kris-nader/scTherapy>
- Zenodo 代码：<https://doi.org/10.5281/zenodo.13340796>
- Docker：<https://hub.docker.com/r/kmnader/sctherapy>
- 本仓库数据模块：[`datasets/sctherapy/`](../../datasets/sctherapy/)

scTherapy 是一个利用单细胞转录组数据识别患者定制癌症治疗方案的计算框架。它通过整合药物诱导表达数据（LINCS）、药物剂量-响应数据（PharmacoDB）和药物结构数据（PubChem），训练 LightGBM 模型预测药物组合对特定癌症克隆的协同抑制效果。

本条目保存 AML 和 HGSC 患者单细胞数据（SRA/EGA）、处理后 Seurat 对象（Zenodo）、模型训练数据库入口、下载脚本和检查工具。受控人类数据（EGA）仅记录 accession 和申请流程，不尝试下载或上传。
