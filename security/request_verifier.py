from __future__ import annotations

from .agent_identity import AgentIdentity, verify_identity
from .intent_store import IntentStore


class RequestVerifier:
    def __init__(self, secrets: dict[str, bytes], intents: IntentStore) -> None:
        self.secrets = secrets
        self.intents = intents

    def verify(self, *, agent_id: str, intent_id: str, intent: str, issued_at: int, signature: str) -> tuple[bool, str]:
        secret = self.secrets.get(agent_id)
        if secret is None:
            return False, "unknown agent"

        identity = AgentIdentity(agent_id=agent_id, issued_at=issued_at, intent_id=intent_id)
        if not verify_identity(identity, signature, secret):
            return False, "invalid or expired agent signature"

        if not self.intents.matches(intent_id, agent_id, intent):
            return False, "intent does not match server-side intent state"

        return True, "verified"
