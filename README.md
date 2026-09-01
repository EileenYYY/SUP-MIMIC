# SUP‑MIMIC

**A multi‑task clinical diagnosis benchmark for evaluating whether large language models remain robust when clinical evidence is similar‑but‑different or different‑but‑same.**

[Visual guide](docs/visual_guide.md) · [Tutorial](docs/tutorial.md) · [Reproducibility](docs/reproducibility_workflow.md) · [Compliance](docs/compliance.md) · [SQL](sql/README.md)

> 
> SUP‑MIMIC is a reproducibility‑first code release. It releases the benchmark construction pipeline, SQL templates, LLM evaluation code, documentation, and synthetic examples. **It does NOT redistribute MIMIC‑IV raw data or any patient‑level derived clinical records.**
> 
> 
> ⚠️ **Current status**: Manuscript is under peer‑review. This repository contains only implementation code, synthetic demonstration data and conceptual diagrams. No full paper manuscript, real experimental results or patient artifacts are included here.

![SUP‑MIMIC overview](docs/assets/01-overall-workflow.svg)

## What Problem Does SUP‑MIMIC Study?

Clinical diagnosis is not a simple one‑to‑one mapping from symptoms to diseases. Two patients can look clinically similar but require different diagnoses. Conversely, two patients can look very different but still share the same diagnosis. Standard single‑case medical QA benchmarks often miss this failure mode because they mostly test whether a model can answer one isolated question at a time.

SUP‑MIMIC asks a harder research question:
**Can an LLM preserve the correct diagnostic relationship across patient pairs when surface‑level clinical evidence is misleading?**

The benchmark is built upon locally authorized MIMIC‑IV ICU records and defines three complementary evaluation tasks:

| Task | Clinical situation | What the model must do | Main failure exposed |
| --- | --- | --- | --- |
| **BA** | One patient, one candidate disease | Decide whether the disease is present | Basic diagnostic verification |
| **DDT** | Two clinically similar patients, different labels | Accept the diagnosis for the positive case and reject it for the hard negative | Over‑reliance on surface similarity |
| **DCT** | Two clinically different patients, same positive label | Accept the diagnosis for both patients despite heterogeneous presentations | Missed atypical cases |

## Core Idea

Existing LLM medical evaluations often emphasize factual knowledge recall or isolated diagnosis. Real‑world clinical reasoning also requires robustness to contradictory evidence, comorbidity interference, and atypical presentations.

SUP‑MIMIC converts multi‑label ICU records into binary patient‑diagnosis verification tasks. For each anchor disease, it ranks diagnosis‑informative structured features, estimates patient similarity within disease‑specific feature space, and mines naturally occurring adversarial patient pairs from ICU admissions.

This benchmark advocates **pair‑aware evaluation**: performance is not only measured by single‑case prediction accuracy, but also whether the model maintains consistent diagnostic relations inside patient pairs.

## Core Contributions

1. **A pairwise clinical diagnosis benchmark.** SUP‑MIMIC formalizes two robustness settings overlooked by standard pointwise diagnosis benchmarks: diagnostic divergence and diagnostic convergence.
2. **A reproducible adversarial pair‑mining pipeline.** Combines supervised feature ranking, disease‑aware similarity estimation, and controlled pair‑selection logic.
3. **Pair‑aware evaluation metrics.** DDT and DCT are assessed via both instance‑level accuracy and pair‑level correctness that enforces internal diagnostic consistency.
4. **General‑purpose evaluation workflow.** Supports locally‑hosted open‑source LLMs and API‑based closed‑source models for systematic robustness comparison.
5. **Compliance‑first open‑source design.** Public repository only distributes code, SQL templates, documentation and synthetic examples; all restricted MIMIC‑derived patient‑level artifacts stay local to authorized researchers.

## Method Overview

SUP‑MIMIC consumes properly licensed local MIMIC‑IV data and produces private benchmark instances via the following workflow:

| Stage | Input | Operation | Output |
| --- | --- | --- | --- |
| 1. Cohort definition | MIMIC‑IV ICU records | Select adult ICU stays and candidate diagnoses | Local cohort table |
| 2. Feature extraction | SQL templates | Extract first‑24‑hour vitals, labs, scores, diagnoses, and related structured variables | Local feature table |
| 3. Disease filtering | ICD‑coded diagnoses | Remove overly broad, rare, incomplete, or unstable labels | Anchor disease set |
| 4. Feature ranking | Positive/negative cases per disease | Train disease‑specific Random Forest models | Top diagnostic features |
| 5. Similarity mining | Disease‑specific feature space | Compute patient distances | Similar / dissimilar candidate pairs |
| 6. Task construction | Labels + distances | Build BA, DDT, and DCT cases | Private benchmark files |
| 7. LLM evaluation | Structured prompts | Run local models or approved zero‑retention APIs | Private JSONL predictions |
| 8. Reporting | Private predictions | Aggregate metrics and figures | Public aggregate results |

## The Three Evaluation Tasks

### BA: Basic Assessment

BA is the ordinary single‑case diagnostic verification task. The model receives one structured patient profile and one candidate disease, then predicts whether the disease is present.

```
Patient profile + target disease -> yes / no
```

BA validates basic diagnostic capacity, but cannot test model consistency under contrastive clinical evidence.

### DDT: Diagnostic Divergence Task

DDT constructs hard pairs: two patients similar on disease‑relevant features but holding different ground‑truth labels for the anchor disease.

```
Patient A: similar profile, disease present
Patient B: similar profile, disease absent
Correct pair = A yes + B no
```

DDT examines whether models can capture decisive subtle differences instead of assigning identical diagnosis based on superficial clinical overlap.

### DCT: Diagnostic Convergence Task

DCT constructs pairs where two patients are clinically dissimilar yet share the same target disease label.

```
Patient A: atypical presentation, disease present
Patient B: different presentation, disease present
Correct pair = A yes + B yes
```

DCT tests model capacity to recognize identical disease across heterogeneous clinical manifestations, avoiding dismissal of atypical presentations.

## Metrics

SUP‑MIMIC defines conventional point‑wise metrics and novel pair‑aware robustness metrics.

| Metric | Meaning |
| --- | --- |
| `Acc_BA` | Accuracy on single‑case basic assessment |
| `Acc_DDT` | Pointwise accuracy on DDT cases |
| `Acc_DCT` | Pointwise accuracy on DCT cases |
| `PDRA_DDT` | Pair correct only when positive accepted and hard‑negative rejected |
| `PDRA_DCT` | Pair correct only when both positive instances are accepted |
| `ADR` | Average diagnostic robustness aggregated across BA and pairwise tasks |
| `SRS` | Composite robustness score penalizing performance imbalance between DDT and DCT |
| `Sick_R` | Recall for disease‑present cases |
| `Healthy_R` | Recall for disease‑absent cases |

> 
> A patient pair counts as robust **only if the internal diagnostic relationship is fully preserved**. Partial correct predictions for one single patient within a pair do not count as successful pair inference.

## Observed Failure Modes

The benchmark framework supports post‑hoc error analysis categorized into four clinically‑oriented failure modes:

| Failure mode | Description | Why it matters |
| --- | --- | --- |
| Combinatorial neglect | The model observes individual clinical clues but fails to integrate multiple signals jointly | Dominant failure mode for complex ICU cases |
| Feature misweighting | The model assigns inappropriate importance to available clinical indicators | Produces high‑confidence yet erroneous diagnosis |
| Comorbidity conflation | The target disease is confused with co‑existing comorbid conditions | Highly relevant for multi‑morbidity ICU populations |
| Biomarker omission | Relevant biomarkers are mentioned in explanation but ignored in final prediction | Exposes misalignment between reasoning trace and final prediction |

> 
> Detailed real patient‑level error examples are **not released publicly**. Derived dense clinical feature vectors and model rationales are treated as restricted artifacts under the PhysioNet Data‑Use Agreement.

## Repository Contents

```
SUP‑MIMIC‑open‑source/
  configs/               # safe config templates, NO credentials or real patient IDs
  docs/                  # compliance, reproducibility manual, visual guide
  examples/              # fully synthetic demonstration samples only
  scripts/               # benchmark construction & LLM evaluation scripts
  sql/                   # MIMIC‑IV SQL extraction templates, NO extracted real data
  src/mimic_pipeline_kit # reusable extraction, feature processing and statistic utilities
  tests/                 # unit tests running over synthetic mock data
```

## Quick Start On Synthetic Data

> 
> This demo runs on synthetic mock data only. Real MIMIC‑IV data is required for producing authentic SUP‑MIMIC benchmark instances.

Environment setup:

```
python -m venv .venv
# Windows
. .venv/Scripts/Activate.ps1
# Linux / Mac
# source .venv/bin/activate

pip install -e .[all,dev,llm-api]
pytest
```

Build tiny synthetic SUP‑MIMIC sample:

```
python scripts/build_sup_mimic_cases.py ^
  --input-dir examples/synthetic_multidisease/input ^
  --all-csv all.csv ^
  --output-dir outputs/synthetic_sup_mimic ^
  --top-k-features 8 ^
  --ba-n 2 ^
  --pair-n 2
```

Run LLM evaluation over synthetic sample with API‑compatible endpoint:

```
# Set your api key as environment variable
set SUP_MIMIC_API_KEY=<API_KEY>

python scripts/llm_api_evaluation.py ^
  --root-dir outputs/synthetic_sup_mimic ^
  --save-dir outputs/synthetic_api_eval ^
  --model gpt‑4o‑mini ^
  --base-url https://api.openai.com/v1/chat/completions
```

## Reproducing With Real MIMIC‑IV

Researchers must execute the full workflow within their own authorized MIMIC‑IV environment:

1. Complete CITI training and obtain formal MIMIC‑IV access from PhysioNet.
2. Load MIMIC‑IV dataset into local database compliant with the PhysioNet DUA.
3. Copy `configs/full_example_config.yaml` to a private local config file (add to `.gitignore`).
4. Store database credentials and api keys in environment variables or private untracked configuration.
5. Execute SQL feature extraction locally.
6. Generate SUP‑MIMIC benchmark instances locally.
7. Run LLM evaluation locally or adopt zero‑retention API services.
8. Only publish code, SQL templates, synthetic examples, and aggregated summary statistics.

![Open‑source boundary](docs/assets/02-open-source-boundary.svg)

## Compliance And Data Availability

This open‑source repository focuses on **method‑level reproducibility**. It does **not** grant access to MIMIC‑IV and does **not** redistribute any MIMIC‑derived patient‑level clinical data.

Items permitted for public release within this repository:

- Source code and python utilities
- SQL query templates for MIMIC‑IV feature extraction
- Configuration templates (without secrets)
- Fully synthetic mock examples
- Documentation, tutorials and workflow diagrams
- Aggregated, de‑identified summary metrics and conceptual figures

Items **NEVER** permitted to commit / publish to GitHub:

- Raw MIMIC‑IV source data
- Real patient‑level feature tables, benchmark jsonl/csv
- Patient‑level prompts, clinical notes, model per‑case responses
- Imaging, ECG, CXR related patient metadata
- Database credentials, api keys, access tokens or institutional access materials

Please read full statement in [docs/compliance.md](docs/compliance.md) and [docs/data_availability_statement.md](docs/data_availability_statement.md).

## Project Status

| Component | Status |
| --- | --- |
| SQL extraction templates | Included |
| Python feature‑processing utilities | Included |
| SUP‑MIMIC BA/DDT/DCT construction script | Included |
| Hugging‑Face local model evaluation script | Included |
| API‑compatible evaluation script | Included |
| Error‑analysis scaffold | Included |
| Synthetic demonstration examples | Included |
| Real MIMIC‑IV raw data | Not included |
| Real patient‑level benchmark files | Not included |

> 
> Manuscript PDF, LaTeX source and full experimental result tables will be added after paper acceptance / official preprint release.

## Citation

If you utilize this code repository in your research, please cite this code artifact:

```
@misc{yu2026supmimic,
  title={SUP-MIMIC: A Multi-Task Clinical Diagnosis Benchmark for Evaluating LLMs' Robustness to Contradictory Evidence},
  author={Yu, Yi and Wang, Bo and Feng, Chong and Shi, Ge and Liu, Xia and Yang, Ziyi and Shi, Xuewen},
  year={2026},
  eprint={2608.29582},
  archivePrefix={arXiv},
  primaryClass={cs.CL},
  url={https://arxiv.org/abs/2608.29582}
}
```

## License

Code and documentation within this repository are released under the **MIT License**.

This license applies solely to repository‑hosted implementation artifacts. It **does not** grant access to MIMIC‑IV dataset, does not redistribute MIMIC‑IV data, and cannot override any terms of the PhysioNet Data‑Use‑Agreement. All users must independently comply with PhysioNet licensing requirements when working with MIMIC‑IV.

---

。
