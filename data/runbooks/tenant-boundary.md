# Tenant isolation for diagnostic tools

Derive tenant scope from the authenticated context, not from model-generated arguments. Every SQL query and vector search filter must apply the authorized tenant before retrieval. Reject a tool call when its tenant argument differs from the authenticated scope. Include cross-tenant negative tests and avoid returning hidden record counts that could leak another tenant's existence.
