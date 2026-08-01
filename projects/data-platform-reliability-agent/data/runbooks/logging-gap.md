# Missing diagnostic and correlation logs

Every log event should carry tenant-safe request, pipeline, run, and correlation identifiers plus stage, status, duration, and sanitized error context. Standardize the schema before migrating log platforms. Reject secrets and raw sensitive payloads at the logger boundary. Missing required diagnostic fields should fail an observability-quality check.
