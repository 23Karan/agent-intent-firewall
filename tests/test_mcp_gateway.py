import pytest

from app.mcp_gateway import MCPGateway, MCPTool
from app.mcp_server import build_gateway
from app.models import ToolExecutionRequest


def test_registered_tools_are_visible():
    tools = build_gateway().list_tools()
    assert {tool["name"] for tool in tools} == {
        "repository.read",
        "dependency.scan",
        "report.generate",
    }


def test_authorized_tool_can_execute():
    gateway = build_gateway()
    request = ToolExecutionRequest(
        agent_id="research-agent",
        intent="Analyze my GitHub repository",
        tool="repository.read",
        resource="github",
        action="read",
        arguments={"repository": "23Karan/example"},
    )
    result = gateway.execute_authorized(request)
    assert result["status"] == "ok"


def test_unknown_tool_never_executes():
    gateway = build_gateway()
    request = ToolExecutionRequest(
        agent_id="research-agent",
        intent="Analyze my GitHub repository",
        tool="secrets.export",
        resource="secrets",
        action="export",
    )
    with pytest.raises(KeyError):
        gateway.execute_authorized(request)


def test_tool_metadata_mismatch_is_rejected():
    gateway = build_gateway()
    request = ToolExecutionRequest(
        agent_id="research-agent",
        intent="Analyze my GitHub repository",
        tool="repository.read",
        resource="secrets",
        action="export",
    )
    with pytest.raises(PermissionError):
        gateway.execute_authorized(request)


def test_duplicate_registration_is_rejected():
    gateway = MCPGateway()
    gateway.register(MCPTool("demo", "demo", "read", lambda _: {"ok": True}))
    with pytest.raises(ValueError):
        gateway.register(MCPTool("demo", "demo", "read", lambda _: {"ok": True}))
