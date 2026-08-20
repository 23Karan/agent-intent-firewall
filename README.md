# Agent Intent Continuity Firewall

A live runtime security gateway for autonomous AI agents. The firewall sits between an agent and protected tools, evaluates intent and authorization before execution, blocks unsafe calls, and produces tamper-evident security evidence.

## What is live now

The project is no longer only an authorization API. It now exposes a guarded tool-execution boundary:

```text
AI Agent
   |
   | tool request
   v
+---------------------------+
| Agent Intent Firewall     |
|---------------------------|
| Identity                  |
| Policy                    |
| Intent continuity         |
| Risk evaluation           |
| Execution gate            |
| Hash-chained audit        |
+-------------+-------------+
              |
        +-----+-----+
        |           |
      ALLOW        BLOCK
        |           |
        v           v
    Real tool   No execution
```

The important property is **deny before execution**: a tool is invoked only after the gateway has authorized the request.

## Endpoints

- `GET /health` — service health and registered tools
- `POST /v1/authorize` — evaluate an action without executing it
- `POST /v1/tools/execute` — authorize and then execute a registered tool
- `GET /v1/tools` — list registered tools
- `GET /v1/audit/verify` — verify the audit hash chain

### Example tool execution

```json
{
  "agent_id": "research-agent",
  "intent": "analyze my workspace",
  "tool": "workspace.list",
  "resource": "filesystem:workspace",
  "action": "list"
}
```

A blocked request returns no tool result and records the decision in the audit chain.

## Current security controls

- Agent identity and capability boundaries
- Resource/action policy enforcement
- Intent-continuity checks
- Delegation restrictions
- Risk scoring
- Pre-execution tool gate
- Unknown-tool blocking
- SHA-256 hash-chained audit events
- Automated authorization and execution tests
- Docker deployment

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

Run tests:

```bash
pytest -q
```

Run the live client example:

```bash
python examples/live_client.py
```

## Docker

```bash
docker build -t agent-intent-firewall .
docker run --rm -p 8000:8000 agent-intent-firewall
```

## Roadmap

- [x] Runtime authorization gateway
- [x] Pre-execution tool enforcement
- [x] Intent continuity enforcement
- [x] Delegation capability limits
- [x] Hash-chained audit log
- [x] Live client example
- [ ] Persistent event store
- [ ] Real MCP adapter
- [ ] Agent-to-agent delegation protocol
- [ ] Semantic intent-drift model
- [ ] WebSocket live security dashboard
- [ ] Authentication and mTLS
- [ ] Production cloud deployment
- [ ] Red-team benchmark suite

## Safety

Use only with systems and accounts you own or are explicitly authorized to assess.
