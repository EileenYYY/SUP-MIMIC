# Stats and ML Workflow

This workflow covers descriptive analysis, model comparison, longitudinal summaries, and classical ML baselines.

## Inputs

- `case_profile.json`
- `case_profile.jsonl`
- `feature_table.csv`

## Statistics

The statistics layer reports:

- missingness
- descriptive summaries
- group comparisons
- time-window aggregations
- consistency checks

## Classical ML

The ML layer runs:

1. label preparation
2. feature table construction
3. train/validation/test splitting
4. baseline training
5. metric reporting
6. artifact export

## Baselines

- logistic regression
- random forest
- gradient boosting
- Cox model
- Lasso / Ridge

## Metrics

- AUC
- accuracy
- F1
- precision
- recall
- calibration
- Brier score

## Public Release

Public release contains code, configuration templates, synthetic examples, aggregate tables, and aggregate figures. It does not contain patient-level outputs.
