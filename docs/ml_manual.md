# Machine Learning Manual

这份手册对应 PDF 里的“机器学习建模、特征筛选、模型训练、最终模型、模型测试、论文产出”。

## 1. 准备标签

机器学习任务必须先定义标签。

常见标签：

- 院内死亡
- ICU 内死亡
- 28 天死亡
- 30 天死亡
- 是否发生 AKI
- 是否发生脓毒症
- 是否再入院

建议把标签保存为：

```text
__label__
```

## 2. 准备特征

输入可以是：

- `case_profile.json`
- `case_profile.jsonl`
- 已经整理好的 CSV

生成特征表：

```bash
mimic-pipeline build-features --input outputs/cases/case_profile.jsonl --output outputs/features.csv
```

## 3. 特征筛选

推荐顺序：

1. 删除缺失率极高的变量
2. 删除近零方差变量
3. 删除泄露变量
4. 做临床合理性检查
5. 再做 Lasso / Boruta / tree importance 等模型筛选

不要把结局发生之后的数据放进预测特征。

## 4. 训练 baseline

```bash
mimic-pipeline train-model --input outputs/features.csv --model-output outputs/models/baseline.pkl --metrics-output outputs/models/baseline_metrics.json
```

默认训练 logistic regression baseline。

## 5. 评估模型

```bash
mimic-pipeline evaluate-model --input outputs/features.csv --model outputs/models/baseline.pkl --output outputs/models/eval.json
```

默认输出：

- accuracy
- precision
- recall
- F1
- ROC AUC

## 6. 推荐扩展模型

可以继续扩展：

- random forest
- gradient boosting
- XGBoost / LightGBM
- survival model
- deep learning model

## 7. 论文产出建议

建议保存：

- cohort flow
- baseline table
- feature list
- model parameters
- internal validation metrics
- calibration plot
- ROC / PR curve
- decision curve analysis

## 8. 开源边界

可以公开：

- 特征工程代码
- 模型训练代码
- 模型评估代码
- synthetic demo
- 不含真实患者数据的配置文件

不要公开：

- 原始 MIMIC 数据
- 由原始患者数据直接导出的受限表
- 未授权的真实模型权重

