# Applied Agentic AI Portfolio

[![CI](https://github.com/omni-shiva/shiva-applied-agentic/actions/workflows/ci.yml/badge.svg)](https://github.com/omni-shiva/shiva-applied-agentic/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A multi-project portfolio that connects data engineering with safe, evaluation-driven AI agents.
Every project is self-contained: its agent, tools, synthetic data, evaluation cases, tests,
documentation and setup instructions stay inside its own folder.

All examples are independent portfolio implementations by **Shivanand Kumar**. They use synthetic
data and do not contain employer code, data, configurations or confidential architecture. Agentic
AI, RAG, vector search and synthetic-data evaluation are presented as hands-on project capability,
not as production ownership.

## Projects

| Project | Agent and purpose | Main evidence | Status |
|---|---|---|---|
| [Data Platform Reliability Agent](projects/data-platform-reliability-agent/) | Investigates synthetic pipeline incidents with tenant-safe tools, contract inspection and runbook retrieval. It proposes remediation but never executes it. | FastAPI, Pydantic, Qdrant, tenant-scoped SQL, citations, approval controls, 25 evaluation cases | Code and evaluation complete |
| [Synthetic Data and Print Recommendation Agent](projects/synthetic-data-print-recommendation-agent/) | Detects training-data scarcity, generates controlled document variations, engineers document features and recommends print settings with confidence and human-review gates. | Scarcity analysis, 1x/10x/100x synthetic generation, independent holdout evaluation, structured API responses, bias and saturation checks | Code and evaluation complete |

**Current project count: 2.**

## Portfolio structure

```text
projects/
  data-platform-reliability-agent/
    src/       Agent, tools, retrieval, API and evaluation code
    data/      Synthetic events, contracts and runbooks
    evals/     Versioned evaluation cases
    tests/     API, retrieval, safety and evaluation tests
    docs/      Architecture, evaluation and interview guidance
  synthetic-data-print-recommendation-agent/
    src/       Scarcity, generation, features, recommender and API code
    data/      Small synthetic seed corpus
    evals/     Independent labelled holdout documents
    tests/     Generation, recommendation, safety and evaluation tests
    docs/      Architecture, evaluation and interview guidance
.github/workflows/
  ci.yml       Runs lint and tests independently for both projects
```

There is deliberately no single universal agent or shared domain skill. Pipeline diagnosis and
print recommendation have different inputs, tools, safety rules and evaluation criteria, so each
project owns its complete implementation.

## Run a project

Each project has its own README and Python package. For example:

```bash
cd projects/data-platform-reliability-agent
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
```

Use the same process inside `projects/synthetic-data-print-recommendation-agent`.

## Engineering principles

- Synthetic or public-safe data only.
- Structured inputs and outputs with application validation.
- Evaluation datasets versioned with the code.
- Human review before risky or low-confidence decisions.
- No autonomous production actions.
- Clear separation between direct evidence, model inference and limitations.
- Honest distinction between portfolio capability and production experience.

## License

[MIT](LICENSE)
