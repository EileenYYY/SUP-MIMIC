-- Emergency department triage records for one subject.

select
    subject_id,
    hadm_id,
    stay_id,
    intime,
    esi,
    acuity,
    chiefcomplaint
from mimiciv_ed.triage
where subject_id = %(subject_id)s
order by intime, stay_id;

