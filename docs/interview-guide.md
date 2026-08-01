# Interview guide

## 30-second explanation

I built a synthetic data-platform reliability agent that diagnoses pipeline failures from three
evidence sources: run events, versioned data contracts and operational runbooks. The agent selects
read-only tools, validates every argument against tenant scope, retrieves runbooks from Qdrant and
returns evidence, citations, confidence and a proposed recovery step. Remediation is never executed;
human approval is outside the service. A 25-case suite checks tool selection, grounding and safety.

## Two-minute architecture answer

The API first validates the request with Pydantic and establishes tenant scope. A bounded planner
can call a tenant-scoped SQL event query, contract inspector and Qdrant runbook search. The tool
registry rejects mismatched tenant arguments. A deterministic synthesizer separates direct evidence
from likely causes and recommendations. It calculates confidence from evidence coverage, attaches
retrieval citations and marks any recovery action as approval-required. Offline mode is fully
reproducible; optional OpenAI mode uses the same tools through strict function calling. CI runs lint,
API, tenant-isolation and versioned evaluation checks.

## Three production-style failure cases

1. **Cross-tenant tool argument:** the tool registry blocks the call before storage access.
2. **Prompt injection inside a runbook:** runbook content is treated as evidence, never as executable
   instruction; only application-defined tools exist.
3. **LLM timeout or malformed tool call:** the live planner is bounded and falls back to the offline
   deterministic path; strict schemas and Pydantic reject malformed data.

## Important trade-off

The project prefers bounded autonomy over a highly autonomous agent. That reduces the number of
incident types it can solve, but improves traceability, tenant safety and evaluation. More tools
should be added only with a specific failure case and a corresponding regression test.

## Likely questions

### Why RAG instead of fine-tuning?

Runbooks change and answers need citations. Retrieval keeps knowledge external, updateable and
inspectable. Fine-tuning would not be the primary mechanism for injecting current operational facts.

### Why Qdrant?

It provides a real vector-store interface and metadata-ready retrieval while supporting a local
in-memory demo. The repository uses deterministic local embeddings for reproducibility, not to claim
state-of-the-art semantic retrieval.

### Why an agent instead of a fixed workflow?

Different failures need different evidence. Schema drift needs contract inspection; an SLA breach
may need events and performance guidance. Conditional tool choice is useful, while the application
still controls the tool allow-list, tenant scope and maximum steps.

### How is retrieval evaluated separately?

This first version checks expected tool selection and citation presence. The next retrieval-specific
layer would add expected source IDs, recall at k, mean reciprocal rank and metadata-filter tests.

### How do you prevent destructive autonomous actions?

The agent has no write tool. Its remediation endpoint produces a preview only. Every state-changing
recommendation is marked approval-required and the response records `execution_performed=false`.

### What is production-ready versus portfolio-ready?

The repository is portfolio-ready and locally tested. Production would additionally require real
identity-derived tenant scope, managed storage, secrets, observability, rate limiting, workload
benchmarks, hybrid retrieval, deployment controls and a separately authorized execution service.
