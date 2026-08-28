# SUP-MIMIC 图解指南

这组图把整个开源与复现过程拆成四个视角：

![总流程图](assets/01-overall-workflow.svg)

图 1 展示从 PhysioNet 授权、本地 MIMIC 数据库、SQL 提取、特征处理、BA/DDT/DCT 构建，到本地模型或合规 API 评估，最后只发布代码和聚合结果的完整路径。

![开源边界图](assets/02-open-source-boundary.svg)

图 2 用左右两栏区分“可以公开”和“不要公开”。最重要的判断是：去掉姓名并不等于可以公开；密集的患者级临床特征、prompt、模型回答和错误归因仍可能属于受限派生材料。

![构建逻辑图](assets/03-benchmark-construction.svg)

图 3 解释 SUP-MIMIC 的三个任务：

- BA：从阳性样本中抽取基础评估实例。
- DDT：寻找标签不同但结构化特征相近的样本对。
- DCT：寻找标签相同但结构化特征差异大的样本对。

![发布闸门图](assets/04-release-gates.svg)

图 4 是发布前检查顺序。代码测试、数据隔离、密钥清理、图表复核、LLM 数据治理和 arXiv 编译都通过后，再推送公开仓库或上传论文。

## 建议阅读顺序

1. 先看图 1，理解全流程。
2. 再看图 2，确认哪些材料绝不能上传。
3. 看图 3，理解 BA/DDT/DCT 的样本构建。
4. 最后按图 4 执行发布前检查。

对应的详细文字文档：

- [compliance.md](compliance.md)
- [reproducibility_workflow.md](reproducibility_workflow.md)
- [llm_evaluation.md](llm_evaluation.md)
- [data_availability_statement.md](data_availability_statement.md)
- [arXiv README](../arxiv/README.md)
