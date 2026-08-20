from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class AgentIdentity:
    agent_id: str
    issued_at: int
    intent_id: str

    def canonical(self) -> bytes:
        return json.dumps(
            {"agent_id": self.agent_id, "issued_at": self.issued_at, "intent_id": self.intent_id},
            sort_keys=True,
            separators=(",", ":"),
        ).encode()


def sign_identity(identity: AgentIdentity, secret: bytes) -> str:
    signature = hmac.new(secret, identity.canonical(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(signature).decode().rstrip("=")


def verify_identity(identity: AgentIdentity, signature: str, secret: bytes, max_age: int = 300) -> bool:
    if abs(int(time.time()) - identity.issued_at) > max_age:
        return False
    expected = sign_identity(identity, secret)
    return hmac.compare_digest(expected, signature)
