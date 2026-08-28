-- Emergency department medication reconciliation for one subject.

select
    subject_id,
    hadm_id,
    stay_id,
    charttime,
    name,
    dose,
    route,
    frequency
from mimiciv_ed.medrecon
where subject_id = %(subject_id)s
order by charttime, stay_id;

