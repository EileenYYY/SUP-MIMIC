-- Emergency department stays for one subject.

select
    subject_id,
    hadm_id,
    stay_id,
    intime,
    outtime,
    gender,
    race,
    arrival_transport
from mimiciv_ed.edstays
where subject_id = %(subject_id)s
order by intime, stay_id;

