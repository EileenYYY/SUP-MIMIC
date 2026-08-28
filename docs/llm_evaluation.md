# LLM Evaluation Notes

SUP-MIMIC evaluates single-disease binary verification from structured clinical features.

## Output Schema

Models are prompted to return:

```json
{
  "disease": "Sepsis",
  "prediction": "yes",
  "confidence": 0.73,
  "rationale": "short rationale",
  "explanation": "evidence-grounded explanation"
}
```

`prediction` is normalized across `yes/no`, `true/false`, `1/0`, and Chinese `是/否`.

## Input Minimization

Evaluation scripts exclude source identifiers from prompts:

- `subject_id`
- `hadm_id`
- `stay_id`
- `dicom_id`
- `study_id`

This does not make real feature vectors automatically public. It only reduces unnecessary disclosure during private inference.

## Recommended Runs

1. Smoke-test with `examples/sup_mimic_synthetic`.
2. Run local models first.
3. Run API models only after data-governance review.
4. Save raw JSONL logs privately.
5. Export only aggregate metrics for public reporting.

## Metrics

The scripts write row-level predictions. Downstream analysis can compute:

- Pointwise accuracy
- BA accuracy
- DDT pair success
- DCT pair success
- Sick recall
- Healthy recall
- Calibration and confidence diagnostics
- Failure-mode proportions

Keep metric code deterministic and record model name, model version, decoding settings, and prompt version.
