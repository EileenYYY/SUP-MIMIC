-- Diagnosis sequence for one admission.

select
    d.subject_id,
    d.hadm_id,
    d.seq_num,
    d.icd_code,
    d.icd_version,
    dx.long_title
from mimiciv_hosp.diagnoses_icd d
left join mimiciv_hosp.d_icd_diagnoses dx
  on d.icd_code = dx.icd_code
 and d.icd_version = dx.icd_version
where d.hadm_id = %(hadm_id)s
order by d.seq_num, d.icd_code;

