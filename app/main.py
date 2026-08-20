from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .audit import AuditChain
from .models import AuthorizationRequest, AuthorizationResponse
from .policy import POLICIES, evaluate, intent_consistent

app = FastAPI(
    title="Agent Intent Continuity Firewall",
    version="0.1.0",
    description="Runtime authorization and intent-continuity enforcement for autonomous AI agents.",
)

audit_chain = AuditChain()


@app.get("/health")
def health() -> dict[str, object]:
    return {"status": "ok", "audit_chain_valid": audit_chain.verify(), "agents": len(POLICIES)}


@app.post("/v1/authorize", response_model=AuthorizationResponse)
def authorize(request: AuthorizationRequest) -> AuthorizationResponse:
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

    event = audit_chain.append(
        {
            "agent_id": request.agent_id,
            "intent": request.intent,
            "resource": request.resource,
            "action": request.action,
            "decision": decision,
            "risk_score": risk,
            "reasons": reasons,
        }
    )

    return AuthorizationResponse(
        decision=decision,
        risk_score=risk,
        reasons=reasons,
        audit_hash=event.event_hash,
    )


@app.get("/v1/audit/verify")
def verify_audit() -> JSONResponse:
    return JSONResponse({"valid": audit_chain.verify(), "events": len(audit_chain.events)})
