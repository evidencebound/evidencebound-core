import pytest

from evidencebound import (
    ActionDecision,
    EvidenceBound,
    EvidenceRecord,
    ListEventSink,
    PolicyBinding,
    ReplayConflict,
    ReplayGuard,
    ReplayStatus,
)


def test_replay_guard():
    guard = ReplayGuard()
    assert guard.apply("op1", {"x": 1}) is ReplayStatus.APPLIED
    assert guard.apply("op1", {"x": 1}) is ReplayStatus.ALREADY_APPLIED
    with pytest.raises(ReplayConflict):
        guard.apply("op1", {"x": 2})


def test_structured_events_include_block():
    sink = ListEventSink()
    eb = EvidenceBound(policy=PolicyBinding("p", "1"), event_sink=sink)
    evidence = EvidenceRecord("e", {"x": 1}, None)
    cp = eb.checkpoint(agent="a", evidence=[evidence], output={"x": 1})
    result = eb.verify(cp)
    assert result.action is ActionDecision.BLOCK
    names = [event.name for event in sink.events]
    assert "checkpoint_created" in names
    assert "verification_completed" in names
    assert "action_blocked" in names
