# Privacy model

This project is designed for public release from its isolated directory inside
the `shiva-applied-agentic` portfolio repository.

## Included

- Newly authored evaluation code
- Fictional task text and Python fixtures
- Authored synthetic candidates and traces
- Deterministic generated results
- Public documentation and tests

## Excluded

- Employer, client, reviewer, or vendor identities
- Real repositories, issues, task identifiers, prompts, patches, or tests
- Private model outputs or hidden reasoning
- Credentials, account metadata, costs, comments, logs, or screenshots
- Local machine paths, personal contact details, or private hashes
- Copied workflow documents or internal operating procedures

The scanner rejects common sensitive patterns and accepts an optional private denylist through `PUBLIC_RELEASE_DENYLIST`. Keep that denylist outside the repository.

Before publishing, inspect the full Git diff and confirm that the release scanner and test suite pass from a clean checkout.
