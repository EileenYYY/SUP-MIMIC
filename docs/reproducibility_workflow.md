# Reproducibility Workflow

## Stage 0: Local Setup

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .[all,dev,llm-api]
pytest
```

## Stage 1: Authorized MIMIC Database

1. Obtain MIMIC access through PhysioNet.
2. Load the approved MIMIC modules into PostgreSQL or another local database.
3. Store database credentials in a private config file excluded from Git.
4. Keep raw MIMIC files and exports outside the public repository.

## Stage 2: SQL Extraction

```bash
Copy-Item configs\full_example_config.yaml configs\local_private.yaml
```

Fill the private config with the authorized database connection, then run:

```bash
sup-mimic-pipeline validate-config --config configs/local_private.yaml
sup-mimic-pipeline run --config configs/local_private.yaml --subject-id <SUBJECT_ID> --hadm-id <HADM_ID> --stay-id <STAY_ID>
```

The extraction step writes local JSONL or CSV outputs under `outputs/raw/`.

## Stage 3: Case Profile

```bash
sup-mimic-pipeline build-case --config configs/local_private.yaml --input-dir outputs/raw --output outputs/cases/case_profile.json
```

The resulting case profile merges the extracted tables into one structured record.

## Stage 4: Screening

```bash
sup-mimic-pipeline screen --config configs/local_private.yaml --input outputs/cases/case_profile.json --output outputs/cases/screened.json
```

The screening step applies age, ICU, admission, and completeness rules.

## Stage 5: Feature Table

```bash
sup-mimic-pipeline build-features --input outputs/cases/case_profile.json --output outputs/features.csv
```

The feature table is the input for statistics and classical machine-learning baselines.

## Stage 6: Statistics and ML Baseline

```bash
sup-mimic-pipeline stats-summary --input outputs/cases/case_profile.json --output outputs/reports/case_summary.json
sup-mimic-pipeline train-model --input outputs/features.csv --model-output outputs/models/baseline.pkl --metrics-output outputs/models/baseline_metrics.json
sup-mimic-pipeline evaluate-model --input outputs/features.csv --model outputs/models/baseline.pkl --output outputs/models/baseline_eval.json
```

## Stage 7: SUP-MIMIC Construction

```bash
python scripts/build_sup_mimic_cases.py ^
  --input-dir private_input ^
  --all-csv all.csv ^
  --output-dir private_outputs\sup_mimic_cases ^
  --top-k-features 25 ^
  --ba-n 10 ^
  --pair-n 5
```

The script writes one folder per disease with BA, DDT, and DCT files.

## Stage 8: Local Hugging Face Evaluation

```bash
python scripts/local_hf_evaluation.py ^
  --model-dir <LOCAL_MODEL_DIR> ^
  --root-dir private_outputs\sup_mimic_cases ^
  --save-dir private_outputs\local_eval ^
  --auto-pick-gpu
```

## Stage 9: API Evaluation

```bash
set SUP_MIMIC_API_KEY=<API_KEY>
python scripts/llm_api_evaluation.py ^
  --root-dir private_outputs\sup_mimic_cases ^
  --save-dir private_outputs\api_eval ^
  --model gpt-4o-mini ^
  --base-url https://api.openai.com/v1/chat/completions
```

External API evaluation is used only when the authorized data policy and the provider contract permit it.

## Stage 10: Error Attribution

```bash
python scripts/error_attribution.py ^
  --results-jsonl private_outputs\api_eval\results_stream.jsonl ^
  --case-root private_outputs\sup_mimic_cases ^
  --output-jsonl private_outputs\attribution\errors.jsonl
```

## Stage 11: Public Package

The public GitHub package contains:

- code
- SQL templates
- configuration templates
- synthetic examples
- documentation
- aggregate tables and figures
- arXiv source files

The public GitHub package does not contain:

- raw MIMIC data
- patient-level derived outputs
- database passwords or API keys
- private response logs
