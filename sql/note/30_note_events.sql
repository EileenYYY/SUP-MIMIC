-- Optional note extraction for one admission.

select
    note_id,
    subject_id,
    hadm_id,
    charttime,
    storetime,
    note_type,
    category,
    description,
    text
from mimiciv_note.noteevents
where hadm_id = %(hadm_id)s
order by charttime, note_id;

