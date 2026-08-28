# MIMIC Modules

下面是这个仓库建议覆盖的 MIMIC-IV 模块。

## 1. Hospital

- `patients`
- `admissions`
- `transfers`
- `diagnoses_icd`
- `procedures_icd`
- `prescriptions`
- `omr`（如果环境里有）

## 2. ICU

- `icustays`
- `chartevents`
- `inputevents`
- `outputevents`
- `procedureevents`
- `derived.first_day_vitalsign`
- `derived.first_day_lab`

## 3. Emergency Department

- `edstays`
- `triage`
- `diagnosis`
- `medrecon`
- `vitalsign`
- `pyxis`

## 4. Radiology / CXR

- `mimic-cxr` 记录列表
- 放射图像索引
- 影像报告文本

## 5. ECG

- ECG record table
- machine measurement
- waveform note links

## 6. Notes

- discharge summary
- radiology note
- nursing note
- other narrative notes

## 7. What to open source

建议把每个模块拆成三类文件：

1. `sql/` 下的提取模板
2. `docs/` 下的数据字典
3. `src/` 下的标准化与导出代码

