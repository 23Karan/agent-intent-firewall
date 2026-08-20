# Production Security Requirements

This project must not be exposed directly to the public internet without an authenticated reverse proxy, TLS, rate limiting, and secret management.

## Required before production

- Set `AGENT_IDENTITY_SECRET` through a secret manager; never commit it.
- Use TLS for agent-to-firewall and firewall-to-upstream connections.
- Configure an authenticated upstream MCP endpoint.
- Persist intent state and audit events in a transactional datastore.
- Apply request-size and timeout limits.
- Run the service as a non-root user with least-privilege network access.
- Restrict outbound network access to explicitly approved MCP upstreams.
- Enable structured logs and security-event monitoring.
- Rotate signing secrets and support key identifiers before multi-tenant deployment.
- Run the security and integration test suites in CI before release.

The repository's example configuration contains placeholders only. A successful local run is not evidence of production readiness.
