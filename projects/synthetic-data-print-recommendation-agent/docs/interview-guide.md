# Interview guide

## 90-second explanation

I built an independent synthetic-data and print-recommendation agent around a data-scarcity
problem. The system first measures missing document segments, then generates controlled variations
at 1x, 10x and 100x scale and engineers transparent document characteristics. A local bounded agent
recommends print settings with confidence, evidence IDs and a human-review gate. The most important
part is the evaluation boundary: the generator never sees the independent holdout IDs or labels, and
I measure coverage, diversity, duplicates, exact accuracy, rare-group performance and saturation.
The service returns recommendation JSON but cannot execute printing.

## Why this is agentic

The service makes a bounded decision from engineered context, retrieves labelled evidence, produces
a structured recommendation and routes uncertain cases to human review. It is deliberately less
autonomous than an open-ended agent because the domain has explicit settings and safety boundaries.

## Likely questions

### Why can 100x synthetic data be worse than 10x?

It may repeat the same feature patterns, amplify the generator's assumptions, distort the real
distribution or reinforce incorrect synthetic labels. Volume must be assessed with diversity and
independent holdout metrics.

### How do you prevent leakage?

Seed, generated and holdout document IDs are separated. The holdout is loaded only by evaluation,
never by generation or fitting, and code raises an error if seed and holdout IDs overlap.

### Is the holdout truly real?

No. In this public portfolio it is a separately authored synthetic holdout. It demonstrates the
evaluation design, not real-world model validity. Production needs domain-expert labels and actual
print-quality outcomes.

### Why not use an LLM?

The core risk is data quality and synthetic bias, so a deterministic local model is easier to test
and explain. An LLM could later extract features or explain results, but its output would still need
schemas, evaluation and human review.

### Where is human validation?

The code implements the review boundary and review queue conditions. No real human validation is
claimed. Actual domain experts would approve or correct labels before production training.

## Three failure cases

1. Synthetic variations are numerically different but semantically repetitive.
2. Rare document categories receive high overall accuracy but poor subgroup accuracy.
3. A low-confidence recommendation is used without printer-specific expert review.

## Capability boundary

Describe this as an end-to-end portfolio implementation of synthetic-data generation, feature
engineering, recommendation, structured APIs and evaluation. Do not describe it as an employer
system, a production printer platform or evidence of real user outcomes.
