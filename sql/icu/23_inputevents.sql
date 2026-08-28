-- ICU input events for one stay.

select
    subject_id,
    hadm_id,
    stay_id,
    starttime,
    endtime,
    itemid,
    amount,
    amountuom,
    rate,
    rateuom
from mimiciv_icu.inputevents
where stay_id = %(stay_id)s
order by starttime, itemid;

