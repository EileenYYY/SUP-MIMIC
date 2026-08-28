-- Demographics and patient anchor information.

select
    p.subject_id,
    p.gender,
    p.anchor_age,
    p.anchor_year,
    p.anchor_year_group,
    count(a.hadm_id) as admissions_total
from mimiciv_hosp.patients p
left join mimiciv_hosp.admissions a
  on p.subject_id = a.subject_id
where p.subject_id = %(subject_id)s
group by
    p.subject_id,
    p.gender,
    p.anchor_age,
    p.anchor_year,
    p.anchor_year_group
order by p.subject_id;

