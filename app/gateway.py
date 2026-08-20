from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from threading import Lock
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Agent Intent Continuity Firewall", version="0.1.0")


@dataclass
class AuditEvent:
    timestamp: float
    agent_id: str
    action: str
    resource: str
    decision: str
    reason: str
    risk: int
    previous_hash: str
    event_hash: str


class ActionRequest(BaseModel):
    agent_id: str = Field(min_length=1)
    intent: str = Field(min_length=1)
    action: str = Field(min_length=1)
    resource: str = Field(min_length=1)
    context: dict[str, Any] = Field(default_factory=dict)


class Gateway:
    def __init__(self) -> None:
        self._lock = Lock()
        self._events: list[AuditEvent] = []
        self._intent: dict[str, str] = {}

    def evaluate(self, request: ActionRequest) -> AuditEvent:
        with self._lock:
            previous_intent = self._intent.get(request.agent_id)
            risk = 0
            reasons: list[str] = []

            if previous_intent is None:
                self._intent[request.agent_id] = request.intent
            elif request.intent.strip().lower() != previous_intent.strip().lower():
                risk += 70
                reasons.append("intent drift detected")

            # Explicit high-impact operations require an approved context flag.
            dangerous = {"delete", "drop", "shutdown", "export", "credential_access"}
            if request.action.lower() in dangerous and not request.context.get("approved"):
                risk += 25
                reasons.append("high-impact action is not approved")

            # A simple resource boundary for the initial production-oriented gateway.
            allowed_prefix = request.context.get("allowed_resource_prefix")
            if allowed_prefix and not request.resource.startswith(str(allowed_prefix)):
                risk += 30
                reasons.append("resource is outside delegated boundary")

            risk = min(risk, 100)
            decision = "BLOCK" if risk >= 50 else "ALLOW"
            reason = "; ".join(reasons) if reasons else "action is consistent with current intent and policy"

            previous_hash = self._events[-1].event_hash if self._events else "GENESIS"
            payload = {
                "timestamp": time.time(),
                "agent_id": request.agent_id,
                "action": request.action,
                "resource": request.resource,
                "decision": decision,
                "reason": reason,
                "risk": risk,
                "previous_hash": previous_hash,
            }
            event_hash = hashlib.sha256(
                json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()

            event = AuditEvent(**payload, event_hash=event_hash)
            self._events.append(event)
            return event

    def events(self) -> list[dict[str, Any]]:
        with self._lock:
            return [asdict(event) for event in self._events]


firewall = Gateway()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "agent-intent-firewall"}


@app.post("/v1/authorize")
def authorize(request: ActionRequest) -> dict[str, Any]:
    event = firewall.evaluate(request)
    return {"decision": event.decision, "risk": event.risk, "reason": event.reason, "audit_hash": event.event_hash}


@app.get("/v1/audit")
def audit() -> dict[str, Any]:
    return {"count": len(firewall.events()), "events": firewall.events()}
