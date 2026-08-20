from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock


class RateLimiter:
    def __init__(self, limit: int = 60, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str) -> bool:
        now = time.time()
        cutoff = now - self.window
        with self._lock:
            q = self._events[key]
            while q and q[0] <= cutoff:
                q.popleft()
            if len(q) >= self.limit:
                return False
            q.append(now)
            return True
