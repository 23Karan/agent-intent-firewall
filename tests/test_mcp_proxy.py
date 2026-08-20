from fastapi.testclient import TestClient

from mcp_proxy.server import app

client = TestClient(app)


def rpc(params):
    return client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": params})


def test_mcp_call_requires_intent():
    response = rpc({"name": "workspace.list", "arguments": {}, "_meta": {"agent_id": "a"}})
    assert response.status_code == 200
    assert response.json()["error"]["code"] == -32602


def test_mcp_unknown_tool_is_blocked():
    response = rpc({"name": "secret.dump", "arguments": {}, "_meta": {"agent_id": "a", "intent": "Analyze repository"}})
    assert response.json()["error"]["code"] == -32602


def test_mcp_tool_call_is_authorized_before_execution():
    response = rpc({"name": "workspace.list", "arguments": {}, "_meta": {"agent_id": "a", "intent": "Analyze repository"}})
    assert response.json()["result"]["_meta"]["risk_score"] <= 60
