# Stats and ML Workflow

这部分对应你 PDF 里的：

- 探索性分析
- 经典统计方法
- 一致性与模型比较
- 纵向与重复测量
- 因果推断
- 机器学习建模

## 1. 输入

输入建议统一为以下任意一种：

- `case_profile.json`
- `case_profile.jsonl`
- `feature_table.csv`

## 2. 统计分析

建议先做：

- 缺失率
- 描述统计
- 分组比较
- 时间窗汇总
- 共线性检查

## 3. 机器学习

标准流程：

1. 构建标签
2. 提取特征
3. 划分训练/验证/测试
4. 训练 baseline
5. 比较多个模型
6. 评估 calibration 和 discrimination
7. 保存模型与指标

## 4. 推荐基线模型

- logistic regression
- random forest
- gradient boosting
- Cox 模型
- Lasso / Ridge

## 5. 推荐评估指标

- AUC
- accuracy
- F1
- precision / recall
- calibration
- Brier score

## 6. 推荐发布内容

- 训练脚本
- 推理脚本
- 指标脚本
- 配置样例
- 结果导出模板

