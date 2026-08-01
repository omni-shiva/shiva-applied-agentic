# Upstream readiness and late arrival

Use a data-readiness signal rather than a fixed schedule when the downstream pipeline depends on an upstream snapshot. Retries must use bounded exponential backoff and an idempotency key. Distinguish an empty valid dataset from data that has not arrived. Route exhausted retries to an operator-visible queue instead of starting an unbounded retry loop.
