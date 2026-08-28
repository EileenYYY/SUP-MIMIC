# Compliance Guide

This repository is a methods and code release. It is not a data release.

## Public Release Boundary

Safe to publish:

- Source code
- SQL templates
- Configuration templates without credentials or real IDs
- Documentation
- Synthetic examples
- Aggregate figures and aggregate metrics after review

Do not publish:

- Raw MIMIC files
- Database dumps
- Patient-level derived CSV, JSONL, Excel, parquet, images, ECG files, CXR metadata rows, or clinical notes
- Real `subject_id`, `hadm_id`, `stay_id`, `dicom_id`, or note identifiers
- Prompts or model logs that contain patient-level features from MIMIC
- API keys, database DSNs with passwords, institutional usernames, or model service tokens

## MIMIC/PhysioNet Handling

Reproducers must obtain their own authorized access to MIMIC through PhysioNet, complete required training, and run the pipeline locally. This repository must not be used to transfer MIMIC access to another person.

Patient-level outputs produced by this code remain controlled research artifacts. Even if IDs are dropped or hashed, rich clinical feature vectors can still be re-identification-sensitive and may remain restricted derived data.

## LLM/API Handling

For real MIMIC-derived inputs:

- Prefer local models inside the controlled research environment.
- Use external APIs only if your institutional approval and the provider contract allow it.
- Require explicit zero-retention or equivalent controls for protected/restricted data.
- Do not paste MIMIC rows, notes, reports, or prompts containing patient-level features into public chat tools.
- Do not commit request/response logs if they include real patient-level features.

## arXiv Handling

arXiv can host the manuscript and source files, but it should not be used as a channel to distribute restricted datasets. Include code availability and data availability statements that point users to PhysioNet access procedures and to this code repository.

Detailed per-case appendix examples should be reviewed carefully. If they contain many patient-level measurements, treat them as potentially restricted derived records unless they are explicitly synthetic or sufficiently transformed under your institution's policy.

## Pre-Release Checklist

Run:

```bash
python scripts/qa_release_audit.py .
```

Then manually verify:

- `git status --short` shows only intended files.
- No real MIMIC data or derived patient-level outputs are present.
- No API keys or database passwords are present.
- `configs/` contains templates only.
- `arxiv/source/` excludes build logs, reviewer correspondence, and private download folders.
- Figures do not display patient-level tables, report screenshots, or identifiable examples.

## Official References

- PhysioNet Credentialed Health Data License: https://physionet.org/about/licenses/physionet-credentialed-health-data-license-150/
- MIMIC-IV on PhysioNet: https://physionet.org/content/mimiciv/
- MIMIC project homepage: https://mimic.mit.edu/
- arXiv TeX submission help: https://info.arxiv.org/help/submit_tex.html
- arXiv license information: https://info.arxiv.org/help/license/
