# SQL Conventions

## Principles

1. Each SQL file covers one topic.
2. Use parameterized placeholders.
3. Keep output field names stable.
4. Use explicit ordering when order matters.
5. Prefer explicit column lists over `SELECT *`.

## File Naming

- `10_patients.sql`
- `11_admissions.sql`
- `20_icustays.sql`
- `21_first_day_vitals.sql`
- `22_first_day_labs.sql`
- `13_diagnoses.sql`
- `14_procedures.sql`
- `15_prescriptions.sql`

## Parameters

The project uses Python DB-API style parameters:

```sql
where subject_id = %(subject_id)s
```

```sql
where hadm_id = %(hadm_id)s
```

## Common Output Fields

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
