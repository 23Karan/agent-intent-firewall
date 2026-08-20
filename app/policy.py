from __future__ import annotations

from .models import AgentPolicy, AuthorizationRequest


POLICIES: dict[str, AgentPolicy] = {
    "research-agent": AgentPolicy(
        allowed_resources={"github:repo", "filesystem:workspace"},
        allowed_actions={"read", "analyze", "list"},
        max_risk=55,
        delegation_allowed=True,
    ),
    "report-agent": AgentPolicy(
        allowed_resources={"filesystem:workspace"},
        allowed_actions={"read", "write"},
        max_risk=45,
        delegation_allowed=False,
    ),
}


def evaluate(request: AuthorizationRequest) -> tuple[int, list[str]]:
    policy = POLICIES.get(request.agent_id)
    if policy is None:
        return 100, ["unknown agent identity"]

    reasons: list[str] = []
    risk = 0

    if request.resource not in policy.allowed_resources:
        risk += 55
        reasons.append("resource is outside the agent capability boundary")

    if request.action not in policy.allowed_actions:
        risk += 35
        reasons.append("action is not authorized for this agent")

    if request.delegated_by and not policy.delegation_allowed:
        risk += 25
        reasons.append("delegation is disabled for this agent")

    # High-impact verbs receive an additional runtime penalty.
    if request.action.lower() in {"delete", "execute", "export", "admin", "write"}:
        risk += 15
        reasons.append("high-impact action requires elevated scrutiny")

    return min(risk, 100), reasons


def intent_consistent(request: AuthorizationRequest) -> tuple[bool, str | None]:
    text = request.intent.lower()
    action = request.action.lower()
    resource = request.resource.lower()

    # First defensive continuity rule: destructive or privileged actions must be
    # explicitly represented in the original intent.
    high_impact = {"delete", "execute", "export", "admin"}
    if action in high_impact and not any(word in text for word in high_impact):
        return False, "action is not semantically represented by the declared intent"

    if "github" in resource and "github" not in text and "repository" not in text and "repo" not in text:
        return False, "resource is not connected to the declared intent"

    return True, None
