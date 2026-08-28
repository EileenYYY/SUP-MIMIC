# Reproducibility Workflow

## Stage 0: Local Setup

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .[all,dev,llm-api]
pytest
python scripts/qa_release_audit.py .
```

## Stage 1: Authorized MIMIC Database

1. Obtain MIMIC access from PhysioNet.
2. Load the required MIMIC modules into PostgreSQL or another supported local database.
3. Keep database credentials in a private config file that is ignored by Git.
4. Do not place raw CSVs or SQL exports inside the public repository.

## Stage 2: SQL Extraction

Copy a config template:

```bash
copy configs\full_example_config.yaml configs\local_private.yaml
```

Edit only the private config, then run:

```bash
sup-mimic-pipeline validate-config --config configs/local_private.yaml
sup-mimic-pipeline run --config configs/local_private.yaml --subject-id YOUR_ID --hadm-id YOUR_ID --stay-id YOUR_ID
```

The template is intentionally single-case oriented. For full benchmark construction, extend the SQL cohort queries and run them in your authorized environment.

## Stage 3: Feature Table

Construct a local feature table with one row per ICU stay or patient-diagnosis instance. The benchmark construction script expects:

```text
private_input/
  all.csv
  Sepsis.csv
  Acute_kidney_injury.csv
  ...
```

`all.csv` must include `subject_id` and `stay_id`. Each disease file must include a `stay_id` column listing positive examples for that disease.

## Stage 4: SUP-MIMIC BA/DDT/DCT Construction

```bash
python scripts/build_sup_mimic_cases.py ^
  --input-dir private_input ^
  --all-csv all.csv ^
  --output-dir private_outputs/sup_mimic_cases ^
  --top-k-features 25 ^
  --ba-n 10 ^
  --pair-n 5
```

Default output drops source identifiers and writes hashed `case_id` values. Do not publish these outputs when they are derived from real MIMIC records.

## Stage 5: LLM Evaluation

Local model:

```bash
python scripts/local_hf_evaluation.py ^
  --model-dir /path/to/your-local-model ^
  --root-dir private_outputs/sup_mimic_cases ^
  --save-dir private_outputs/local_eval ^
  --auto-pick-gpu
```

API model:

```bash
set SUP_MIMIC_API_KEY=replace-with-your-key
python scripts/llm_api_evaluation.py ^
  --root-dir private_outputs/sup_mimic_cases ^
  --save-dir private_outputs/api_eval ^
  --model gpt-4o-mini ^
  --base-url https://api.openai.com/v1/chat/completions
```

Use APIs with real MIMIC-derived prompts only when allowed by your data-use approval and provider terms.

## Stage 6: Error Attribution

```bash
python scripts/error_attribution.py ^
  --results-jsonl private_outputs/api_eval/results_stream.jsonl ^
  --case-root private_outputs/sup_mimic_cases ^
  --output-jsonl private_outputs/attribution/errors.jsonl
```

This output may contain model explanations and patient-level feature evidence. Keep it private unless formally approved for release.

## Stage 7: Public Reporting

Public materials should contain:

- Methods
- SQL templates
- Source code
- Aggregate tables
- Aggregate figures
- Synthetic examples
- Data-access instructions

Public materials should not contain:

- Patient-level rows
- Patient-level prompts
- Patient-level model responses
- Restricted derived datasets
