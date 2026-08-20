from __future__ import annotations

import os
from dataclasses import dataclass

from .agent_identity import AgentIdentity, verify_identity
from .intent_store import IntentStore


@dataclass(frozen=True)
class GuardResult:
    allowed: bool
    reason: str


class RequestGuard:
    def __init__(self, intent_store: IntentStore | None = None) -> None:
        self.intent_store = intent_store or IntentStore()
        self.secret = os.environ.get("AGENT_IDENTITY_SECRET", "") .encode()

    def verify(self, agent_id: str, intent_id: str, intent: str, issued_at: int, signature: str) -> GuardResult:
        if not self.secret:
            return GuardResult(False, "server identity secret is not configured")
        identity = AgentIdentity(agent_id=agent_id, issued_at=issued_at, intent_id=intent_id)
        if not verify_identity(identity, signature, self.secret):
            return GuardResult(False, "invalid or expired agent signature")
        if not self.intent_store.matches(intent_id, agent_id, intent):
            return GuardResult(False, "intent does not match server-side intent state")
        return GuardResult(True, "authenticated intent")
