from __future__ import annotations

import time
from threading import Lock


class ReplayGuard:
    def __init__(self, ttl_seconds: int = 300) -> None:
        self.ttl = ttl_seconds
        self._seen: dict[str, float] = {}
        self._lock = Lock()

    def accept(self, request_id: str) -> bool:
        now = time.time()
        with self._lock:
            expired = [key for key, expiry in self._seen.items() if expiry <= now]
            for key in expired:
                del self._seen[key]
            if request_id in self._seen:
                return False
            self._seen[request_id] = now + self.ttl
            return True
