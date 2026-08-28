# Data Extraction Manual

This manual matches the MIMIC extraction portion of the project.

## 1. Cohort Definition

The cohort is built from authorized MIMIC tables and starts with adult inpatient or ICU records.

Relevant files:

- `sql/hospital/00_cohort_candidates.sql`
- `sql/hospital/10_patients.sql`
- `sql/hospital/11_admissions.sql`

## 2. Diagnoses and Procedures

Outputs:

- `subject_id`
- `hadm_id`
- `seq_num`
- `icd_code`
- `icd_version`
- `long_title`

Files:

- `sql/hospital/13_diagnoses.sql`
- `sql/hospital/14_procedures.sql`

## 3. Outcomes

The pipeline records length of stay, ICU stay, mortality, and readmission-related fields from the authorized database.

## 4. Labs and Vitals

First-day labs and first-day vitals are extracted for ICU stays.

Files:

- `sql/icu/21_first_day_vitals.sql`
- `sql/icu/22_first_day_labs.sql`

## 5. Prescriptions

Prescription extraction records drug name, dose, route, start time, and stop time.

File:

- `sql/hospital/15_prescriptions.sql`

## 6. ICU Events

Files:

- `sql/icu/23_inputevents.sql`
- `sql/icu/24_outputevents.sql`
- `sql/icu/25_procedureevents.sql`
- `sql/icu/26_chartevents.sql`

## 7. Composite Scores

File:

- `sql/icu/27_score_extracts.sql`

## 8. Extraction Loop

```bash
sup-mimic-pipeline validate-config --config configs/full_example_config.yaml
sup-mimic-pipeline run --config configs/full_example_config.yaml --subject-id <SUBJECT_ID> --hadm-id <HADM_ID> --stay-id <STAY_ID>
sup-mimic-pipeline build-case --config configs/full_example_config.yaml --input-dir outputs/raw --output outputs/cases/case_profile.json
sup-mimic-pipeline screen --config configs/full_example_config.yaml --input outputs/cases/case_profile.json --output outputs/cases/screened.json
```
