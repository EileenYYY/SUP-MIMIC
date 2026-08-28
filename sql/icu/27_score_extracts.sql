-- Example score extracts from ICU derived or raw events.
-- Adjust the source table to your local MIMIC-IV release if needed.

select
    stay_id,
    sofa,
    sapsii,
    oasys,
    qsofa
from mimiciv_derived.icu_scores
where stay_id = %(stay_id)s;
