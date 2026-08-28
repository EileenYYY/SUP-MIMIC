-- Medication orders for one admission.

select
    subject_id,
    hadm_id,
    starttime,
    stoptime,
    drug,
    dose_val_rx,
    dose_unit_rx,
    route,
    pharmacy_id
from mimiciv_hosp.prescriptions
where hadm_id = %(hadm_id)s
order by starttime desc nulls last, drug;

