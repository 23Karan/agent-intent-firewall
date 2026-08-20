from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.mcp_gateway import MCPGateway

app = FastAPI(title="Agent Intent Firewall MCP Proxy")
gateway = MCPGateway()


def _tool_result(tool_name: str, arguments: dict) -> dict:
    return {"tool": tool_name, "arguments": arguments, "status": "executed"}


# Safe demonstration tools. Replace these handlers with adapters to your real
# MCP server only after authentication and resource restrictions are configured.
gateway.register(
    __import__("app.mcp_gateway", fromlist=["MCPTool"]).MCPTool(
        name="workspace.list",
        resource="workspace",
        action="list",
        handler=lambda args: _tool_result("workspace.list", args),
    )
)


def _jsonrpc_error(request_id, code: int, message: str):
    return JSONResponse({"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}})


@app.post("/mcp")
async def mcp(request: Request):
    body = await request.json()
    request_id = body.get("id")
    method = body.get("method")
    params = body.get("params") or {}

    if method == "tools/list":
        tools = gateway.list_tools()
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}

    if method != "tools/call":
        return _jsonrpc_error(request_id, -32601, "Method not supported by security proxy")

    name = params.get("name")
    arguments = params.get("arguments") or {}
    meta = params.get("_meta") or {}
    agent_id = meta.get("agent_id", "unknown-agent")
    intent = meta.get("intent")

    if not intent:
        return _jsonrpc_error(request_id, -32602, "_meta.intent is required")

    tool = next((t for t in gateway._tools.values() if t.name == name), None)
    if tool is None:
        return _jsonrpc_error(request_id, -32602, "Unknown tool")

    decision = gateway.call(
        agent_id=agent_id,
        intent=intent,
        tool_name=name,
        arguments=arguments,
    )

    if decision["decision"] != "allow":
        return _jsonrpc_error(request_id, -32001, "Tool call blocked by Agent Intent Firewall")

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "content": [{"type": "text", "text": str(decision["result"])}],
            "_meta": {"risk_score": decision["risk_score"], "reasons": decision["reasons"]},
        },
    }
