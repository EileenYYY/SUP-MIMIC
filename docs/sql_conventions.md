# SQL Conventions

## 基本原则

1. 每个 SQL 文件只负责一个主题。
2. 使用参数化，不拼接原始字符串。
3. 输出字段名保持稳定。
4. 查询默认显式排序。
5. 能用明确列名就不要写 `SELECT *`。

## 命名建议

- `10_patients.sql`
- `11_admissions.sql`
- `20_icustays.sql`
- `21_first_day_vitals.sql`
- `22_first_day_labs.sql`
- `13_diagnoses.sql`
- `14_procedures.sql`
- `15_prescriptions.sql`

## 参数约定

本项目示例采用 Python DB-API 风格参数：

```sql
where subject_id = %(subject_id)s
```

或者：

```sql
where hadm_id = %(hadm_id)s
```

## 推荐输出字段

- `subject_id`
- `hadm_id`
- `stay_id`
- `seq_num`
- `item_code`
- `item_name`
- `value`
- `unit`
- `starttime`
- `charttime`

