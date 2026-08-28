-- ICU chart events for one stay.

select
    subject_id,
    hadm_id,
    stay_id,
    charttime,
    itemid,
    value,
    valuenum,
    valueuom
from mimiciv_icu.chartevents
where stay_id = %(stay_id)s
order by charttime, itemid;

