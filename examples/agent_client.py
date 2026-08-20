"""Minimal agent-side client.

The agent never calls a tool handler directly. Every tool request is sent to
Agent Intent Firewall, which makes the authorization decision before execution.
"""

import os
import requests

FIREWALL_URL = os.getenv("FIREWALL_URL", "http://127.0.0.1:8000")
AGENT_ID = os.getenv("AGENT_ID", "research-agent")


def call_tool(intent: str, tool: str, resource: str, action: str, arguments: dict):
    response = requests.post(
        f"{FIREWALL_URL}/v1/tools/execute",
        json={
            "agent_id": AGENT_ID,
            "intent": intent,
            "tool": tool,
            "resource": resource,
            "action": action,
            "arguments": arguments,
        },
        timeout=10,
    )
    response.raise_for_status()
    decision = response.json()
    if decision["decision"] != "allow":
        raise PermissionError(
            f"Firewall blocked {tool}: {decision['reasons']}"
        )
    return decision["result"]


if __name__ == "__main__":
    print(
        call_tool(
            intent="Analyze my repository",
            tool="workspace.list",
            resource="workspace",
            action="list",
            arguments={},
        )
    )
