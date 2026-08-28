# Compliance Guide

This repository is a methods-and-code release. It is not a data release.

## Public Boundary

Public:

- source code
- SQL templates
- configuration templates without credentials
- documentation
- synthetic examples
- aggregate figures and aggregate metrics

Restricted:

- raw MIMIC files
- database dumps
- patient-level derived CSV, JSONL, Excel, parquet, images, ECG files, CXR metadata rows, or clinical notes
- real `subject_id`, `hadm_id`, `stay_id`, `dicom_id`, or note identifiers
- prompts or model logs that contain patient-level features from MIMIC
- API keys, database DSNs with passwords, institutional usernames, or model tokens

## MIMIC / PhysioNet Handling

Authorized reproduction runs inside a local environment with approved MIMIC access from PhysioNet. The released code is used to reproduce the workflow, not to transfer data access.

Patient-level outputs produced by the code remain controlled research artifacts even when identifiers are dropped or hashed.

## LLM / API Handling

For real MIMIC-derived inputs:

- Use local models inside the controlled research environment when possible.
- Use external APIs only when the data-use approval and provider contract permit the transfer.
- Require explicit zero-retention or equivalent controls for restricted data.
- Keep prompts, responses, and logs private when they contain patient-level features.

## arXiv Handling

The arXiv source package contains manuscript source files only. It does not redistribute restricted datasets.

## Reference Links

- PhysioNet Credentialed Health Data License: https://physionet.org/about/licenses/physionet-credentialed-health-data-license-150/
- MIMIC-IV on PhysioNet: https://physionet.org/content/mimiciv/
- MIMIC project homepage: https://mimic.mit.edu/
- arXiv TeX submission help: https://info.arxiv.org/help/submit_tex.html
- arXiv license information: https://info.arxiv.org/help/license/
