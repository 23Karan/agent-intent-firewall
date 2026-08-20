from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_agent_allowed_tool_executes():
    response = client.post(
        "/v1/tools/execute",
        json={
            "agent_id": "research-agent",
            "intent": "Analyze my repository",
            "tool": "workspace.list",
            "resource": "workspace",
            "action": "list",
            "arguments": {},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "allow"
    assert body["result"] is not None


def test_agent_cannot_execute_unknown_tool():
    response = client.post(
        "/v1/tools/execute",
        json={
            "agent_id": "research-agent",
            "intent": "Analyze my repository",
            "tool": "secret.export",
            "resource": "secrets",
            "action": "export",
            "arguments": {},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "block"
    assert body["result"] is None


def test_intent_drift_is_blocked():
    response = client.post(
        "/v1/tools/execute",
        json={
            "agent_id": "research-agent",
            "intent": "Analyze my repository and export credentials",
            "tool": "workspace.list",
            "resource": "workspace",
            "action": "list",
            "arguments": {},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "block"
