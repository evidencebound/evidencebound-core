import json
import sqlite3
from dataclasses import replace
from pathlib import Path

import pytest

from evidencebound import (
    ActionDecision,
    Checkpoint,
    DependencyGraph,
    EvidenceRecord,
    InvalidationReason,
    PersistenceIntegrityError,
    PolicyBinding,
    ProvenanceRecord,
    ReplayConflict,
    ReplayStatus,
    UnsupportedPersistenceSchema,
    plan_recovery,
    verify_checkpoint,
)
from evidencebound.providers.sqlite import (
    SQLiteCrashPoint,
    SQLiteReplayGuard,
    SQLiteStore,
)


class InjectedCrash(RuntimeError):
    pass


def checkpoint(
    checkpoint_id: str,
    *,
    depends_on: tuple[str, ...] = (),
    operation_id: str | None = None,
    consequential: bool = True,
) -> Checkpoint:
    evidence = EvidenceRecord(
        f"e-{checkpoint_id}",
        {"value": checkpoint_id},
        ProvenanceRecord("test", f"urn:test:{checkpoint_id}"),
    )
    return Checkpoint(
        checkpoint_id,
        "agent",
        (evidence,),
        {"result": checkpoint_id},
        PolicyBinding("policy", "1", consequential=consequential),
        depends_on=depends_on,
        operation_id=operation_id,
    )


def commit(store: SQLiteStore, cp: Checkpoint) -> None:
    result = verify_checkpoint(cp)
    assert result.action is ActionDecision.ALLOW
    assert store.commit_bundle(cp, result) is None


def test_restart_reconstructs_graph_and_verified_state_deterministically(tmp_path: Path):
    path = tmp_path / "state.db"
    root = checkpoint("root")
    left = checkpoint("left", depends_on=("root",))
    right = checkpoint("right", depends_on=("root",))
    leaf = checkpoint("leaf", depends_on=("left",))
    expected = DependencyGraph((root, left, right, leaf))

    with SQLiteStore(path) as store:
        for cp in (root, right, left, leaf):
            commit(store, cp)

    with SQLiteStore(path) as reopened:
        graph, verification = reopened.load_recovery_state()

    assert graph.topological_order() == expected.topological_order()
    assert graph.blast_radius(("left",)) == expected.blast_radius(("left",))
    assert tuple(verification) == graph.topological_order()
    assert all(result.action is ActionDecision.ALLOW for result in verification.values())


def test_tampered_checkpoint_fails_binding_after_reopen(tmp_path: Path):
    path = tmp_path / "tamper.db"
    cp = checkpoint("cp")
    with SQLiteStore(path) as store:
        commit(store, cp)

    connection = sqlite3.connect(path)
    raw = connection.execute(
        "SELECT payload FROM eb_checkpoints WHERE checkpoint_id = 'cp'"
    ).fetchone()[0]
    payload = json.loads(raw)
    payload["output"] = {"result": "tampered"}
    connection.execute(
        "UPDATE eb_checkpoints SET payload = ? WHERE checkpoint_id = 'cp'",
        (json.dumps(payload, sort_keys=True, separators=(",", ":")),),
    )
    connection.commit()
    connection.close()

    with SQLiteStore(path) as reopened:
        with pytest.raises(PersistenceIntegrityError, match="fails receipt/checkpoint binding"):
            reopened.load_verification("cp")


def test_tampered_verification_state_fails_binding_after_reopen(tmp_path: Path):
    path = tmp_path / "verification-tamper.db"
    cp = checkpoint("cp")
    with SQLiteStore(path) as store:
        commit(store, cp)

    connection = sqlite3.connect(path)
    raw = connection.execute(
        "SELECT payload FROM eb_verifications WHERE checkpoint_id = 'cp'"
    ).fetchone()[0]
    payload = json.loads(raw)
    payload["action"] = "BLOCK"
    connection.execute(
        "UPDATE eb_verifications SET payload = ? WHERE checkpoint_id = 'cp'",
        (json.dumps(payload, sort_keys=True, separators=(",", ":")),),
    )
    connection.commit()
    connection.close()

    with SQLiteStore(path) as reopened:
        with pytest.raises(PersistenceIntegrityError, match="fails receipt/checkpoint binding"):
            reopened.load_verification("cp")


@pytest.mark.parametrize(
    "point",
    [
        SQLiteCrashPoint.AFTER_CHECKPOINT_WRITE,
        SQLiteCrashPoint.AFTER_RECEIPT_WRITE,
        SQLiteCrashPoint.AFTER_VERIFICATION_WRITE,
        SQLiteCrashPoint.AFTER_REPLAY_WRITE,
    ],
)
def test_crash_before_commit_rolls_back_entire_bundle(
    tmp_path: Path,
    point: SQLiteCrashPoint,
):
    path = tmp_path / f"rollback-{point.value}.db"
    cp = checkpoint("cp", operation_id="op-1")
    result = verify_checkpoint(cp)

    def inject(current: SQLiteCrashPoint) -> None:
        if current is point:
            raise InjectedCrash(point.value)

    store = SQLiteStore(path, fault_injector=inject)
    with pytest.raises(InjectedCrash):
        store.commit_bundle(cp, result, operation_id="op-1", operation_payload={"x": 1})
    store.close()

    with SQLiteStore(path) as reopened:
        assert reopened.load_graph().checkpoint_ids == ()
        assert reopened.apply_operation("op-1", {"x": 1}) is ReplayStatus.APPLIED


def test_crash_after_commit_preserves_complete_bundle_and_replay_state(tmp_path: Path):
    path = tmp_path / "after-commit.db"
    cp = checkpoint("cp", operation_id="op-1")
    result = verify_checkpoint(cp)

    def inject(current: SQLiteCrashPoint) -> None:
        if current is SQLiteCrashPoint.AFTER_COMMIT:
            raise InjectedCrash(current.value)

    store = SQLiteStore(path, fault_injector=inject)
    with pytest.raises(InjectedCrash):
        store.commit_bundle(cp, result, operation_id="op-1", operation_payload={"x": 1})
    store.close()

    with SQLiteStore(path) as reopened:
        loaded = reopened.load_verification("cp")
        assert loaded is not None
        assert loaded.action is ActionDecision.ALLOW
        assert reopened.apply_operation("op-1", {"x": 1}) is ReplayStatus.ALREADY_APPLIED


def test_replay_duplicate_and_conflict_survive_restart(tmp_path: Path):
    path = tmp_path / "replay.db"
    with SQLiteStore(path) as store:
        guard = SQLiteReplayGuard(store)
        assert guard.apply("operation", {"value": 1}) is ReplayStatus.APPLIED

    with SQLiteStore(path) as reopened:
        guard = SQLiteReplayGuard(reopened)
        assert guard.apply("operation", {"value": 1}) is ReplayStatus.ALREADY_APPLIED
        with pytest.raises(ReplayConflict):
            guard.apply("operation", {"value": 2})


def test_bundle_replay_is_idempotent_only_for_same_persisted_bundle(tmp_path: Path):
    path = tmp_path / "bundle-replay.db"
    cp = checkpoint("cp", operation_id="operation")
    result = verify_checkpoint(cp)
    with SQLiteStore(path) as store:
        assert (
            store.commit_bundle(
                cp,
                result,
                operation_id="operation",
                operation_payload={"request": 1},
            )
            is ReplayStatus.APPLIED
        )

    with SQLiteStore(path) as reopened:
        assert (
            reopened.commit_bundle(
                cp,
                result,
                operation_id="operation",
                operation_payload={"request": 1},
            )
            is ReplayStatus.ALREADY_APPLIED
        )
        with pytest.raises(ReplayConflict):
            reopened.commit_bundle(
                cp,
                result,
                operation_id="operation",
                operation_payload={"request": 2},
            )


def test_missing_verification_state_cannot_be_reused_or_allowed(tmp_path: Path):
    path = tmp_path / "partial.db"
    cp = checkpoint("cp")
    with SQLiteStore(path) as store:
        commit(store, cp)

    connection = sqlite3.connect(path)
    connection.execute("DELETE FROM eb_verifications WHERE checkpoint_id = 'cp'")
    connection.commit()
    connection.close()

    with SQLiteStore(path) as reopened:
        graph = reopened.load_graph()
        with pytest.raises(PersistenceIntegrityError, match="missing receipt or verification state"):
            reopened.load_recovery_state()

    plan = plan_recovery(graph, {}, verification={}, consequential={"cp"})
    assert plan.reusable == ()
    assert plan.requires_verification == ("cp",)
    assert plan.blocked == ("cp",)


def test_invalidation_blast_radius_is_identical_after_restart(tmp_path: Path):
    path = tmp_path / "blast.db"
    root = checkpoint("root")
    left = checkpoint("left", depends_on=("root",))
    leaf = checkpoint("leaf", depends_on=("left",))
    independent = checkpoint("independent")
    before = DependencyGraph((root, left, leaf, independent))

    with SQLiteStore(path) as store:
        for cp in (independent, root, left, leaf):
            commit(store, cp)

    with SQLiteStore(path) as reopened:
        after, verification = reopened.load_recovery_state()

    expected = before.blast_radius(("left",))
    assert after.blast_radius(("left",)) == expected == ("left", "leaf")
    plan = plan_recovery(
        after,
        {"left": InvalidationReason.EVIDENCE_CHANGED},
        verification=verification,
        consequential={"leaf", "independent"},
    )
    assert plan.recompute == ("left", "leaf")
    assert "independent" in plan.reusable
    assert "independent" not in plan.blocked


def test_unknown_database_schema_version_fails_closed(tmp_path: Path):
    path = tmp_path / "schema.db"
    with SQLiteStore(path):
        pass

    connection = sqlite3.connect(path)
    connection.execute(
        "UPDATE eb_metadata SET value = '2' WHERE key = 'schema_version'"
    )
    connection.commit()
    connection.close()

    with pytest.raises(UnsupportedPersistenceSchema, match="unsupported persistence schema"):
        SQLiteStore(path)


def test_unknown_record_version_fails_closed(tmp_path: Path):
    path = tmp_path / "record-version.db"
    cp = checkpoint("cp")
    with SQLiteStore(path) as store:
        commit(store, cp)

    connection = sqlite3.connect(path)
    connection.execute(
        "UPDATE eb_checkpoints SET record_version = '2' WHERE checkpoint_id = 'cp'"
    )
    connection.commit()
    connection.close()

    with SQLiteStore(path) as reopened:
        with pytest.raises(UnsupportedPersistenceSchema, match="checkpoint record version"):
            reopened.load_graph()


def test_partial_schema_fails_closed_instead_of_auto_repairing(tmp_path: Path):
    path = tmp_path / "partial-schema.db"
    with SQLiteStore(path):
        pass

    connection = sqlite3.connect(path)
    connection.execute("DROP TABLE eb_receipts")
    connection.commit()
    connection.close()

    with pytest.raises(UnsupportedPersistenceSchema, match="schema is incomplete"):
        SQLiteStore(path)


def test_invalid_verification_is_rejected_before_any_write(tmp_path: Path):
    path = tmp_path / "invalid-input.db"
    cp = checkpoint("cp")
    result = verify_checkpoint(cp)
    invalid = replace(result, action=ActionDecision.BLOCK)

    with SQLiteStore(path) as store:
        with pytest.raises(PersistenceIntegrityError, match="not bound"):
            store.commit_bundle(cp, invalid)
        assert store.load_graph().checkpoint_ids == ()
