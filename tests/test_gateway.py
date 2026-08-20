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


def test_audit_chain_is_valid():
    assert audit_chain.verify()
