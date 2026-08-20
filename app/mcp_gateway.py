from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .models import ToolExecutionRequest


@dataclass(frozen=True)
class MCPTool:
    name: str
    resource: str
    action: str
    handler: Callable[[dict[str, Any]], Any]


class MCPGateway:
    """Local MCP-like tool boundary.

    Tool handlers are registered here and are never called directly by an
    agent. The application must authorize the request before invoking a
    handler. This keeps the execution boundary outside the agent's trust
    boundary.
    """

    def __init__(self) -> None:
        self._tools: dict[str, MCPTool] = {}

    def register(self, tool: MCPTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def list_tools(self) -> list[dict[str, str]]:
        return [
            {"name": t.name, "resource": t.resource, "action": t.action}
            for t in self._tools.values()
        ]

    def resolve(self, request: ToolExecutionRequest) -> MCPTool:
        tool = self._tools.get(request.tool)
        if tool is None:
            raise KeyError(f"unknown tool: {request.tool}")
        if tool.resource != request.resource or tool.action != request.action:
            raise PermissionError("tool metadata does not match requested operation")
        return tool

    def execute_authorized(self, request: ToolExecutionRequest) -> Any:
        """Execute only after the caller has completed authorization."""
        tool = self.resolve(request)
        return tool.handler(request.arguments)
