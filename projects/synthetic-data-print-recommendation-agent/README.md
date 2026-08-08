# Synthetic Data and Print Recommendation Agent

[Back to the Applied Agentic AI portfolio](../../README.md)

An evaluation-driven project for a practical data-scarcity problem: real labelled documents are
limited, but a print recommendation system needs diverse document categories, layouts and quality
requirements. The project generates controlled synthetic variations, engineers document features,
trains a small local recommender and compares 1x, 10x and 100x scaling on a separately versioned
synthetic holdout with disjoint IDs. The expected settings use the same documented synthetic policy
assumptions, so the results test a controlled synthetic world rather than independent ground truth.

This is an independent portfolio implementation by **Shivanand Kumar**. All document profiles are
synthetic. The project contains no employer documents, print rules, source code or confidential
architecture. It demonstrates project capability, not production ownership.

## Business question

More synthetic rows do not automatically mean more useful information. A generator can amplify
bias, repeat low-diversity patterns, create distribution mismatch or reinforce incorrect labels.
The central question is:

> Does synthetic scaling add new feature coverage and improve recommendations on a separately
> versioned synthetic holdout, or does performance saturate while volume continues to grow?

## End-to-end flow

```mermaid
flowchart LR
    S["Limited seed documents"] --> A["Scarcity analyser"]
    A --> G["Controlled corpus generator"]
    G --> F["Document feature engineering"]
    F --> M["Distance-weighted recommendation model"]
    M --> H["Synthetic holdout evaluation"]
    H --> J["Evaluation findings"]
    M --> R["Print recommendation JSON"]
    R --> Q["Review-required flag"]
```

The code does not pretend that automated labels are human validation. Ambiguous and low-confidence
cases return a review-required flag; there is no implemented queue or approval workflow. Holdout
IDs remain separate from generation and fitting, but expected settings come from the same documented
synthetic policy world.

## What it demonstrates

- Scarcity analysis using categorical coverage and rare document segments.
- Controlled synthetic generation at 1x, 10x and 100x with deterministic seeds.
- Feature engineering for category, text/image/colour balance, page size, length and quality need.
- A bounded local recommendation agent with evidence IDs and confidence.
- Structured print-setting JSON with no print execution.
- Review-required flags for low confidence, out-of-distribution and threshold-boundary cases.
- Separately versioned synthetic holdout evaluation with disjoint document IDs.
- Diversity, duplicate, coverage and saturation checks to expose synthetic-data failure modes.
- FastAPI endpoints, Pydantic validation, tests, Docker packaging and CI.

## Quick start

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
uvicorn print_recommendation_agent.api:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the generated API interface.

### Analyse scarcity

```bash
curl -s http://127.0.0.1:8000/v1/scarcity
```

### Request a print recommendation

```bash
curl -s http://127.0.0.1:8000/v1/recommend \
  -H 'Content-Type: application/json' \
  -d '{
    "document_id": "incoming_brochure_001",
    "category": "brochure",
    "text_ratio": 0.30,
    "image_ratio": 0.70,
    "color_ratio": 0.82,
    "page_size": "A4",
    "page_count": 8,
    "quality_priority": "premium"
  }'
```

The response contains recommended settings, confidence, evidence document IDs, reasons,
`human_review_required` and `execution_performed=false`.

## Evaluation

```bash
print-agent-eval
pytest
ruff check .
```

The evaluation rebuilds the training corpus separately at 1x, 10x and 100x, then tests each
version against synthetic holdout documents that generation and fitting never see. Expected
settings follow the same documented synthetic policy assumptions. Metrics are reported
separately for volume, feature-space coverage, duplicates, exact recommendation accuracy,
per-setting accuracy, rare groups and human-review rate.

See [Evaluation design](docs/evaluation.md) and [Architecture and trade-offs](docs/architecture.md).

## Safety and validity boundaries

- Inputs are synthetic document metadata, not uploaded PDFs or employer files.
- Synthetic labels are not described as ground truth or human validation.
- The holdout set is never used for synthetic generation or model fitting.
- Holdout IDs are disjoint, but the expected settings are not independent expert labels.
- Low-confidence or unusual inputs require human review.
- The service recommends settings but cannot operate a printer.
- Increasing data volume is not treated as success without diversity and holdout metrics.
- Real deployment would require domain-expert labels, printer-specific constraints, user feedback,
  privacy controls, drift monitoring and controlled online experiments.

## Interview-ready explanation

> I built a synthetic-data and print-recommendation agent around a data-scarcity problem. It first
> measures which document segments are missing, creates deterministic controlled variations and
> engineers document characteristics. A local recommender returns structured print settings with
> evidence and a review-required flag. The key design choice is evaluation: I compare 1x, 10x and
> 100x training scales on a separately versioned synthetic holdout with disjoint IDs and measure
> diversity, rare-group performance and
> saturation, so more synthetic volume is not automatically treated as better.

See the [interview guide](docs/interview-guide.md) for likely design questions and honest limits.

## Project layout

```text
src/       Scarcity analysis, generation, features, model, service, API and evaluation
data/      Synthetic seed document profiles
evals/     Separately versioned synthetic holdout document profiles
tests/     Generation, recommendation, API, safety and evaluation tests
docs/      Architecture, evaluation and interview guidance
```

## License

[MIT](../../LICENSE)
