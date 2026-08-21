# 模型概览

## PLM

PLM类模型直接学习单细胞表达的“语言”。常见输入编码包括：

- 表达分箱：scBERT、CellLM。
- 基因排序：GeneFormer、tGPT。
- 基因token加表达值：scGPT。
- 表达加先验知识：GeneCompass。
- 表达加空间邻域：Nicheformer。
- 多任务生成：scMulan。

## LLM_or_agent

这一类不是简单把大规模表达矩阵送进BERT：

- Cell2Sentence、ChatCell、CELLama：把细胞表达转换成基因“句子”。
- GenePT、scELMo：利用通用LLM生成的基因/药物文本嵌入。
- scInterpreter：把表达基因和任务指令接入Llama。
- scChat：由LLM驱动的多代理分析系统，主要执行和解释分析流程。

## 官方代码核验

本次共记录22个模型。CellLM和scInterpreter只确认到论文，未确认官方代码仓库；其余20个有作者或机构官方仓库/模型页。具体许可必须查看每个仓库和权重页，代码许可不自动覆盖权重许可。
