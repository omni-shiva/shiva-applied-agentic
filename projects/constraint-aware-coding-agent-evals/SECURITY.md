# Security policy

## Reporting a vulnerability

Use the repository host's private vulnerability-reporting feature. Do not publish exploit details in a public issue before a fix is available.

## Sensitive material

Never submit secrets, access tokens, private repositories, personal information, or confidential evaluation artifacts. If sensitive material is committed accidentally, rotate the affected credential and purge it through the repository host's documented process before continuing.

## Execution boundary

The included candidates are authored fixtures. Extending the project to evaluate untrusted code requires a stronger sandbox, resource limits, filesystem isolation, and network controls beyond this educational implementation.

