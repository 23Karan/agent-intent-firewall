from security.replay_guard import ReplayGuard
from security.rate_limit import RateLimiter


def test_replay_is_rejected():
    guard = ReplayGuard(ttl_seconds=60)
    assert guard.accept("request-1")
    assert not guard.accept("request-1")


def test_rate_limit_blocks_after_limit():
    limiter = RateLimiter(limit=2, window_seconds=60)
    assert limiter.allow("agent-a")
    assert limiter.allow("agent-a")
    assert not limiter.allow("agent-a")
