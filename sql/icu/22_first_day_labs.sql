-- First-day laboratory summary for one ICU stay.

select
    stay_id,
    sodium_min,
    sodium_max,
    potassium_min,
    potassium_max,
    creatinine_min,
    creatinine_max,
    glucose_min,
    glucose_max,
    hemoglobin_min,
    hemoglobin_max
from mimiciv_derived.first_day_lab
where stay_id = %(stay_id)s;

