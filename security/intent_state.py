from __future__ import annotations

from dataclasses import dataclass
from threading import RLock


@dataclass(frozen=True)
class IntentState:
    agent_id: str
    intent_id: str
    original_intent: str


class IntentRegistry:
    def __init__(self) -> None:
        self._states: dict[tuple[str, str], IntentState] = {}
        self._lock = RLock()

    def establish(self, agent_id: str, intent_id: str, original_intent: str) -> IntentState:
        state = IntentState(agent_id, intent_id, original_intent)
        with self._lock:
            self._states.setdefault((agent_id, intent_id), state)
            return self._states[(agent_id, intent_id)]

    def get(self, agent_id: str, intent_id: str) -> IntentState | None:
        with self._lock:
            return self._states.get((agent_id, intent_id))

    def matches(self, agent_id: str, intent_id: str, claimed_intent: str) -> bool:
        state = self.get(agent_id, intent_id)
        return state is not None and state.original_intent == claimed_intent
