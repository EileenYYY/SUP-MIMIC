# SQL

This folder contains MIMIC-IV topic SQL templates.

## Structure

- `hospital/` for patients, admissions, diagnoses, and prescriptions
- `icu/` for ICU trajectory, first-day vitals, first-day labs, and event tables
- `ed/` for emergency department modules
- `cxr/` for chest X-ray record lists
- `ecg/` for ECG tables
- `note/` for optional text extraction

## Writing Rules

- use parameterized placeholders
- name columns explicitly
- keep ordering stable
- keep each file focused on one task

## Extension Targets

The following files complete the current extraction coverage:

- `icu/26_chartevents.sql`
- `icu/27_score_extracts.sql`
- `ed/12_vitalsign.sql`
- `ed/13_medrecon.sql`
- `cxr/10_cxr_record_list.sql`
- `ecg/10_ecg_record_table.sql`
- `ecg/11_ecg_machine_measurement.sql`
