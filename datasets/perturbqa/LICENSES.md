# 许可证说明 (LICENSES.md)

本项目包含多个来源的数据和代码，各部分适用不同的许可证。

## 官方代码

**PerturbQA 官方代码** (https://github.com/genentech/PerturbQA)

- 许可证: **Genentech Non-Commercial Software License 1.0**
- 适用范围: 官方仓库中的源代码
- 限制: 仅限非商业用途
- 完整许可证文本: 请参阅官方仓库中的 LICENSE 文件

## PerturbQA 数据和模型输出

**PerturbQA 加工后的基准数据、模型输出和评价结果**

- 来源: Zenodo (https://doi.org/10.5281/zenodo.14915312)
- 许可证: **CC BY 4.0** (Creative Commons Attribution 4.0 International)
- 适用范围:
  - benchmark 数据 (DE, direction, GSE)
  - Summer 模型输出
  - 消融模型输出 (llm-nocot, llm-noretrieve)
  - 最终评价结果
- 要求: 注明出处

## CORUM 数据

**CORUM (Comprehensive Resource of Mammalian protein complexes)**

- 来源: 知识图谱数据中包含的 CORUM 部分
- 许可证: **CC BY-NC 4.0** (Creative Commons Attribution-NonCommercial 4.0)
- 限制: 非商业用途
- 官网: https://mips.helmholtz-muenchen.de/corum/

## 其他知识图谱数据

知识图谱中可能包含的其他数据库:

| 数据库 | 许可证 | 来源 |
|--------|--------|------|
| Gene Ontology | BSD-3 | https://geneontology.org/ |
| Reactome | CC BY 4.0 | https://reactome.org/ |
| KEGG | 学术使用需注册 | https://www.kegg.jp/ |
| DisGeNET | CC BY-NC-SA 4.0 | https://www.disgenet.org/ |
| STRING | CC BY 4.0 | https://string-db.org/ |

**注意**: 知识图谱中各数据库的具体组成以实际数据文件为准。使用时请保留各来源的许可证声明。

## 基因自然语言摘要

**基因功能摘要 (gene_summary.zip)**

- 来源: Zenodo
- 许可证: **CC BY 4.0** (随 PerturbQA 数据)
- 注意: 摘要内容可能整合自多个来源，使用时请注明原始来源

## 本项目代码

本仓库中的下载脚本、检查脚本和 notebook:

- 许可证: **MIT License**
- 仅限数据查看和下载功能，不包含 PerturbQA 模型代码

## 使用建议

1. 学术研究使用: 大部分数据可自由使用，注明出处即可
2. 商业使用: 需注意 CORUM (CC BY-NC) 和官方代码 (Non-Commercial) 的限制
3. 重新分发: 保留各部分的许可证声明和出处信息
4. 不确定时: 以各数据原始来源的许可证为准
