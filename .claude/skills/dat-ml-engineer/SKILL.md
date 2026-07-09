---
name: dat-ml-engineer
description: "ML/AI feature integration behind eval suite + failover path."
---
# Data - ML Engineer

Scaffold an ML feature pipeline with evaluation harness and rule-based fallback. Generates pipeline class, config file, and support for recommendation/classification/regression types.

## Tool
`.claude/tools/dat/ml-engineer/ml-feature.sh`

## When to use
- New ML feature: scaffold pipeline with predict/evaluate/fallback methods
- Gate 4 data layer: prepare ML integration with fallback for when model is unavailable
- Prototyping: recommendation, classification, or regression feature skeleton

## How to use
```bash
.claude/tools/dat/ml-engineer/ml-feature.sh <PRJ-ID> <feature-name> [type]
```

## Input
- `PRJ-ID` — project directory
- `feature-name` — snake_case name (e.g. `product_relevance`)
- `type` — `recommendation` (default), `classification`, or `regression`

## Output
- `app/ML/{Name}Pipeline.php` — pipeline with:
  - `predict()` — calls model inference with try/catch → fallback
  - `fallback()` — rule-based default when model unavailable
  - `evaluate()` — accuracy calculation against test set
- `app/ML/config/{name}.php` — config file with type, model_path, min_confidence, fallback_on_error, batch_size

## Related
- `engine/agents/dat/ml-engineer.md`
- `.claude/tools/dat/ml-engineer/ml-feature.sh`
