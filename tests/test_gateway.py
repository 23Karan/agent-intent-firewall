from fastapi.testclient import TestClient

from app.main import app, audit_chain

client = TestClient(app)


def test_allowed_action():
    response = client.post(
        "/v1/authorize",
        json={
            "agent_id": "research-agent",
            "intent": "analyze my GitHub repository for security vulnerabilities",
            "resource": "github:repo",
            "action": "read",
        },
    )
    assert response.status_code == 200
    assert response.json()["decision"] == "allow"


def test_intent_drift_is_blocked():
    response = client.post(
        "/v1/authorize",
        json={
            "agent_id": "research-agent",
            "intent": "analyze my GitHub repository for security vulnerabilities",
            "resource": "database:production",
            "action": "export",
        },
    )
    assert response.status_code == 200
    assert response.json()["decision"] == "block"


def test_unknown_agent_is_blocked():
    response = client.post(
        "/v1/authorize",
        json={
            "agent_id": "unknown-agent",
            "intent": "read repository",
            "resource": "github:repo",
            "action": "read",
        },
    )
    assert response.status_code == 200
    assert response.json()["decision"] == "block"


def test_allowed_tool_executes_only_after_authorization():
    response = client.post(
        "/v1/tools/execute",
        json={
            "agent_id": "research-agent",
            "intent": "analyze my workspace",
            "tool": "workspace.list",
            "resource": "filesystem:workspace",
            "action": "list",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "allow"
    assert body["result"]["items"]


def test_unauthorized_tool_never_executes():
    response = client.post(
        "/v1/tools/execute",
        json={
            "agent_id": "report-agent",
            "intent": "write the report to my workspace",
            "tool": "echo",
            "resource": "filesystem:workspace",
            "action": "execute",
            "arguments": {"message": "should not run"},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "block"
    assert body["result"] is None


def test_unknown_tool_is_blocked():
    response = client.post(
        "/v1/tools/execute",
        json={
            "agent_id": "research-agent",
            "intent": "analyze my workspace",
            "tool": "unknown.tool",
            "resource": "filesystem:workspace",
            "action": "list",
        },
    )
    assert response.status_code == 200
    assert response.json()["decision"] == "block"


def test_audit_chain_is_valid():
    assert audit_chain.verify()
