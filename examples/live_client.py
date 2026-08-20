"""Minimal client showing the firewall as an execution boundary."""

import json
from urllib.request import Request, urlopen


BASE = "http://127.0.0.1:8000"


def call(payload: dict) -> dict:
    request = Request(
        f"{BASE}/v1/tools/execute",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request) as response:
        return json.loads(response.read())


if __name__ == "__main__":
    allowed = call(
        {
            "agent_id": "research-agent",
            "intent": "analyze my workspace",
            "tool": "workspace.list",
            "resource": "filesystem:workspace",
            "action": "list",
        }
    )
    print("ALLOWED TOOL:", json.dumps(allowed, indent=2))

    blocked = call(
        {
            "agent_id": "research-agent",
            "intent": "analyze my GitHub repository",
            "tool": "workspace.list",
            "resource": "filesystem:workspace",
            "action": "delete",
        }
    )
    print("BLOCKED TOOL:", json.dumps(blocked, indent=2))
