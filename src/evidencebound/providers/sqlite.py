"""Crash-consistent stdlib SQLite reference persistence for EvidenceBound."""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import Any, cast

from ..canonical import canonical_bytes, digest
from ..graph import DependencyGraph, GraphError
from ..models import (
    ActionDecision,
    ApplicabilityStatus,
    Checkpoint,
    EvidenceAssessment,
    EvidenceRecord,
    EvidenceState,
    IntegrityStatus,
    JsonValue,
    PolicyBinding,
    ProofReceipt,
    ProvenanceRecord,
    VerificationResult,
)
from ..persistence import (
    PERSISTED_RECORD_VERSION,
    PERSISTENCE_SCHEMA_VERSION,
    PersistenceError,
    PersistenceIntegrityError,
    UnsupportedPersistenceSchema,
)
from ..replay import ReplayConflict, ReplayStatus
from ..verification import verify_verification_receipt


class SQLiteCrashPoint(str, Enum):
    BEFORE_CHECKPOINT_WRITE = "before_checkpoint_write"
    AFTER_CHECKPOINT_WRITE = "after_checkpoint_write"
    BEFORE_RECEIPT_WRITE = "before_receipt_write"
    AFTER_RECEIPT_WRITE = "after_receipt_write"
    AFTER_VERIFICATION_WRITE = "after_verification_write"
    BEFORE_REPLAY_WRITE = "before_replay_write"
    AFTER_REPLAY_WRITE = "after_replay_write"
    AFTER_COMMIT = "after_commit"


FaultInjector = Callable[[SQLiteCrashPoint], None]

_EXPECTED_TABLES = {
    "eb_metadata",
    "eb_checkpoints",
    "eb_receipts",
    "eb_verifications",
    "eb_replay",
}


class SQLiteStore:
    """Reference durable store with explicit all-or-nothing bundle commits.

    Stored verification results are never trusted merely because they exist.
    Every load reconstructs the checkpoint, receipt and verification state and
    re-runs deterministic receipt/result binding before returning a result.
    """

    def __init__(
        self,
        path: str | Path,
        *,
        fault_injector: FaultInjector | None = None,
    ) -> None:
        self.path = str(path)
        self._fault_injector = fault_injector
        self._connection = sqlite3.connect(self.path, isolation_level=None)
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.execute("PRAGMA synchronous = FULL")
        if self.path != ":memory:":
            self._connection.execute("PRAGMA journal_mode = WAL")
        self._initialize_schema()

    def __enter__(self) -> SQLiteStore:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    def close(self) -> None:
        self._connection.close()

    def _initialize_schema(self) -> None:
        existing = {
            cast(str, row[0])
            for row in self._connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        evidencebound_tables = existing & _EXPECTED_TABLES
        if "eb_metadata" in existing:
            row = self._connection.execute(
                "SELECT value FROM eb_metadata WHERE key = 'schema_version'"
            ).fetchone()
            if row is None:
                raise UnsupportedPersistenceSchema("missing persistence schema_version metadata")
            version = cast(str, row[0])
            if version != PERSISTENCE_SCHEMA_VERSION:
                raise UnsupportedPersistenceSchema(
                    f"unsupported persistence schema version: {version!r}"
                )
            missing = _EXPECTED_TABLES - existing
            if missing:
                raise UnsupportedPersistenceSchema(
                    "persistence schema is incomplete; missing tables: "
                    + ", ".join(sorted(missing))
                )
            return
        if evidencebound_tables:
            raise UnsupportedPersistenceSchema(
                "partial EvidenceBound persistence schema found without metadata"
            )

        self._connection.execute(
            "CREATE TABLE eb_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        self._connection.execute(
            """
            CREATE TABLE eb_checkpoints (
                checkpoint_id TEXT PRIMARY KEY,
                record_version TEXT NOT NULL,
                payload TEXT NOT NULL
            )
            """
        )
        self._connection.execute(
            """
            CREATE TABLE eb_receipts (
                checkpoint_id TEXT PRIMARY KEY
                    REFERENCES eb_checkpoints(checkpoint_id) ON DELETE CASCADE,
                record_version TEXT NOT NULL,
                payload TEXT NOT NULL
            )
            """
        )
        self._connection.execute(
            """
            CREATE TABLE eb_verifications (
                checkpoint_id TEXT PRIMARY KEY
                    REFERENCES eb_checkpoints(checkpoint_id) ON DELETE CASCADE,
                record_version TEXT NOT NULL,
                payload TEXT NOT NULL
            )
            """
        )
        self._connection.execute(
            """
            CREATE TABLE eb_replay (
                operation_id TEXT PRIMARY KEY,
                payload_digest TEXT NOT NULL
            )
            """
        )
        self._connection.execute(
            "INSERT INTO eb_metadata(key, value) VALUES('schema_version', ?)",
            (PERSISTENCE_SCHEMA_VERSION,),
        )

    def _fault(self, point: SQLiteCrashPoint) -> None:
        if self._fault_injector is not None:
            self._fault_injector(point)

    def _rollback_if_needed(self) -> None:
        if self._connection.in_transaction:
            self._connection.rollback()

    def commit_bundle(
        self,
        checkpoint: Checkpoint,
        verification: VerificationResult,
        *,
        operation_id: str | None = None,
        operation_payload: Any | None = None,
    ) -> ReplayStatus | None:
        """Atomically commit checkpoint, receipt, verification and optional replay state."""
        if checkpoint.schema_version != PERSISTED_RECORD_VERSION:
            raise UnsupportedPersistenceSchema(
                f"unsupported checkpoint schema version: {checkpoint.schema_version!r}"
            )
        if checkpoint.checkpoint_id != verification.checkpoint_id:
            raise PersistenceIntegrityError("checkpoint and verification IDs differ")
        if not verify_verification_receipt(verification, checkpoint):
            raise PersistenceIntegrityError(
                "verification receipt is not bound to the checkpoint being persisted"
            )
        if checkpoint.operation_id != operation_id:
            if checkpoint.operation_id is not None or operation_id is not None:
                raise PersistenceIntegrityError(
                    "checkpoint operation_id must match the atomically persisted replay operation"
                )
        if operation_id is None and operation_payload is not None:
            raise PersistenceError("operation_payload requires operation_id")

        checkpoint_text = _canonical_text(checkpoint.to_dict())
        receipt_text = _canonical_text(verification.receipt.to_dict())
        verification_text = _canonical_text(_verification_state_payload(verification))
        operation_digest = (
            digest(operation_payload, domain="operation") if operation_id is not None else None
        )

        if self._connection.in_transaction:
            raise PersistenceError("connection already has an open transaction")
        self._connection.execute("BEGIN IMMEDIATE")
        try:
            if operation_id is not None and operation_digest is not None:
                previous = self._connection.execute(
                    "SELECT payload_digest FROM eb_replay WHERE operation_id = ?",
                    (operation_id,),
                ).fetchone()
                if previous is not None:
                    previous_digest = cast(str, previous[0])
                    if previous_digest != operation_digest:
                        raise ReplayConflict(
                            f"operation id {operation_id!r} was reused with a different payload"
                        )
                    self._require_existing_bundle_matches(
                        checkpoint.checkpoint_id,
                        checkpoint_text,
                        receipt_text,
                        verification_text,
                    )
                    self._connection.rollback()
                    return ReplayStatus.ALREADY_APPLIED

            self._fault(SQLiteCrashPoint.BEFORE_CHECKPOINT_WRITE)
            self._connection.execute(
                """
                INSERT INTO eb_checkpoints(checkpoint_id, record_version, payload)
                VALUES(?, ?, ?)
                ON CONFLICT(checkpoint_id) DO UPDATE SET
                    record_version = excluded.record_version,
                    payload = excluded.payload
                """,
                (checkpoint.checkpoint_id, PERSISTED_RECORD_VERSION, checkpoint_text),
            )
            self._fault(SQLiteCrashPoint.AFTER_CHECKPOINT_WRITE)
            self._fault(SQLiteCrashPoint.BEFORE_RECEIPT_WRITE)
            self._connection.execute(
                """
                INSERT INTO eb_receipts(checkpoint_id, record_version, payload)
                VALUES(?, ?, ?)
                ON CONFLICT(checkpoint_id) DO UPDATE SET
                    record_version = excluded.record_version,
                    payload = excluded.payload
                """,
                (checkpoint.checkpoint_id, PERSISTED_RECORD_VERSION, receipt_text),
            )
            self._fault(SQLiteCrashPoint.AFTER_RECEIPT_WRITE)
            self._connection.execute(
                """
                INSERT INTO eb_verifications(checkpoint_id, record_version, payload)
                VALUES(?, ?, ?)
                ON CONFLICT(checkpoint_id) DO UPDATE SET
                    record_version = excluded.record_version,
                    payload = excluded.payload
                """,
                (checkpoint.checkpoint_id, PERSISTED_RECORD_VERSION, verification_text),
            )
            self._fault(SQLiteCrashPoint.AFTER_VERIFICATION_WRITE)

            if operation_id is not None and operation_digest is not None:
                self._fault(SQLiteCrashPoint.BEFORE_REPLAY_WRITE)
                self._connection.execute(
                    "INSERT INTO eb_replay(operation_id, payload_digest) VALUES(?, ?)",
                    (operation_id, operation_digest),
                )
                self._fault(SQLiteCrashPoint.AFTER_REPLAY_WRITE)

            self._connection.commit()
        except Exception:
            self._rollback_if_needed()
            raise

        self._fault(SQLiteCrashPoint.AFTER_COMMIT)
        return ReplayStatus.APPLIED if operation_id is not None else None

    def _require_existing_bundle_matches(
        self,
        checkpoint_id: str,
        checkpoint_text: str,
        receipt_text: str,
        verification_text: str,
    ) -> None:
        row = self._connection.execute(
            """
            SELECT c.payload, r.payload, v.payload
            FROM eb_checkpoints AS c
            LEFT JOIN eb_receipts AS r USING(checkpoint_id)
            LEFT JOIN eb_verifications AS v USING(checkpoint_id)
            WHERE c.checkpoint_id = ?
            """,
            (checkpoint_id,),
        ).fetchone()
        expected = (checkpoint_text, receipt_text, verification_text)
        if row is None or tuple(row) != expected:
            raise PersistenceIntegrityError(
                "replay record exists but its persisted checkpoint bundle is missing or different"
            )

    def apply_operation(self, operation_id: str, payload: Any) -> ReplayStatus:
        """Persist replay/idempotency state independently of a checkpoint bundle."""
        payload_digest = digest(payload, domain="operation")
        if self._connection.in_transaction:
            raise PersistenceError("connection already has an open transaction")
        self._connection.execute("BEGIN IMMEDIATE")
        try:
            previous = self._connection.execute(
                "SELECT payload_digest FROM eb_replay WHERE operation_id = ?",
                (operation_id,),
            ).fetchone()
            if previous is not None:
                self._connection.rollback()
                if cast(str, previous[0]) == payload_digest:
                    return ReplayStatus.ALREADY_APPLIED
                raise ReplayConflict(
                    f"operation id {operation_id!r} was reused with a different payload"
                )
            self._fault(SQLiteCrashPoint.BEFORE_REPLAY_WRITE)
            self._connection.execute(
                "INSERT INTO eb_replay(operation_id, payload_digest) VALUES(?, ?)",
                (operation_id, payload_digest),
            )
            self._fault(SQLiteCrashPoint.AFTER_REPLAY_WRITE)
            self._connection.commit()
        except Exception:
            self._rollback_if_needed()
            raise
        self._fault(SQLiteCrashPoint.AFTER_COMMIT)
        return ReplayStatus.APPLIED

    def load_checkpoint(self, checkpoint_id: str) -> Checkpoint | None:
        row = self._connection.execute(
            "SELECT record_version, payload FROM eb_checkpoints WHERE checkpoint_id = ?",
            (checkpoint_id,),
        ).fetchone()
        if row is None:
            return None
        _check_record_version(cast(str, row[0]), "checkpoint", checkpoint_id)
        return _decode_checkpoint(cast(str, row[1]))

    def load_verification(self, checkpoint_id: str) -> VerificationResult | None:
        checkpoint_row = self._connection.execute(
            "SELECT record_version, payload FROM eb_checkpoints WHERE checkpoint_id = ?",
            (checkpoint_id,),
        ).fetchone()
        if checkpoint_row is None:
            return None
        receipt_row = self._connection.execute(
            "SELECT record_version, payload FROM eb_receipts WHERE checkpoint_id = ?",
            (checkpoint_id,),
        ).fetchone()
        verification_row = self._connection.execute(
            "SELECT record_version, payload FROM eb_verifications WHERE checkpoint_id = ?",
            (checkpoint_id,),
        ).fetchone()
        if receipt_row is None or verification_row is None:
            raise PersistenceIntegrityError(
                f"persisted checkpoint {checkpoint_id!r} is missing receipt or verification state"
            )

        _check_record_version(cast(str, checkpoint_row[0]), "checkpoint", checkpoint_id)
        _check_record_version(cast(str, receipt_row[0]), "receipt", checkpoint_id)
        _check_record_version(cast(str, verification_row[0]), "verification", checkpoint_id)
        checkpoint = _decode_checkpoint(cast(str, checkpoint_row[1]))
        receipt = _decode_receipt(cast(str, receipt_row[1]))
        result = _decode_verification(cast(str, verification_row[1]), receipt)
        if result.checkpoint_id != checkpoint_id or checkpoint.checkpoint_id != checkpoint_id:
            raise PersistenceIntegrityError("persisted checkpoint IDs are inconsistent")
        if not verify_verification_receipt(result, checkpoint):
            raise PersistenceIntegrityError(
                f"persisted verification for {checkpoint_id!r} fails receipt/checkpoint binding"
            )
        return result

    def load_graph(self) -> DependencyGraph:
        checkpoints: list[Checkpoint] = []
        for checkpoint_id, record_version, payload in self._connection.execute(
            """
            SELECT checkpoint_id, record_version, payload
            FROM eb_checkpoints
            ORDER BY checkpoint_id
            """
        ):
            checkpoint_id = cast(str, checkpoint_id)
            _check_record_version(cast(str, record_version), "checkpoint", checkpoint_id)
            checkpoint = _decode_checkpoint(cast(str, payload))
            if checkpoint.checkpoint_id != checkpoint_id:
                raise PersistenceIntegrityError(
                    "checkpoint row key differs from serialized checkpoint_id"
                )
            checkpoints.append(checkpoint)
        try:
            return DependencyGraph(checkpoints)
        except GraphError as exc:
            raise PersistenceIntegrityError(
                f"persisted dependency graph is invalid: {exc}"
            ) from exc

    def load_recovery_state(self) -> tuple[DependencyGraph, dict[str, VerificationResult]]:
        graph = self.load_graph()
        verification: dict[str, VerificationResult] = {}
        for checkpoint_id in graph.topological_order():
            result = self.load_verification(checkpoint_id)
            if result is None:
                raise PersistenceIntegrityError(
                    f"checkpoint {checkpoint_id!r} disappeared while loading recovery state"
                )
            verification[checkpoint_id] = result
        return graph, verification


class SQLiteReplayGuard:
    """ReplayGuard-compatible durable wrapper backed by SQLiteStore."""

    def __init__(self, store: SQLiteStore) -> None:
        self._store = store

    def apply(self, operation_id: str, payload: Any) -> ReplayStatus:
        return self._store.apply_operation(operation_id, payload)


def _canonical_text(payload: Any) -> str:
    return canonical_bytes(payload).decode()


def _check_record_version(version: str, kind: str, identifier: str) -> None:
    if version != PERSISTED_RECORD_VERSION:
        raise UnsupportedPersistenceSchema(
            f"unsupported {kind} record version {version!r} for {identifier!r}"
        )


def _decode_json_object(text: str, label: str) -> dict[str, Any]:
    try:
        value: Any = json.loads(text)
        canonical_bytes(value)
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise PersistenceIntegrityError(f"malformed canonical JSON for {label}") from exc
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise PersistenceIntegrityError(f"{label} must be a string-keyed JSON object")
    return cast(dict[str, Any], value)


def _string(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise PersistenceIntegrityError(f"{field} must be a string")
    return value


def _optional_string(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _string(value, field)


def _boolean(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise PersistenceIntegrityError(f"{field} must be a boolean")
    return value


def _list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise PersistenceIntegrityError(f"{field} must be a list")
    return value


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise PersistenceIntegrityError(f"{field} must be a string-keyed object")
    return cast(dict[str, Any], value)


def _decode_provenance(value: Any) -> ProvenanceRecord | None:
    if value is None:
        return None
    data = _object(value, "provenance")
    metadata = _object(data.get("metadata", {}), "provenance.metadata")
    return ProvenanceRecord(
        source=_optional_string(data.get("source"), "provenance.source"),
        locator=_optional_string(data.get("locator"), "provenance.locator"),
        retrieved_at=_optional_string(data.get("retrieved_at"), "provenance.retrieved_at"),
        content_type=_optional_string(data.get("content_type"), "provenance.content_type"),
        metadata=cast(dict[str, JsonValue], metadata),
    )


def _decode_evidence(value: Any) -> EvidenceRecord:
    data = _object(value, "evidence")
    return EvidenceRecord(
        evidence_id=_string(data.get("evidence_id"), "evidence.evidence_id"),
        payload=cast(JsonValue | None, data.get("payload")),
        provenance=_decode_provenance(data.get("provenance")),
        observed_at=_optional_string(data.get("observed_at"), "evidence.observed_at"),
        valid_until=_optional_string(data.get("valid_until"), "evidence.valid_until"),
        explicitly_refuted=_boolean(
            data.get("explicitly_refuted", False),
            "evidence.explicitly_refuted",
        ),
    )


def _decode_policy(value: Any) -> PolicyBinding:
    data = _object(value, "policy")
    return PolicyBinding(
        policy_id=_string(data.get("policy_id"), "policy.policy_id"),
        version=_string(data.get("version"), "policy.version"),
        require_provenance=_boolean(
            data.get("require_provenance", True),
            "policy.require_provenance",
        ),
        consequential=_boolean(data.get("consequential", True), "policy.consequential"),
    )


def _decode_checkpoint(text: str) -> Checkpoint:
    data = _decode_json_object(text, "checkpoint")
    schema_version = _string(data.get("schema_version"), "checkpoint.schema_version")
    if schema_version != PERSISTED_RECORD_VERSION:
        raise UnsupportedPersistenceSchema(
            f"unsupported checkpoint schema version: {schema_version!r}"
        )
    evidence = tuple(_decode_evidence(item) for item in _list(data.get("evidence"), "evidence"))
    dependencies = tuple(
        _string(item, "checkpoint.depends_on item")
        for item in _list(data.get("depends_on", []), "checkpoint.depends_on")
    )
    return Checkpoint(
        checkpoint_id=_string(data.get("checkpoint_id"), "checkpoint.checkpoint_id"),
        agent=_string(data.get("agent"), "checkpoint.agent"),
        evidence=evidence,
        output=cast(JsonValue, data.get("output")),
        policy=_decode_policy(data.get("policy")),
        depends_on=dependencies,
        operation_id=_optional_string(data.get("operation_id"), "checkpoint.operation_id"),
        schema_version=schema_version,
    )


def _decode_receipt(text: str) -> ProofReceipt:
    data = _decode_json_object(text, "receipt")
    return ProofReceipt(
        checkpoint_id=_string(data.get("checkpoint_id"), "receipt.checkpoint_id"),
        checkpoint_digest=_string(data.get("checkpoint_digest"), "receipt.checkpoint_digest"),
        verification_digest=_string(
            data.get("verification_digest"),
            "receipt.verification_digest",
        ),
        policy_id=_string(data.get("policy_id"), "receipt.policy_id"),
        policy_version=_string(data.get("policy_version"), "receipt.policy_version"),
        canonicalization_version=_string(
            data.get("canonicalization_version"),
            "receipt.canonicalization_version",
        ),
        receipt_version=_string(data.get("receipt_version"), "receipt.receipt_version"),
    )


def _verification_state_payload(result: VerificationResult) -> dict[str, Any]:
    return {
        "checkpoint_id": result.checkpoint_id,
        "integrity": result.integrity.value,
        "applicability": result.applicability.value,
        "action": result.action.value,
        "provenance_complete": result.provenance_complete,
        "policy_compatible": result.policy_compatible,
        "evidence": [item.to_dict() for item in result.evidence],
        "reasons": list(result.reasons),
    }


def _decode_assessment(value: Any) -> EvidenceAssessment:
    data = _object(value, "evidence assessment")
    try:
        state = EvidenceState(_string(data.get("state"), "assessment.state"))
    except ValueError as exc:
        raise PersistenceIntegrityError("unknown evidence assessment state") from exc
    return EvidenceAssessment(
        evidence_id=_string(data.get("evidence_id"), "assessment.evidence_id"),
        state=state,
        snapshot_digest=_optional_string(
            data.get("snapshot_digest"),
            "assessment.snapshot_digest",
        ),
        current_digest=_optional_string(
            data.get("current_digest"),
            "assessment.current_digest",
        ),
        reason=_string(data.get("reason"), "assessment.reason"),
    )


def _decode_verification(text: str, receipt: ProofReceipt) -> VerificationResult:
    data = _decode_json_object(text, "verification")
    try:
        integrity = IntegrityStatus(_string(data.get("integrity"), "verification.integrity"))
        applicability = ApplicabilityStatus(
            _string(data.get("applicability"), "verification.applicability")
        )
        action = ActionDecision(_string(data.get("action"), "verification.action"))
    except ValueError as exc:
        raise PersistenceIntegrityError("unknown persisted verification enum value") from exc
    reasons = tuple(
        _string(item, "verification.reasons item")
        for item in _list(data.get("reasons", []), "verification.reasons")
    )
    assessments = tuple(
        _decode_assessment(item)
        for item in _list(data.get("evidence", []), "verification.evidence")
    )
    return VerificationResult(
        checkpoint_id=_string(data.get("checkpoint_id"), "verification.checkpoint_id"),
        integrity=integrity,
        applicability=applicability,
        action=action,
        provenance_complete=_boolean(
            data.get("provenance_complete"),
            "verification.provenance_complete",
        ),
        policy_compatible=_boolean(
            data.get("policy_compatible"),
            "verification.policy_compatible",
        ),
        evidence=assessments,
        reasons=reasons,
        receipt=receipt,
    )
