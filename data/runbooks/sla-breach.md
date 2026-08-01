# SLA breach and Spark performance triage

Compare the failing run with the last healthy baseline: input volume, partition sizes, shuffle volume, skew, spill, join strategy, caching, and cluster saturation. Change one variable at a time. Prefer a canary run before scaling resources broadly. Capture the runtime and cost effect so an optimization is not accepted on latency alone.
