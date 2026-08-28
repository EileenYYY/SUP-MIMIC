-- Emergency department vital signs for one subject.

select
    subject_id,
    hadm_id,
    stay_id,
    charttime,
    temperature,
    heartrate,
    resprate,
    o2sat,
    sbp,
    dbp,
    pain
from mimiciv_ed.vitalsign
where subject_id = %(subject_id)s
order by charttime, stay_id;

