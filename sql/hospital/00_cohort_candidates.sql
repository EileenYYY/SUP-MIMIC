-- Cohort candidate list
-- Filter to adult hospital admissions with at least one ICU stay.

select distinct
    p.subject_id
from mimiciv_hosp.patients p
join mimiciv_hosp.admissions a
  on p.subject_id = a.subject_id
left join mimiciv_icu.icustays i
  on a.subject_id = i.subject_id
where coalesce(p.anchor_age, 0) >= 18
  and a.admission_type is distinct from 'NEWBORN'
  and (%(require_icu)s is null or (%(require_icu)s = true and i.stay_id is not null))
order by p.subject_id;
