# Case study: synthetic notice planner

## Executive summary

This case study evaluates two fictional notice-planner implementations. Both pass the same three ordinary unit tests. The reference passes six focused runtime probes; the comparison passes two.

The key outcome is not a favorable candidate score. It is the reproducible detection of constraint violations invisible to ordinary tests.

## Scenario

A planner receives notice objects, resolves each delivery channel through an injected policy, compares optional schedules with a time snapshot, groups deliverable notices, and returns the rest as rejected.

The scenario adds six observable behaviors covering input protocols, object ownership, state integrity, time consistency, dependency boundaries, and stable ordering.

## Reference behavior

The reference takes one clock snapshot, traverses the supplied iterable once, delegates each channel decision, retains inputs unchanged, appends rejected originals directly, and naturally preserves order.

## Comparison behavior

The comparison performs a redundant preflight traversal, calls the clock inside the second loop, rewrites resolved channels on input objects, and deep-copies rejected notices. It still passes the ordinary tests because those tests use reusable lists, a fixed clock, value equality, and canonical outputs.

## Deterministic outcome

| Dimension | Reference | Comparison |
|---|---:|---:|
| Functional correctness | PASS | PASS |
| Input consumed once | PASS | FAIL |
| Rejected identity preserved | PASS | FAIL |
| Inputs unchanged | PASS | FAIL |
| Clock snapshotted once | PASS | FAIL |
| Policy delegated | PASS | PASS |
| Rejection order preserved | PASS | PASS |
| Overall | PASS | FAIL |

## Engineering lessons

- Correct outputs can hide unsafe implementation behavior.
- Focused probes should target meaningfully different failure categories.
- Accepted examples need isolated adversarial counterexamples.
- A failed probe should not erase evidence from later probes.
- Reproducible negative results are more valuable than cosmetically favorable scores.
- Public portfolio work needs an explicit provenance boundary.

## Limitations

The scenario, candidates, and results are deliberately small and synthetic. They demonstrate an evaluation architecture, not real-world model performance.
