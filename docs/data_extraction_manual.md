# Data Extraction Manual

这份手册对应 PDF 里的“人群、诊断、手术、通用指标、检验、生命体征、住院用药、ICU 出入量、ICU 治疗单、复合指标库”。

## 1. 人群筛选

建议把 cohort 筛选分成三层：

1. 基础人群：年龄、性别、住院或 ICU 患者
2. 诊断和手术排纳：ICD-9 / ICD-10 纳入、合并、排除
3. 时间与结局：住院时长、ICU 时长、死亡、再入院

对应文件：

- `sql/hospital/00_cohort_candidates.sql`
- `sql/hospital/10_patients.sql`
- `sql/hospital/11_admissions.sql`

## 2. 诊断和手术

诊断建议输出：

- `subject_id`
- `hadm_id`
- `seq_num`
- `icd_code`
- `icd_version`
- `long_title`

手术建议输出：

- `subject_id`
- `hadm_id`
- `seq_num`
- `chartdate`
- `icd_code`
- `long_title`

对应文件：

- `sql/hospital/13_diagnoses.sql`
- `sql/hospital/14_procedures.sql`

## 3. 通用指标和预后

建议先实现这些稳定结局：

- 住院天数
- ICU 停留时间
- 院内死亡
- ICU 内死亡
- 28 / 30 / 90 / 365 天死亡
- 距上次出院小时数
- 到下次入院小时数

这些指标可以在 SQL 层产出，也可以在 Python 层根据 `admissions` 和 `icustays` 计算。

## 4. 检验与生命体征

建议分两类：

- 首日汇总：优先使用 `mimiciv_derived.first_day_lab` 和 `mimiciv_derived.first_day_vitalsign`
- 任意时间窗：使用 `labevents` 或 `chartevents` 自己按时间窗聚合

常用聚合：

- first
- last
- mean
- min
- max
- median

对应文件：

- `sql/icu/21_first_day_vitals.sql`
- `sql/icu/22_first_day_labs.sql`
- `sql/icu/26_chartevents.sql`

## 5. 住院用药

建议先按 admission 提取处方：

- `drug`
- `dose_val_rx`
- `dose_unit_rx`
- `route`
- `starttime`
- `stoptime`

对应文件：

- `sql/hospital/15_prescriptions.sql`

如果要做抗生素、降压药、胰岛素等药物族，建议另建映射表，不要把药名判断散在代码里。

## 6. ICU 出入量

对应 MIMIC-IV ICU 表：

- `inputevents`
- `outputevents`

推荐聚合：

- 总入量
- 总出量
- 首日入量
- 首日出量
- 净液体平衡
- VIS 相关用药可在 inputevents 中按 itemid / label 映射

对应文件：

- `sql/icu/23_inputevents.sql`
- `sql/icu/24_outputevents.sql`

## 7. ICU 治疗单

对应 MIMIC-IV ICU 表：

- `procedureevents`
- `chartevents`

常见指标：

- 机械通气
- HFNC
- CRRT
- RRT
- 心律
- CAM-ICU 谵妄

对应文件：

- `sql/icu/25_procedureevents.sql`
- `sql/icu/26_chartevents.sql`

## 8. 复合指标库

复合指标建议单独维护，不要和原始数据提取混在一起。

常见复合指标：

- SOFA
- qSOFA
- SAPS II
- OASIS
- shock index
- eGFR
- MAP
- anion gap

对应文件：

- `sql/icu/27_score_extracts.sql`

## 9. 推荐工作流

```bash
mimic-pipeline validate-config --config configs/full_example_config.yaml
mimic-pipeline run --config configs/full_example_config.yaml --subject-id YOUR_SUBJECT_ID --hadm-id YOUR_HADM_ID --stay-id YOUR_STAY_ID
mimic-pipeline build-case --config configs/full_example_config.yaml --input-dir outputs/raw --output outputs/cases/case_profile.json
mimic-pipeline screen --config configs/full_example_config.yaml --input outputs/cases/case_profile.json --output outputs/cases/screened.json
```
