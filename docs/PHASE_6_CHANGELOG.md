# Phase 6 — API Tooling

## Scope
- Add a bounded generic HTTP API function tool.
- Support GET, POST, PUT, PATCH and DELETE.
- Support query parameters, headers and JSON request bodies.
- Enforce URL, request-body and response-body size limits.
- Enforce a 1–30 second timeout range.
- Reject embedded URL credentials.
- Return structured HTTP responses, including structured HTTP error responses.
- Normalize transport failures through `ToolExecutionError` without exposing internal exception text.
- Register `api_request` with the root agent.
- Add unit coverage for validation, request construction, HTTP errors and transport-error normalization.

## Explicitly not included
- MCP integration
- persistent API credentials/secrets management
- OAuth flows
- API-specific adapters (Jira, GitHub, etc.)
- retries/circuit breakers
- persistent observability
- multi-agent changes
