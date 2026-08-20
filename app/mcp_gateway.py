from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .models import AuthorizationRequest, ToolExecutionRequest
from .policy import POLICIES, evaluate, intent_consistent


@dataclass(frozen=True)
class MCPTool:
    name: str
    resource: str
    action: str
    handler: Callable[[dict[str, Any]], Any]


class MCPGateway:
    """MCP-style execution boundary with mandatory pre-execution authorization."""

    def __init__(self) -> None:
        self._tools: dict[str, MCPTool] = {}

    def register(self, tool: MCPTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def list_tools(self) -> list[dict[str, str]]:
        return [{"name": t.name, "resource": t.resource, "action": t.action} for t in self._tools.values()]

    def resolve(self, request: ToolExecutionRequest) -> MCPTool:
        tool = self._tools.get(request.tool)
        if tool is None:
            raise KeyError(f"unknown tool: {request.tool}")
        if tool.resource != request.resource or tool.action != request.action:
            raise PermissionError("tool metadata does not match requested operation")
        return tool

    def authorize(self, request: ToolExecutionRequest) -> tuple[str, int, list[str]]:
        auth = AuthorizationRequest(agent_id=request.agent_id, intent=request.intent, resource=request.resource, action=request.action, delegated_by=request.delegated_by, context={"mcp_tool": request.tool})
        risk, reasons = evaluate(auth)
        consistent, continuity_reason = intent_consistent(auth)
        if not consistent:
            risk = min(100, risk + 35)
            reasons.append(continuity_reason or "intent continuity failure")
        policy = POLICIES.get(request.agent_id)
        if policy and risk > policy.max_risk:
            reasons.append(f"risk score {risk} exceeds policy threshold {policy.max_risk}")
        decision = "allow" if policy and consistent and risk <= policy.max_risk else "block"
        if decision == "allow" and not reasons:
            reasons.append("MCP action satisfies authorization and intent continuity")
        return decision, risk, reasons

    def execute(self, request: ToolExecutionRequest) -> dict[str, Any]:
        tool = self.resolve(request)
        decision, risk, reasons = self.authorize(request)
        if decision != "allow":
            return {"decision": decision, "risk_score": risk, "reasons": reasons, "result": None}
        try:
            return {"decision": "allow", "risk_score": risk, "reasons": reasons, "result": tool.handler(request.arguments)}
        except Exception:
            return {"decision": "block", "risk_score": 100, "reasons": ["tool execution failed safely"], "result": None}

    def execute_authorized(self, request: ToolExecutionRequest) -> dict[str, Any]:
        tool = self.resolve(request)
        decision, risk, reasons = self.authorize(request)
        if decision != "allow":
            return {"status": "blocked", "decision": decision, "risk_score": risk, "reasons": reasons, "result": None}
        return {"status": "ok", "decision": "allow", "risk_score": risk, "reasons": reasons, "result": tool.handler(request.arguments)}

    def call(self, *, agent_id: str, intent: str, tool_name: str, arguments: dict[str, Any], delegated_by: str | None = None) -> dict[str, Any]:
        tool = self._tools.get(tool_name)
        if tool is None:
            return {"decision": "block", "risk_score": 100, "reasons": [f"unknown MCP tool: {tool_name}"], "result": None}
        request = ToolExecutionRequest(agent_id=agent_id, intent=intent, tool=tool_name, resource=tool.resource, action=tool.action, arguments=arguments, delegated_by=delegated_by)
        return self.execute(request)
