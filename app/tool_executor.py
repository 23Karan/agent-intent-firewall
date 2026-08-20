from __future__ import annotations

from typing import Any, Callable


Tool = Callable[[dict[str, Any]], Any]


class ToolRegistry:
    """Small execution boundary: registered tools run only after authorization."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, name: str, tool: Tool) -> None:
        if not name or name in self._tools:
            raise ValueError("tool name must be unique and non-empty")
        self._tools[name] = tool

    def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        tool = self._tools.get(name)
        if tool is None:
            raise KeyError(f"unknown tool: {name}")
        return tool(arguments)

    def names(self) -> list[str]:
        return sorted(self._tools)


tools = ToolRegistry()


def echo_tool(arguments: dict[str, Any]) -> dict[str, Any]:
    return {"echo": arguments.get("message", "")}


def list_workspace_tool(arguments: dict[str, Any]) -> dict[str, Any]:
    # Safe built-in tool for integration testing; it does not touch the host filesystem.
    return {"items": ["README.md", "src/", "tests/"]}


tools.register("echo", echo_tool)
tools.register("workspace.list", list_workspace_tool)
