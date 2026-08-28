-- ECG machine measurement table for one subject.

select
    subject_id,
    study_id,
    measurement_name,
    measurement_value,
    measurement_unit
from mimic_ecg.machine_measurement
where subject_id = %(subject_id)s
order by study_id, measurement_name;

