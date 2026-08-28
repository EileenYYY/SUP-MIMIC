# Tutorial

This tutorial describes the full public workflow around SUP-MIMIC.

## 1. Environment

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .[all,dev,llm-api]
pytest
```

The project exposes the command line entry point `sup-mimic-pipeline` and the alias `mimic-pipeline`.

## 2. Authorized Database

MIMIC-IV data are loaded into a local PostgreSQL instance that is authorized for the study.

Expected schemas:

- `mimiciv_hosp`
- `mimiciv_icu`
- `mimiciv_derived`
- `mimiciv_ed`
- `mimiciv_note`

The public repository keeps only the configuration template. The private connection string lives in a local config file excluded from Git.

## 3. Private Config

```bash
Copy-Item configs\full_example_config.yaml configs\local_private.yaml
```

The private config contains:

- the database DSN
- schema names
- SQL job definitions
- output paths
- screening rules

The public template uses placeholder values and does not contain credentials.

## 4. SQL Extraction

```bash
sup-mimic-pipeline validate-config --config configs/local_private.yaml
sup-mimic-pipeline run --config configs/local_private.yaml --subject-id <SUBJECT_ID> --hadm-id <HADM_ID> --stay-id <STAY_ID>
```

The run command executes the SQL jobs defined in the config and writes the results to `outputs/raw/`.

Main output files:

- `patients.jsonl`
- `admissions.jsonl`
- `icustays.jsonl`
- `first_day_labs.jsonl`
- `first_day_vitals.jsonl`
- `diagnoses.jsonl`
- `procedures.jsonl`
- `prescriptions.jsonl`
- optional ED, CXR, ECG, and note files when the config enables them

## 5. Case Profile

```bash
sup-mimic-pipeline build-case --config configs/local_private.yaml --input-dir outputs/raw --output outputs/cases/case_profile.json
```

The case profile merges the extracted tables into one structured record with:

- patient information
- admissions
- ICU stays
- first-day labs
- first-day vitals
- diagnoses
- procedures
- prescriptions
- optional ED, CXR, ECG, and note records

## 6. Screening

```bash
sup-mimic-pipeline screen --config configs/local_private.yaml --input outputs/cases/case_profile.json --output outputs/cases/screened.json
```

The screening step applies the configured age, ICU, admission, and completeness conditions.

## 7. Feature Table

```bash
sup-mimic-pipeline build-features --input outputs/cases/case_profile.json --output outputs/features.csv
```

The feature table flattens the case profile into one row per instance for classical ML baselines and statistics.

## 8. Statistics

```bash
sup-mimic-pipeline stats-summary --input outputs/cases/case_profile.json --output outputs/reports/case_summary.json
```

The command supports:

- full-record summary
- field frequency counting
- grouped summaries

## 9. Classical Baseline

```bash
sup-mimic-pipeline train-model --input outputs/features.csv --model-output outputs/models/baseline.pkl --metrics-output outputs/models/baseline_metrics.json
sup-mimic-pipeline evaluate-model --input outputs/features.csv --model outputs/models/baseline.pkl --output outputs/models/baseline_eval.json
```

The baseline trainer reads the label column defined by `--label-key` and writes both model and metrics artifacts.

## 10. SUP-MIMIC Case Construction

The construction script reads a local feature table named `all.csv` plus one disease file per label. Each disease file contains the positive `stay_id` values.

Example input directory:

```text
private_input/
  all.csv
  Sepsis.csv
  Acute_kidney_injury.csv
  ...
```

Run:

```bash
python scripts/build_sup_mimic_cases.py ^
  --input-dir private_input ^
  --all-csv all.csv ^
  --output-dir private_outputs\sup_mimic_cases ^
  --top-k-features 25 ^
  --ba-n 10 ^
  --pair-n 5
```

Outputs per disease:

- `A_class_basic_assessment.csv`
- `B_class_ddt_pairs.csv`
- `C_class_dct_pairs.csv`
- `selected_features.csv`

## 11. Local Hugging Face Evaluation

```bash
python scripts/local_hf_evaluation.py ^
  --model-dir <LOCAL_MODEL_DIR> ^
  --root-dir private_outputs\sup_mimic_cases ^
  --save-dir private_outputs\local_eval ^
  --auto-pick-gpu
```

The local evaluator writes a streaming JSONL file with one record per case.

## 12. API Evaluation

```bash
set SUP_MIMIC_API_KEY=<API_KEY>
python scripts/llm_api_evaluation.py ^
  --root-dir private_outputs\sup_mimic_cases ^
  --save-dir private_outputs\api_eval ^
  --model gpt-4o-mini ^
  --base-url https://api.openai.com/v1/chat/completions
```

The API evaluator reads the API key from the environment and writes `results_stream.jsonl` plus a summary CSV.

## 13. Error Attribution

```bash
python scripts/error_attribution.py ^
  --results-jsonl private_outputs\api_eval\results_stream.jsonl ^
  --case-root private_outputs\sup_mimic_cases ^
  --output-jsonl private_outputs\attribution\errors.jsonl
```

The attribution script classifies each wrong prediction into one of the SUP-MIMIC failure modes.

## 14. Public Package Contents

The public repository contains:

- code
- SQL templates
- documentation
- synthetic examples
- aggregate figures
- aggregate tables
- arXiv source files

The public repository does not contain:

- raw MIMIC data
- patient-level benchmark files
- patient-level prompts or responses
- credentials
- internal review files
