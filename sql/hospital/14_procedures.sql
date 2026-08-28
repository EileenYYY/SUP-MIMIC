-- Procedure sequence for one admission.

select
    p.subject_id,
    p.hadm_id,
    p.seq_num,
    p.icd_code,
    p.icd_version,
    p.chartdate,
    dx.long_title
from mimiciv_hosp.procedures_icd p
left join mimiciv_hosp.d_icd_procedures dx
  on p.icd_code = dx.icd_code
 and p.icd_version = dx.icd_version
where p.hadm_id = %(hadm_id)s
order by p.seq_num, p.icd_code;

