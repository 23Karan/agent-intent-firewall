import time

from security.agent_identity import AgentIdentity, sign_identity, verify_identity
from security.intent_state import IntentRegistry


def test_signed_identity_verifies():
    identity = AgentIdentity("agent-1", int(time.time()), "intent-1")
    secret = b"test-secret"
    signature = sign_identity(identity, secret)
    assert verify_identity(identity, signature, secret)


def test_tampered_identity_fails():
    secret = b"test-secret"
    identity = AgentIdentity("agent-1", int(time.time()), "intent-1")
    signature = sign_identity(identity, secret)
    tampered = AgentIdentity("agent-2", identity.issued_at, identity.intent_id)
    assert not verify_identity(tampered, signature, secret)


def test_intent_is_server_side_state():
    registry = IntentRegistry()
    registry.establish("agent-1", "intent-1", "Analyze repository")
    assert registry.matches("agent-1", "intent-1", "Analyze repository")
    assert not registry.matches("agent-1", "intent-1", "Read private credentials")
