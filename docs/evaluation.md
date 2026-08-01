# Evaluation design

The evaluation harness uses versioned JSON Lines cases so every prompt, router, tool or guardrail
change can be tested against the same inputs.

## Case fields

- `case_id`: stable identifier for regression tracking.
- `tenant_id` and `pipeline_id`: synthetic authorized scope.
- `question`: interview-style incident request.
- `expected_tool`: minimum tool expected in the trace.
- `expected_error_code`: incident signature expected in the diagnosis.
- `risk_category`: identifies requests that imply state-changing recovery.

## Metrics

- **Tool-selection accuracy:** expected read tool appears in the trace.
- **Evidence-grounded rate:** direct event/contract evidence and at least one citation are present.
- **Approval-guard rate:** destructive-action cases require approval and execute nothing.
- **Pass rate:** tool, signature, grounding and applicable guard checks all pass.

These are deterministic gates, not a complete measure of diagnostic quality. A production suite
would add retrieval recall at k, citation accuracy, human-reviewed correctness, refusal accuracy,
latency, token usage, cost, consistency and failure-recovery tests. An LLM judge may assist review,
but should not be the only quality signal.

## Run locally

```bash
reliability-agent-eval
pytest
```

Add new cases before changing behavior so a bug fix produces an explicit regression test.
