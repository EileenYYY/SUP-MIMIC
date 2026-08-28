-- ICU stays for one subject.

select
    subject_id,
    hadm_id,
    stay_id,
    intime,
    outtime,
    los,
    first_careunit,
    last_careunit
from mimiciv_icu.icustays
where subject_id = %(subject_id)s
order by intime, stay_id;

