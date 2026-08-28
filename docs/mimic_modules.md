# MIMIC Modules

The public code covers the following MIMIC-IV areas.

## Hospital

- `patients`
- `admissions`
- `transfers`
- `diagnoses_icd`
- `procedures_icd`
- `prescriptions`

## ICU

- `icustays`
- `chartevents`
- `inputevents`
- `outputevents`
- `procedureevents`
- `derived.first_day_vitalsign`
- `derived.first_day_lab`

## Emergency Department

- `edstays`
- `triage`
- `diagnosis`
- `medrecon`
- `vitalsign`
- `pyxis`

## Radiology / CXR

- CXR record list
- imaging metadata
- report text

## ECG

- ECG record table
- machine measurement table

## Notes

- discharge summary
- radiology note
- nursing note
- other narrative notes

## Release Split

- `sql/` holds extraction templates
- `docs/` holds the data dictionary and workflow notes
- `src/` holds normalization, export, and analysis code
