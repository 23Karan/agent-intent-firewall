import os
import requests

MCP_URL = os.getenv("MCP_URL", "http://127.0.0.1:8000/mcp")


def call_mcp_tool(agent_id: str, intent: str, tool: str, arguments: dict):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool,
            "arguments": arguments,
            "_meta": {"agent_id": agent_id, "intent": intent},
        },
    }
    response = requests.post(MCP_URL, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    print(call_mcp_tool(
        "research-agent",
        "Analyze my repository",
        "workspace.list",
        {},
    ))
