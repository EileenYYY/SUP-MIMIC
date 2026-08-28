-- ICU procedure events for one stay.

select
    subject_id,
    hadm_id,
    stay_id,
    starttime,
    endtime,
    itemid,
    value,
    valueuom
from mimiciv_icu.procedureevents
where stay_id = %(stay_id)s
order by starttime, itemid;

