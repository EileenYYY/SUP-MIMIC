# SUP‑MIMIC
**A multi‑task clinical diagnosis benchmark for evaluating whether large language models remain robust when clinical evidence is similar‑but‑different or different‑but‑same.**

[Visual guide](docs/visual_guide.md) · [Tutorial](docs/tutorial.md) · [Reproducibility](docs/reproducibility_workflow.md) · [Compliance](docs/compliance.md) · [SQL](sql/README.md)

> SUP‑MIMIC is a reproducibility‑first code release. It releases the benchmark construction pipeline, SQL templates, LLM evaluation code, documentation, and synthetic examples. **It does not redistribute MIMIC data or patient‑level derived records.**

![SUP‑MIMIC overview](docs/assets/01-overall-workflow.svg)

## What Problem Does SUP‑MIMIC Study?
Clinical diagnosis is not a simple one‑to‑one mapping from symptoms to diseases. Two patients can look clinically similar but require different diagnoses. Conversely, two patients can look very different but still share the same diagnosis. Standard single‑case medical QA benchmarks often miss this failure mode because they mostly test whether a model can answer one isolated question at a time.

SUP‑MIMIC asks a harder question:
**Can an LLM preserve the correct diagnostic relationship across patient pairs when surface‑level clinical evidence is misleading?**

The benchmark is built from authorized local MIMIC‑IV ICU records and evaluates LLMs with three complementary tasks:

| Task | Clinical situation | What the model must do | Main failure exposed |
|---|---|---|---|
| **BA** | One patient, one candidate disease | Decide whether the disease is present | Basic diagnostic verification |
| **DDT** | Two clinically similar patients, different labels | Accept the diagnosis for the positive case and reject it for the hard negative | Over‑reliance on surface similarity |
| **DCT** | Two clinically different patients, same positive label | Accept the diagnosis for both patients despite heterogeneous presentations | Missed atypical cases |

## Core Idea
Existing LLM medical evaluations often emphasize factual knowledge recall or isolated diagnosis. Real clinical reasoning also requires robustness to contradictory evidence, comorbidity interference, and atypical presentations.

SUP‑MIMIC converts multi‑label ICU records into binary patient‑diagnosis verification tasks. For each anchor disease, it ranks diagnosis‑informative structured features, estimates patient similarity in that disease‑specific feature space, and mines naturally occurring adversarial pairs from real ICU records.

The benchmark is designed for **pair‑aware evaluation**: it cares not only about single‑case prediction accuracy but also whether the model preserves the diagnostic relationship within patient pairs.

## Core Contributions
1. **A pairwise clinical diagnosis benchmark.** SUP‑MIMIC formalizes two robustness settings that standard pointwise diagnosis misses: diagnostic divergence and diagnostic convergence.
2. **A reproducible adversarial pair mining pipeline.** The construction method combines supervised feature ranking, disease‑specific similarity estimation, and controlled pair selection.
3. **Pair‑aware evaluation metrics.** DDT and DCT are evaluated not only by per‑case accuracy but also by whether the model preserves the diagnostic relationship within a pair.
4. **General evaluation workflow.** Supports open‑source local LLMs and API‑based closed‑source models for systematic robustness comparison.
5. **A compliance‑conscious release.** The public repository contains code, SQL, documentation, and synthetic examples while keeping restricted MIMIC‑derived patient‑level artifacts out of GitHub.

## Method Overview
SUP‑MIMIC starts from authorized local MIMIC‑IV data and produces private benchmark cases through the following stages:

| Stage | Input | Operation | Output |
|---|---|---|---|
| 1. Cohort definition | MIMIC‑IV ICU records | Select adult ICU stays and candidate diagnoses | Local cohort table |
| 2. Feature extraction | SQL templates | Extract first‑24‑hour vitals, labs, scores, diagnoses, and related structured variables | Local feature table |
| 3. Disease filtering | ICD‑coded diagnoses | Remove overly broad, rare, incomplete, or unstable labels | Anchor disease set |
| 4. Feature ranking | Positive/negative cases per disease | Train disease‑specific Random Forest models | Top diagnostic features |
| 5. Similarity mining | Disease‑specific feature space | Compute patient distances | Similar / dissimilar candidate pairs |
| 6. Task construction | Labels + distances | Build BA, DDT, and DCT cases | Private benchmark files |
| 7. LLM evaluation | Structured prompts | Run local models or approved APIs | Private JSONL predictions |
| 8. Reporting | Private predictions | Aggregate metrics and figures | Public aggregate results |

## The Three Evaluation Tasks
### BA: Basic Assessment
BA is the ordinary single‑case diagnostic verification task. The model receives one structured patient profile and one candidate disease, then predicts whether the disease is present.
```text
Patient profile + target disease -> yes / no
