# Expired workload credentials

Use workload identity or an approved secret manager. Never place credentials in source code, prompts, tool outputs, or logs. Confirm the scope and expiry, rotate through the authorized workflow, and validate the new credential in a non-production check. Add expiry monitoring so the next rotation occurs before the processing window.
