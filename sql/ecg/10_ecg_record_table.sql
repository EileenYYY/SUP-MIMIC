-- ECG record table for one subject.
-- Adjust schema names to your local ECG release if needed.

select
    subject_id,
    study_id,
    ecg_time,
    report
from mimic_ecg.record_table
where subject_id = %(subject_id)s
order by ecg_time, study_id;
