# Agent Intent Continuity Firewall

A live runtime security gateway for autonomous AI agents. It preserves user intent across multi-step execution and delegation, evaluates every tool action against policy and intent, and blocks actions that exhibit intent drift or privilege escalation.

## Why it exists

Traditional authorization asks **who can perform an action**. Autonomous agents require a second question: **is this action still consistent with the intent that authorized the workflow?**

This project places an enforcement gateway outside the agent's trust boundary. Protected tools should receive requests only after the gateway authorizes them.

## Current release

This first implementation provides a working HTTP gateway with:

- Structured agent identities and intents
- Resource/action authorization policies
- Intent-continuity checks
- Capability/delegation boundaries
- Risk scoring
- SHA-256 hash-chained audit events
- Automated tests
- Docker deployment

## Architecture

```text
User Intent
    |
    v
+------------------------------+
| Agent Intent Firewall        |
|------------------------------|
| Identity verification        |
| Intent policy                |
| Action authorization         |
| Intent continuity            |
| Risk evaluation              |
| Tamper-evident audit chain   |
+--------------+---------------+
               |
          +----+----+
          |         |
        ALLOW     BLOCK
          |         |
          v         v
      Real Tool  Security Event
```

## API

`POST /v1/authorize` evaluates an agent action.

Example request:

```json
{
  "agent_id": "research-agent",
  "intent": "analyze my repository for security vulnerabilities",
  "resource": "github:repo",
  "action": "read",
  "context": {"owner": "23Karan", "repo": "demo"}
}
```

The response contains the decision, risk score, reasons, and audit event hash.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/docs`.

## Docker

```bash
docker build -t agent-intent-firewall .
docker run --rm -p 8000:8000 agent-intent-firewall
```

## Roadmap

- [x] Runtime authorization gateway
- [x] Intent continuity enforcement
- [x] Delegation capability limits
- [x] Hash-chained audit log
- [ ] Persistent event store
- [ ] Real MCP tool adapter
- [ ] Agent-to-agent delegation protocol
- [ ] ML-based semantic intent drift scoring
- [ ] WebSocket live security dashboard
- [ ] Authentication and mTLS
- [ ] Production cloud deployment
- [ ] Red-team benchmark suite

## Safety

Use only with systems and accounts you own or are explicitly authorized to assess.
