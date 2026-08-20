# Security Policy

## Production requirements

- Run behind TLS and an authenticated reverse proxy.
- Store `AGENT_IDENTITY_SECRET` in a managed secret store; never commit it.
- Use durable shared storage for intent and replay state when multiple replicas run.
- Keep the MCP upstream on a private network and allow-list destinations.
- Apply request-size, timeout, and rate limits at the edge.
- Emit audit events to durable append-only storage.
- Rotate signing secrets using a key identifier and overlap window.
- Fail closed when authentication, intent state, policy, or upstream authorization is unavailable.

## Threat model

The firewall is intended to resist forged agent identity, intent tampering, replay, unauthorized tool selection, and tool-chain privilege escalation. It does not make an untrusted upstream MCP server safe by itself.

## Release gate

A release is production-ready only after unit, integration, protocol, security, dependency, container, and end-to-end tests pass in CI.
