from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class AuditEvent:
    sequence: int
    timestamp: str
    payload: dict[str, Any]
    previous_hash: str
    event_hash: str


class AuditChain:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    @property
    def last_hash(self) -> str:
        return self.events[-1].event_hash if self.events else "0" * 64

    def append(self, payload: dict[str, Any]) -> AuditEvent:
        sequence = len(self.events) + 1
        timestamp = datetime.now(timezone.utc).isoformat()
        previous_hash = self.last_hash
        canonical = json.dumps(
            {"sequence": sequence, "timestamp": timestamp, "payload": payload, "previous_hash": previous_hash},
            sort_keys=True,
            separators=(",", ":"),
        )
        event_hash = hashlib.sha256(canonical.encode()).hexdigest()
        event = AuditEvent(sequence, timestamp, payload, previous_hash, event_hash)
        self.events.append(event)
        return event

    def verify(self) -> bool:
        previous = "0" * 64
        for event in self.events:
            canonical = json.dumps(
                {"sequence": event.sequence, "timestamp": event.timestamp, "payload": event.payload, "previous_hash": event.previous_hash},
                sort_keys=True,
                separators=(",", ":"),
            )
            if event.previous_hash != previous or hashlib.sha256(canonical.encode()).hexdigest() != event.event_hash:
                return False
            previous = event.event_hash
        return True
