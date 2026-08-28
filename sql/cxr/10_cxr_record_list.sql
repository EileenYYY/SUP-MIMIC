-- Chest X-ray record list for one subject.
-- Adjust schema names to the local CXR release if needed.

select
    subject_id,
    study_id,
    hadm_id,
    subject_id as patient_id,
    study_datetime,
    view_position
from mimic_cxr.record_list
where subject_id = %(subject_id)s
order by study_datetime, study_id;
