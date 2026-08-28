-- All admissions for one subject.

select
    subject_id,
    hadm_id,
    admittime,
    dischtime,
    admission_type,
    admission_location,
    discharge_location,
    insurance,
    marital_status,
    race
from mimiciv_hosp.admissions
where subject_id = %(subject_id)s
order by admittime, hadm_id;

