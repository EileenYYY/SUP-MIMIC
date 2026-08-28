# Machine Learning Manual

This manual describes the classical ML layer around SUP-MIMIC.

## 1. Labels

The feature table stores the target in a label column such as `__label__`.

## 2. Feature Table

```bash
sup-mimic-pipeline build-features --input outputs/cases/case_profile.jsonl --output outputs/features.csv
```

The input can be `case_profile.json`, `case_profile.jsonl`, or a prepared CSV.

## 3. Training

```bash
sup-mimic-pipeline train-model --input outputs/features.csv --model-output outputs/models/baseline.pkl --metrics-output outputs/models/baseline_metrics.json
```

The trainer writes a serialized model and a metrics JSON.

## 4. Evaluation

```bash
sup-mimic-pipeline evaluate-model --input outputs/features.csv --model outputs/models/baseline.pkl --output outputs/models/eval.json
```

The evaluator writes accuracy-oriented metrics for the saved model.

## 5. Public Release Split

Public:

- feature engineering code
- model training code
- model evaluation code
- synthetic demo data

Private:

- raw MIMIC data
- patient-level derived outputs
- unreleased model weights from restricted data
