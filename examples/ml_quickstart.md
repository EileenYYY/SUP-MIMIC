# ML Quickstart

使用 synthetic 数据跑一个完整机器学习闭环：

```bash
mimic-pipeline build-features --input examples/synthetic_profiles.jsonl --output outputs/features/synthetic.csv
mimic-pipeline stats-summary --input outputs/features/synthetic.csv --output outputs/reports/synthetic_summary.json
mimic-pipeline train-model --input outputs/features/synthetic.csv --model-output outputs/models/synthetic_baseline.pkl --metrics-output outputs/models/synthetic_metrics.json --test-size 0.5
mimic-pipeline evaluate-model --input outputs/features/synthetic.csv --model outputs/models/synthetic_baseline.pkl --output outputs/models/synthetic_eval.json
```

这个例子只用于验证流程，不代表真实医学模型。

