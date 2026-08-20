import time

from security.agent_identity import AgentIdentity, sign_identity
from security.intent_store import IntentRecord, IntentStore
from security.request_verifier import RequestVerifier


def test_valid_signed_request():
    secret = b"test-secret"
    intents = IntentStore()
    intents.establish(IntentRecord("i-1", "agent-1", "Analyze repository"))
    verifier = RequestVerifier({"agent-1": secret}, intents)
    issued = int(time.time())
    identity = AgentIdentity("agent-1", issued, "i-1")
    signature = sign_identity(identity, secret)

    assert verifier.verify(
        agent_id="agent-1", intent_id="i-1", intent="Analyze repository",
        issued_at=issued, signature=signature
    ) == (True, "verified")


def test_modified_intent_is_rejected():
    secret = b"test-secret"
    intents = IntentStore()
    intents.establish(IntentRecord("i-1", "agent-1", "Analyze repository"))
    verifier = RequestVerifier({"agent-1": secret}, intents)
    issued = int(time.time())
    identity = AgentIdentity("agent-1", issued, "i-1")

    assert verifier.verify(
        agent_id="agent-1", intent_id="i-1", intent="Delete repository",
        issued_at=issued, signature=sign_identity(identity, secret)
    )[0] is False


def test_unknown_agent_is_rejected():
    verifier = RequestVerifier({}, IntentStore())
    assert verifier.verify(
        agent_id="attacker", intent_id="i-1", intent="anything",
        issued_at=int(time.time()), signature="fake"
    )[0] is False
