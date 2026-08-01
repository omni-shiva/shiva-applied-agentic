# Architecture and trade-offs

## Offline training flow

1. Load a small synthetic seed corpus representing limited labelled documents.
2. Measure missing category, page-size and quality-priority strata.
3. Generate deterministic controlled variations at 1x, 10x or 100x scale.
4. Engineer transparent features from document category, content balance, colour use, page size,
   page count and quality priority.
5. Apply a documented policy to create experimental synthetic labels.
6. Mark ambiguous policy-boundary labels for human review.
7. Fit a distance-weighted local recommendation agent.
8. Evaluate on a separately versioned holdout set that is never used for generation or fitting.

## Online recommendation flow

1. FastAPI and Pydantic validate a document profile.
2. The service creates the same transparent feature vector used during evaluation.
3. The agent retrieves the nearest labelled profiles.
4. Each print-setting field is selected by distance-weighted evidence.
5. Confidence, evidence IDs and reasons are returned with the settings.
6. Policy-boundary, low-confidence and out-of-distribution cases require human review.
7. The service always returns `execution_performed=false`.

## Why a bounded local agent

The project is about data scarcity and evaluation, not model scale. A transparent local model keeps
results deterministic, allows exact regression tests and makes the effect of synthetic volume easy
to inspect. A hosted LLM could later help explain recommendations or extract features from real
documents, but it should not replace structured validation or independent evaluation.

## Failure controls

| Failure | Control |
|---|---|
| Synthetic volume repeats the same patterns | Diversity, duplicate and categorical-coverage metrics |
| Generator assumptions reinforce labels | Independent holdout labels and explicit synthetic label source |
| Rare groups are hidden by overall accuracy | Separate rare-group accuracy |
| Performance stops improving | Direct 1x, 10x and 100x saturation comparison |
| Unusual input receives false certainty | Distance and confidence review gates |
| Ambiguous thresholds create brittle labels | Human-review queue for boundary cases |
| Recommendation triggers a real action | No printer integration and `execution_performed=false` |

## Main trade-offs

- **Synthetic coverage versus realism:** controlled combinations fill gaps but do not prove real
  document diversity.
- **Transparent features versus raw-document capability:** metadata is inspectable and safe, but a
  real system would need robust PDF parsing, image analysis and privacy controls.
- **Local nearest-neighbour model versus scale:** it is deterministic and explainable, but not a
  production recommendation model.
- **More data versus more information:** 100x can add rows without improving holdout results.
- **Automatic policy labels versus expert truth:** policy labels enable a reproducible demo, but
  domain experts must validate real labels and printer-specific constraints.
