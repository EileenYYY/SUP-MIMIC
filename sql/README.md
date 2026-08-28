# SQL

这里放的是面向 MIMIC-IV 的主题 SQL 模板。

## 组织方式

- `hospital/`：患者、住院、诊断、处方
- `icu/`：ICU 轨迹、首日生命体征、首日实验室
- `ed/`：急诊模块
- `cxr/`：胸片模块
- `ecg/`：心电图模块
- `note/`：可选的文本提取

## 写法要求

- 使用参数化占位符
- 明确列名
- 保持排序稳定
- 每个文件只做一件事

## 推荐扩展

如果你要继续加内容，优先补这些文件：

- `icu/26_chartevents.sql`
- `icu/27_score_extracts.sql`
- `ed/12_vitalsign.sql`
- `ed/13_medrecon.sql`
- `cxr/10_cxr_record_list.sql`
- `ecg/10_ecg_record_table.sql`
- `ecg/11_ecg_machine_measurement.sql`
