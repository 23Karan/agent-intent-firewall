from dataclasses import dataclass
from threading import Lock


@dataclass(frozen=True)
class IntentRecord:
    intent_id: str
    agent_id: str
    intent: str


class IntentStore:
    """In-memory reference implementation; production should use durable storage."""

    def __init__(self) -> None:
        self._records: dict[str, IntentRecord] = {}
        self._lock = Lock()

    def establish(self, record: IntentRecord) -> None:
        with self._lock:
            existing = self._records.get(record.intent_id)
            if existing and existing != record:
                raise ValueError("intent_id is immutable")
            self._records[record.intent_id] = record

    def get(self, intent_id: str) -> IntentRecord | None:
        with self._lock:
            return self._records.get(intent_id)

    def matches(self, intent_id: str, agent_id: str, intent: str) -> bool:
        record = self.get(intent_id)
        return bool(record and record.agent_id == agent_id and record.intent == intent)
