# Evaluation design

## Core question

The evaluation does not ask only whether the training dataset became larger. It asks whether
synthetic scaling increases feature-space coverage and improves recommendations on independent,
unseen document profiles.

## Isolation boundary

- `data/seed_documents.jsonl` is the small input corpus.
- Synthetic rows are generated only from the seed corpus and controlled target strata.
- `evals/holdout_documents.jsonl` contains separate document IDs and expected settings.
- The evaluator stops if a holdout ID overlaps the seed corpus.
- Holdout labels are never used for generation or fitting.

This is code-level isolation, not a claim that the small synthetic holdout represents real users.

## Scale comparison

Every run builds three fresh training sets:

- 1x: the seed corpus only;
- 10x: seed rows plus controlled coverage variations;
- 100x: a much larger set used to test saturation and relative diversity.

## Metrics

- **Observed strata and coverage:** category, page size and quality-priority combinations present.
- **Diversity rate:** unique bounded feature signatures divided by training rows.
- **Duplicate rate:** repeated bounded feature signatures divided by training rows.
- **Exact accuracy:** every recommended print setting matches the holdout label.
- **Field accuracy:** setting-level accuracy across colour, DPI, duplex, paper and quality.
- **Rare-group accuracy:** exact accuracy for deliberately uncommon combinations.
- **Human-review rate:** share of holdout predictions held for review.

## Interpretation

The best scale is selected using field accuracy, then exact accuracy, with the smaller dataset used
when performance ties. Saturation is reported when 100x adds no meaningful field-accuracy gain and
does not increase categorical coverage over 10x.

Real validation would require a larger expert-labelled document set, actual print-quality outcomes,
printer and media constraints, subgroup confidence intervals, drift monitoring and online feedback.
