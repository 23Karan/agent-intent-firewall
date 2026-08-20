from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .audit import AuditChain
from .mcp_gateway import MCPGateway, MCPTool
from .models import (
    AuthorizationRequest,
    AuthorizationResponse,
    ToolExecutionRequest,
    ToolExecutionResponse,
)
from .policy import POLICIES, evaluate, intent_consistent
from .tool_executor import echo_tool, list_workspace_tool, tools

app = FastAPI(
    title="Agent Intent Continuity Firewall",
    version="0.3.0",
    description="Runtime authorization and intent-continuity enforcement for autonomous AI agents.",
)

audit_chain = AuditChain()
mcp = MCPGateway()
mcp.register(MCPTool("echo", "tool:echo", "invoke", echo_tool))
mcp.register(MCPTool("workspace.list", "workspace", "list", list_workspace_tool))


def _authorize(request: AuthorizationRequest) -> tuple[str, int, list[str]]:
    risk, reasons = evaluate(request)
    consistent, continuity_reason = intent_consistent(request)

    if not consistent:
        risk = min(100, risk + 35)
        reasons.append(continuity_reason or "intent continuity failure")

    policy = POLICIES.get(request.agent_id)
    if policy and risk > policy.max_risk:
        reasons.append(f"risk score {risk} exceeds policy threshold {policy.max_risk}")

    decision = "allow" if policy and consistent and risk <= policy.max_risk else "block"
    if not reasons and decision == "allow":
        reasons.append("action satisfies identity, capability, policy, and intent-continuity checks")
    return decision, risk, reasons


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "audit_chain_valid": audit_chain.verify(),
        "agents": len(POLICIES),
        "tools": tools.names(),
        "mcp_gateway": True,
    }


@app.post("/v1/authorize", response_model=AuthorizationResponse)
def authorize(request: AuthorizationRequest) -> AuthorizationResponse:
    decision, risk, reasons = _authorize(request)
    event = audit_chain.append({
        "type": "authorization", "agent_id": request.agent_id,
        "intent": request.intent, "resource": request.resource,
        "action": request.action, "decision": decision,
        "risk_score": risk, "reasons": reasons,
    })
    return AuthorizationResponse(decision=decision, risk_score=risk, reasons=reasons, audit_hash=event.event_hash)


@app.post("/v1/tools/execute", response_model=ToolExecutionResponse)
def execute_tool(request: ToolExecutionRequest) -> ToolExecutionResponse:
    authorization = AuthorizationRequest(
        agent_id=request.agent_id,
        intent=request.intent,
        resource=request.resource,
        action=request.action,
        delegated_by=request.delegated_by,
        context={"tool": request.tool},
    )
    decision, risk, reasons = _authorize(authorization)
    result = None
    if decision == "allow":
        try:
            result = tools.execute(request.tool, request.arguments)
        except KeyError as exc:
            decision, risk = "block", max(risk, 80)
            reasons.append(str(exc))
        except Exception:
            decision, risk = "block", 100
            reasons.append("tool execution failed safely")

    event = audit_chain.append({
        "type": "tool_execution", "agent_id": request.agent_id,
        "intent": request.intent, "tool": request.tool,
        "resource": request.resource, "action": request.action,
        "decision": decision, "risk_score": risk, "reasons": reasons,
    })
    return ToolExecutionResponse(decision=decision, risk_score=risk, result=result, reasons=reasons, audit_hash=event.event_hash)


@app.post("/v1/mcp/call")
def mcp_call(request: ToolExecutionRequest) -> dict[str, object]:
    """MCP-style endpoint: tool resolution and authorization happen before handler execution."""
    try:
        response = mcp.execute(request)
    except (KeyError, PermissionError) as exc:
        response = {"decision": "block", "risk_score": 100, "reasons": [str(exc)], "result": None}

    event = audit_chain.append({
        "type": "mcp_tool_call", "agent_id": request.agent_id,
        "intent": request.intent, "tool": request.tool,
        "resource": request.resource, "action": request.action,
        "decision": response["decision"], "risk_score": response["risk_score"],
        "reasons": response["reasons"],
    })
    response["audit_hash"] = event.event_hash
    return response


@app.get("/v1/tools")
def list_tools() -> dict[str, object]:
    return {"tools": tools.names(), "mcp": mcp.list_tools()}


@app.get("/v1/audit/verify")
def verify_audit() -> JSONResponse:
    return JSONResponse({"valid": audit_chain.verify(), "events": len(audit_chain.events)})
