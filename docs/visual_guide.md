# SUP-MIMIC 图解说明

本页汇总仓库中用于 GitHub 展示的核心图像。

![总流程图](assets/01-overall-workflow.svg)

图 1 展示授权环境、SQL 提取、特征处理、SUP-MIMIC 构建、本地或受控 API 评估，以及公开发布边界。

![开源边界图](assets/02-open-source-boundary.svg)

图 2 区分可公开材料与受限材料。公开的是方法、代码、模板、合成样例和聚合结果。受限的是原始 MIMIC 数据、患者级输出、密钥和内部审计材料。

![构建逻辑图](assets/03-benchmark-construction.svg)

图 3 说明 BA、DDT、DCT 的构建逻辑：

- BA：单病例基础诊断验证
- DDT：标签不同、特征相近的病例对
- DCT：标签相同、特征差异大的病例对

对应的详细文档位于：

- [docs/tutorial.md](tutorial.md)
- [docs/reproducibility_workflow.md](reproducibility_workflow.md)
- [docs/compliance.md](compliance.md)
- [docs/data_availability_statement.md](data_availability_statement.md)
