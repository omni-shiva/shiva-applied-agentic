# Methodology

## Evaluation question

For each authored candidate, answer two questions independently:

1. Does the implementation return the expected product values?
2. Does it preserve each declared runtime behavior?

A run fully passes only when both answers are yes.

## Scenario preparation

The synthetic example contains a problem statement, behavior constraints, a starter fixture, ordinary tests, reference evidence, isolated probe fixtures, and candidate artifacts.

Validation fails closed when required files are absent, scenario identifiers disagree, paths escape the example, evidence keys disagree, candidate changes exceed the allowed file set, or the reference diff is stale.

## Probe validation

Every probe is exercised against:

- one or more accepted implementations; and
- one or more single-fault adversarial implementations.

The validator runs every probe against each adversarial fixture and requires exactly one failure. This directly checks fixture isolation rather than inferring it from labels. The time probe judges behavior across controlled real-datetime snapshots, while accepted variants cover direct, inverse, arithmetic, and timestamp-based comparisons. Another accepted variant performs an allowed extra policy lookup while still routing only by the returned value. The validator also checks declared functional-test outcomes. A deliberately incomplete candidate fails the ordinary tests while passing the iteration, identity, and ordering probes. A second candidate duplicates original rejection objects, fails functional tests, and still passes identity compliance. Together they guard against syntax and correctness coupling.

## Functional verification

Each candidate is materialized into a temporary workspace and receives the same ordinary test suite. The tests focus on returned product values and avoid checking the six extra runtime behaviors.

## Constraint grading

Every behavior probe runs independently against a fresh import of the candidate package. Exceptions become failed judgments with evidence instead of aborting the complete grade.

## Analysis

The analyzer reports functional pass rate, full-run pass rate, per-run constraint compliance, and compliance separation. Correctness and compliance are never averaged into one opaque number.

## Reproducibility

The zero-install route runs without network access. Generated reports come from checked-in synthetic artifacts. CI verifies the source scan and confirms that `MANIFEST.sha256` matches the current publishable file set.
