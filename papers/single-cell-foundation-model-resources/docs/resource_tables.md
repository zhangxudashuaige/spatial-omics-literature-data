# 自动生成的资源表

> 请勿手工编辑；运行 `python scripts/generate_markdown_tables.py` 重新生成。

## 预训练语料

| model | corpus_name | survey_reported_size | access_type | official_url |
|---|---|---|---|---|
| scBERT | PanglaoDB corpus | 约1M cells | direct/partial | https://panglaodb.se/ |
| UCE | IMA | 36M cells | partial | https://github.com/snap-stanford/UCE |
| GeneFormer | Genecorpus-30M | 27.4M cells | direct | https://huggingface.co/datasets/ctheodoris/Genecorpus-30M |
| CellPLM | CellPLM pretraining corpus | 9M scRNA-seq + 2M spatial cells | not publicly located | https://github.com/OmicsML/CellPLM |
| scFoundation | scFoundation pretraining collection | >50M cells | partial | https://github.com/biomap-research/scFoundation |
| Nicheformer | SpatialCorpus-110M | 综述约57M cells | partial | https://github.com/theislab/nicheformer |
| tGPT | tGPT transcriptome corpus | 22.3M cells | partial | https://github.com/deeplearningplus/tGPT |
| scGPT | CELLxGENE pretraining corpus | 33M cells | reconstructable | https://github.com/bowang-lab/scGPT |
| CellLM | PanglaoDB + CancerSCEM | 约2M cells | not publicly located | https://arxiv.org/abs/2306.04371 |
| LangCell | scLibrary | 27.5M cell-text pairs | direct | https://huggingface.co/datasets/Toycat/scLibrary |
| scCello | CELLxGENE pretraining set | 22M cells | direct | https://github.com/DeepGraphLearning/scCello |
| scPRINT | CELLxGENE pretraining corpus | 50M cells | partial | https://github.com/cantinilab/scPRINT |
| scMulan | hECA-10M | 10M cells | direct | https://zenodo.org/records/14209942 |
| GeneCompass | scCompass-126M | 126M cells | partial | https://github.com/xCompass-AI/GeneCompass |
| CellFM | CellFM 100M corpus | 约100M cells | partial/direct derived resources | https://github.com/biomed-AI/CellFM |

## 下游数据

| dataset_id | dataset_name | dataset_category | accession | original_paper_url |
|---|---|---|---|---|
| DS001 | Zheng68K | cell_annotation_and_clustering | SRP073767 | https://doi.org/10.1038/ncomms14049 |
| DS002 | PBMC 5K | cell_annotation_and_clustering |  |  |
| DS003 | PBMC 10K | cell_annotation_and_clustering; multiomics |  |  |
| DS004 | Baron pancreas | cell_annotation_and_clustering | GSE84133 | https://doi.org/10.1016/j.cels.2016.08.011 |
| DS005 | Muraro pancreas | cell_annotation_and_clustering | GSE85241 | https://doi.org/10.1016/j.cels.2016.09.002 |
| DS006 | Segerstolpe pancreas | cell_annotation_and_clustering | E-MTAB-5061 | https://doi.org/10.1016/j.cmet.2016.08.020 |
| DS007 | MacParland liver | cell_annotation_and_clustering | GSE115469 | https://doi.org/10.1038/s41467-018-06318-7 |
| DS008 | Multiple Sclerosis | cell_annotation_and_clustering; atlas_and_disease | GSE118257 | https://doi.org/10.1038/s41586-019-1404-z |
| DS009 | Human Cell Atlas | cell_annotation_and_clustering; atlas_and_disease | platform collection | https://doi.org/10.7554/eLife.27041 |
| DS010 | Human Cell Landscape | cell_annotation_and_clustering; atlas_and_disease | HRA000027; GSE134355 | https://doi.org/10.1038/s41586-020-2157-4 |
| DS011 | Tabula Sapiens | cell_annotation_and_clustering; atlas_and_disease | Tabula Sapiens portal collection | https://doi.org/10.1126/science.abl4896 |
| DS012 | Tabula Muris | cell_annotation_and_clustering; atlas_and_disease | figshare collection 5829687 | https://doi.org/10.1038/s41586-018-0590-4 |
| DS013 | Heart Atlas | cell_annotation_and_clustering | HCA heart project | https://doi.org/10.1038/s41586-020-2797-4 |
| DS014 | Lung Atlas | cell_annotation_and_clustering | HLCA collection | https://doi.org/10.1038/s41591-023-02327-2 |
| DS015 | Adamson Perturb-seq | gene_perturbation | GSE90546 | https://doi.org/10.1016/j.cell.2016.11.048 |
| DS016 | Norman Perturb-seq | gene_perturbation | GSE133344 | https://doi.org/10.1126/science.aax4438 |
| DS017 | Replogle Perturb-seq | gene_perturbation | GSE194122 | https://doi.org/10.1016/j.cell.2022.05.013 |
| DS018 | Dixit Perturb-seq | gene_perturbation | GSE90063 | https://doi.org/10.1016/j.cell.2016.11.038 |
| DS019 | Srivatsan chemical perturbation | gene_perturbation; drug_response | GSE142784 | https://doi.org/10.1126/science.aax6234 |
| DS020 | MERFISH mouse brain | spatial_transcriptomics | Allen Brain Cell Atlas | https://doi.org/10.1038/s41586-023-06812-z |
| DS021 | CosMx human liver | spatial_transcriptomics | NanoString public dataset | https://doi.org/10.1038/s41587-021-01006-2 |
| DS022 | CosMx human lung | spatial_transcriptomics | NanoString public dataset | https://doi.org/10.1038/s41587-021-01006-2 |
| DS023 | Xenium human lung | spatial_transcriptomics | 10x Genomics public dataset |  |
| DS024 | Xenium human colon | spatial_transcriptomics | 10x Genomics public dataset |  |
| DS025 | MERSCOPE FFPE immuno-oncology | spatial_transcriptomics | Vizgen public dataset |  |
| DS026 | CITE-seq | multiomics | GSE100866 | https://doi.org/10.1038/nmeth.4380 |
| DS027 | CyTOF | multiomics | not uniquely specified by survey | https://doi.org/10.1038/nprot.2012.026 |
| DS028 | 10x Multiome PBMC | multiomics | 10x Genomics public dataset |  |
| DS029 | BMMC | multiomics | NeurIPS 2021 Open Problems collection | https://openproblems.bio/about/ |
| DS030 | ASAP PBMC | multiomics | GSE156478 | https://doi.org/10.1038/s41587-021-00927-2 |
| DS031 | Human lung cancer drug-response | drug_response | GSE149383 | https://doi.org/10.1038/s41467-021-21884-z |
| DS032 | Oral squamous cancer drug-response | drug_response | GSE117872 | https://doi.org/10.1038/s41467-018-07261-3 |
| DS033 | CDR / DeepCDR benchmark | drug_response | CCLE + GDSC derived | https://doi.org/10.1093/bioinformatics/btaa822 |
| DS034 | SCAD drug-response collection | drug_response | GDSC; GSE149215; GSE108383; SCP542 | https://doi.org/10.1002/advs.202204113 |
| DS035 | TCGA | atlas_and_disease | TCGA program | https://doi.org/10.1038/ng.2764 |
| DS036 | GTEx | atlas_and_disease | dbGaP phs000424 | https://doi.org/10.1126/science.aaz1776 |
| DS037 | COVID-19 integration benchmark | atlas_and_disease | composite benchmark | https://doi.org/10.1038/s41587-021-01001-7 |
| DS038 | PanglaoDB downstream collection | cell_annotation_and_clustering; atlas_and_disease | PanglaoDB | https://doi.org/10.1093/database/baz046 |

## 数据平台

| platform_name | main_use | official_url | requires_account |
|---|---|---|---|
| CELLxGENE Discover | 浏览、筛选和下载标准化单细胞数据 | https://cellxgene.cziscience.com/ | no for most public data |
| NCBI GEO | 通过GSE/GSM检索表达数据 | https://www.ncbi.nlm.nih.gov/geo/ | no |
| Human Cell Atlas | 发现HCA项目、元数据和矩阵 | https://data.humancellatlas.org/ | sometimes |
| Broad Single Cell Portal | 按研究浏览和下载处理后数据 | https://singlecell.broadinstitute.org/single_cell | sometimes |
| EMBL-EBI Single Cell Expression Atlas | 浏览表达、marker并下载标准化结果 | https://www.ebi.ac.uk/gxa/sc/home | no |
| PanglaoDB | marker查询、细胞类型与SRA研究筛选 | https://panglaodb.se/ | no |
| ENA | 下载FASTQ、CRAM、元数据 | https://www.ebi.ac.uk/ena/browser/home | no for open data |
| GSA | 通过CRA/CRR等编号获取原始数据 | https://ngdc.cncb.ac.cn/gsa/ | sometimes |
| ImmPort | 获取免疫学研究数据和元数据 | https://www.immport.org/ | yes for downloads |

## 模型仓库

| model_name | model_category | repository_type | official_repository | paper_url |
|---|---|---|---|---|
| scBERT | PLM | official | https://github.com/TencentAILabHealthcare/scBERT | https://doi.org/10.1038/s42256-022-00534-z |
| UCE | PLM | official | https://github.com/snap-stanford/UCE | https://doi.org/10.1101/2023.11.28.568918 |
| GeneFormer | PLM | official | https://huggingface.co/ctheodoris/Geneformer | https://doi.org/10.1038/s41586-023-06139-9 |
| CellPLM | PLM | official | https://github.com/OmicsML/CellPLM | https://doi.org/10.1101/2023.10.03.560734 |
| scFoundation | PLM | official | https://github.com/biomap-research/scFoundation | https://doi.org/10.1038/s41592-024-02305-7 |
| Nicheformer | PLM | official | https://github.com/theislab/nicheformer | https://doi.org/10.1101/2024.04.15.589472 |
| tGPT | PLM | official | https://github.com/deeplearningplus/tGPT | https://doi.org/10.1016/j.isci.2023.106536 |
| scGPT | PLM | official | https://github.com/bowang-lab/scGPT | https://doi.org/10.1038/s41592-024-02201-0 |
| CellLM | PLM | unverified |  | https://arxiv.org/abs/2306.04371 |
| LangCell | PLM | official | https://github.com/PharMolix/LangCell | https://arxiv.org/abs/2405.06708 |
| scCello | PLM | official | https://github.com/DeepGraphLearning/scCello | https://proceedings.neurips.cc/paper_files/paper/2024/hash/0be40478ab6ee0006ee3b38b158bbc8f-Abstract-Conference.html |
| scPRINT | PLM | official | https://github.com/cantinilab/scPRINT | https://doi.org/10.1038/s41467-025-58699-1 |
| scMulan | PLM | official | https://github.com/SuperBianC/scMulan | https://doi.org/10.1007/978-1-0716-3989-4_57 |
| GeneCompass | PLM | official | https://github.com/xCompass-AI/GeneCompass | https://doi.org/10.1038/s41422-024-01034-y |
| CellFM | PLM | official | https://github.com/biomed-AI/CellFM | https://doi.org/10.1038/s41467-025-59926-5 |
| Cell2Sentence | LLM_or_agent | official | https://github.com/vandijklab/cell2sentence | https://openreview.net/forum?id=f9jzZUn6dM |
| ChatCell | LLM_or_agent | official | https://github.com/zjunlp/ChatCell | https://arxiv.org/abs/2402.08303 |
| GenePT | LLM_or_agent | official | https://github.com/yiqunchen/GenePT | https://doi.org/10.1101/2023.10.16.562533 |
| scELMo | LLM_or_agent | official | https://github.com/HelloWorldLTY/scELMo | https://doi.org/10.1016/j.patter.2025.101431 |
| scInterpreter | LLM_or_agent | unverified |  | https://arxiv.org/abs/2402.12405 |
| CELLama | LLM_or_agent | official | https://github.com/portrai-io/CELLama | https://doi.org/10.1101/2024.05.08.593094 |
| scChat | LLM_or_agent | official | https://github.com/li-group/scChat | https://doi.org/10.1002/aic.18593 |
