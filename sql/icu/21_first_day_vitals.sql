-- First-day vital signs for one ICU stay.

select
    stay_id,
    heart_rate_mean,
    sbp_mean,
    sbp_max,
    dbp_mean,
    dbp_min,
    resp_rate_mean,
    resp_rate_max,
    spo2_mean,
    spo2_min,
    temperature_mean
from mimiciv_derived.first_day_vitalsign
where stay_id = %(stay_id)s;

