-- ICU output events for one stay.

select
    subject_id,
    hadm_id,
    stay_id,
    charttime,
    itemid,
    value,
    valueuom
from mimiciv_icu.outputevents
where stay_id = %(stay_id)s
order by charttime, itemid;

