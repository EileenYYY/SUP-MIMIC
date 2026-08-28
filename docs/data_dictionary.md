# Data Dictionary

## Hospital schema

| Source | Typical fields | Purpose |
|---|---|---|
| `mimiciv_hosp.patients` | `subject_id`, `gender`, `anchor_age`, `anchor_year`, `anchor_year_group` | demographic base |
| `mimiciv_hosp.admissions` | `hadm_id`, `admittime`, `dischtime`, `admission_type`, `discharge_location` | encounter timeline |
| `mimiciv_hosp.diagnoses_icd` | `subject_id`, `hadm_id`, `seq_num`, `icd_code`, `icd_version` | diagnosis sequence |
| `mimiciv_hosp.d_icd_diagnoses` | `icd_code`, `long_title` | diagnosis labels |
| `mimiciv_hosp.procedures_icd` | `subject_id`, `hadm_id`, `seq_num`, `icd_code`, `chartdate` | procedures |
| `mimiciv_hosp.d_icd_procedures` | `icd_code`, `long_title` | procedure labels |
| `mimiciv_hosp.prescriptions` | `drug`, `dose_val_rx`, `route`, `starttime`, `stoptime` | medication orders |

## Emergency Department schema

| Source | Typical fields | Purpose |
|---|---|---|
| `mimiciv_ed.edstays` | `stay_id`, `intime`, `outtime`, `arrival_transport` | ED stay anchor |
| `mimiciv_ed.triage` | `esi`, `acuity`, `chiefcomplaint` | triage profile |
| `mimiciv_ed.vitalsign` | `heartrate`, `resprate`, `sbp`, `dbp`, `o2sat` | ED vitals |
| `mimiciv_ed.medrecon` | `name`, `dose`, `route`, `frequency` | med reconciliation |

## ICU schema

| Source | Typical fields | Purpose |
|---|---|---|
| `mimiciv_icu.icustays` | `stay_id`, `intime`, `outtime`, `first_careunit` | ICU episode anchor |
| `mimiciv_derived.first_day_vitalsign` | `heart_rate_mean`, `sbp_max`, `spo2_min`, `temperature_mean` | first-day vitals |
| `mimiciv_derived.first_day_lab` | `sodium_max`, `potassium_min`, `creatinine_max`, `glucose_min` | first-day labs |

## Imaging and ECG

| Source | Typical fields | Purpose |
|---|---|---|
| `mimic_cxr.record_list` | `study_id`, `study_datetime`, `view_position` | CXR index |
| `mimic_ecg.record_table` | `study_id`, `ecg_time`, `report` | ECG report |
| `mimic_ecg.machine_measurement` | `measurement_name`, `measurement_value` | ECG machine output |

## Optional note schema

| Source | Typical fields | Purpose |
|---|---|---|
| `mimiciv_note.noteevents` | `note_id`, `subject_id`, `hadm_id`, `charttime`, `note_type` | narrative text extraction |
