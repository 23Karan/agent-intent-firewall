from typing import Any, Literal
from pydantic import BaseModel, Field


Decision = Literal["allow", "block"]


class AuthorizationRequest(BaseModel):
    agent_id: str = Field(min_length=1, max_length=128)
    intent: str = Field(min_length=1, max_length=1000)
    resource: str = Field(min_length=1, max_length=500)
    action: str = Field(min_length=1, max_length=100)
    context: dict[str, Any] = Field(default_factory=dict)
    delegated_by: str | None = None


class AuthorizationResponse(BaseModel):
    decision: Decision
    risk_score: int = Field(ge=0, le=100)
    reasons: list[str]
    audit_hash: str


class AgentPolicy(BaseModel):
    allowed_resources: set[str] = Field(default_factory=set)
    allowed_actions: set[str] = Field(default_factory=set)
    max_risk: int = Field(default=60, ge=0, le=100)
    delegation_allowed: bool = False
