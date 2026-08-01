# Idempotent backfill safety checklist

Define the exact tenant, pipeline, date range, expected input, write mode, and rollback boundary. Dry-run the selection and record counts first. Require an idempotency key, a bounded batch size, audit logging, and human approval. Start with a canary partition and stop automatically when error, quality, latency, or cost thresholds are breached.
