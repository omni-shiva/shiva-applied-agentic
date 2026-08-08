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

## Current deterministic regression metrics

- **Required-tool trace rate:** expected read tool appears in the final trace. Event and runbook
  lookups are baseline post-conditions added when absent, so this is not pure planner-selection accuracy.
- **Evidence-present rate:** direct event/contract evidence and at least one citation are non-empty.
  It does not measure citation correctness, relevance or faithfulness.
- **Approval-guard rate:** destructive-action cases require approval and execute nothing.
- **Pass rate:** tool, signature, grounding and applicable guard checks all pass.

The committed suite runs the deterministic offline planner. It does not test the optional OpenAI
planner, prompts, malformed model tool calls or LLM response quality. These are application-regression
gates, not a complete measure of diagnostic or retrieval quality. A production suite
would add retrieval recall at k, citation accuracy, human-reviewed correctness, refusal accuracy,
latency, token usage, cost, consistency and failure-recovery tests. An LLM judge may assist review,
but should not be the only quality signal.

## Run locally

```bash
reliability-agent-eval
pytest
```

Add new cases before changing behavior so a bug fix produces an explicit regression test.
