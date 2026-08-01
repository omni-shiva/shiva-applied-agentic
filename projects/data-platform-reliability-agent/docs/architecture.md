# Architecture and trade-offs

## Request path

1. FastAPI validates tenant, pipeline and question fields with strict Pydantic models.
2. A planner selects from three read-only tools: event query, contract inspection and runbook search.
3. The tool registry checks that every generated tenant argument matches the authorized context.
4. Results are reduced into facts, hypotheses, recommendations, citations and a confidence score.
5. A safety boundary marks state-changing recovery as approval-required and performs no execution.
6. The same public service can run the versioned evaluation dataset.

## Why a bounded agent

A fixed workflow would be simpler if every incident needed identical evidence. An agent is useful
here because schema incidents require contract inspection, while SLA or credential incidents may
need only run history and runbooks. The planner therefore has conditional choice, but the tool set,
tenant boundary and maximum steps remain deterministic application controls.

The offline planner makes the repository reproducible. The optional OpenAI planner demonstrates
dynamic function selection without changing the tool or safety contracts.

## Retrieval

Runbooks are indexed in a local Qdrant collection. The offline demo uses a deterministic feature-
hash embedding to avoid API keys, downloads and nondeterministic tests. This is intentionally a
deployment convenience, not a claim that feature hashing matches a production embedding model.

A production implementation could add semantic embeddings, hybrid keyword/vector retrieval,
metadata filters and reranking behind the same `RunbookStore` interface. Retrieval and generation
should continue to be evaluated separately.

## Data and tenant isolation

Synthetic run events are loaded into SQLite and queried with tenant and pipeline predicates. The
tool registry also rejects a model-generated tenant that differs from the authorized tenant.
Negative tests cover this boundary.

The demo API accepts `tenant_id` in the request and treats it as the authorized context. Production
must derive tenant scope from authenticated identity and must never trust a user- or model-supplied
tenant field by itself.

## Failure controls

| Failure | Control |
|---|---|
| Incorrect tool arguments | Strict JSON schemas plus application validation |
| Cross-tenant request | Authorized-context comparison and tenant-scoped SQL |
| Prompt injection in a runbook | Runbook text is reference data, not instructions |
| Excessive tool looping | Configurable maximum tool steps |
| LLM or API failure | Deterministic offline fallback |
| Unsupported remediation | Preview-only endpoint and mandatory human approval |
| Hallucinated diagnosis | Direct event/contract evidence and runbook citations |
| Silent regression | Versioned evaluation cases in CI |

## Main trade-offs

- **Offline determinism versus semantic quality:** feature hashing is reproducible but less semantic
  than a hosted embedding model.
- **Bounded tools versus autonomy:** three explicit tools reduce capability, ambiguity and risk.
- **SQLite versus production storage:** SQLite keeps the demo portable; production needs managed,
  access-controlled storage and workload-specific scaling.
- **Deterministic synthesis versus expressive answers:** structured rules keep outputs testable; an
  LLM summary is optional rather than trusted as the source of facts.
- **No execute endpoint versus end-to-end automation:** removing execution makes the public demo
  safer and keeps operator approval explicit.
