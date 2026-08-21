"""Research prototype for correction-aware delegated-authority applicability.

This module is intentionally outside the installable EvidenceBound package. It is
proposal evidence for https://github.com/agentrust-io/ca2a/issues/129, not an
AgenTrust-conformant API or a new EvidenceBound wire standard.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Literal

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


class CommitState(str, Enum):
    PENDING = "pending"
    COMMITTED = "committed"


class ApplicabilityStatus(str, Enum):
    NOT_APPLICABLE = "not_applicable"
    SUPERSEDED = "superseded"
    REAPPRAISAL_REQUIRED = "reappraisal_required"
    POST_COMMIT_CORRECTION = "post_commit_correction"


Effect = Literal["invalidate_authority", "require_reappraisal"]


@dataclass(frozen=True)
class CorrectionBody:
    correction_id: str
    principal_id: str
    supersedes_kind: Literal["intent", "decision", "delegation_root", "state"]
    supersedes_digest: str
    replacement_digest: str | None
    affected_action_ids: tuple[str, ...] = ()
    affected_delegation_roots: tuple[str, ...] = ()
    affected_state_refs: tuple[str, ...] = ()
    effect: Effect = "invalidate_authority"
    reason_digest: str | None = None
    ordering_domain: str | None = None
    ordering_position: int | None = None
    ordering_anchor_digest: str | None = None

    def to_signing_object(self) -> dict[str, object]:
        ordering: dict[str, object] | None = None
        if (
            self.ordering_domain is not None
            or self.ordering_position is not None
            or self.ordering_anchor_digest is not None
        ):
            if self.ordering_domain is None or self.ordering_position is None:
                raise ValueError("ordering domain and position must be supplied together")
            ordering = {
                "domain": self.ordering_domain,
                "position": self.ordering_position,
                "anchor_digest": self.ordering_anchor_digest,
            }
        return {
            "type": "CorrectionReceipt/0.1",
            "correction_id": self.correction_id,
            "principal_id": self.principal_id,
            "supersedes": {
                "kind": self.supersedes_kind,
                "digest": self.supersedes_digest,
            },
            "replacement_digest": self.replacement_digest,
            "scope": {
                "action_ids": list(self.affected_action_ids),
                "delegation_roots": list(self.affected_delegation_roots),
                "state_refs": list(self.affected_state_refs),
            },
            "effect": self.effect,
            "reason_digest": self.reason_digest,
            "ordering_ref": ordering,
        }


@dataclass(frozen=True)
class SignedCorrectionReceipt:
    body: CorrectionBody
    key_id: str
    signature_hex: str


@dataclass(frozen=True)
class ActionEvidence:
    action_id: str
    authority_principal_id: str
    intent_digest: str
    delegation_root_digest: str | None = None
    state_refs: tuple[str, ...] = ()
    dependency_digests: tuple[str, ...] = ()
    dependency_set_complete: bool = True
    commit_state: CommitState = CommitState.PENDING
    ordering_domain: str | None = None
    decision_position: int | None = None
    commit_position: int | None = None


@dataclass(frozen=True)
class ApplicabilityResult:
    status: ApplicabilityStatus
    correction_id: str | None
    reason: str


def _validate_canonical_value(value: object) -> None:
    if value is None or isinstance(value, bool | str | int):
        return
    if isinstance(value, float):
        raise TypeError("floats are outside the prototype canonical subset")
    if isinstance(value, list):
        for item in value:
            _validate_canonical_value(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("object keys must be strings")
            if not key.isascii():
                raise TypeError("prototype property names must be ASCII")
            _validate_canonical_value(item)
        return
    raise TypeError(f"unsupported canonical value: {type(value).__name__}")


def canonical_body_bytes(body: CorrectionBody) -> bytes:
    """Return deterministic bytes for this constrained prototype data model.

    The prototype rejects floats and dynamic non-ASCII property names. Upstream
    adoption should use AgenTrust's repository-owned RFC 8785/JCS primitive.
    """

    obj = body.to_signing_object()
    _validate_canonical_value(obj)
    return json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sign_correction(
    body: CorrectionBody,
    key_id: str,
    private_key: Ed25519PrivateKey,
) -> SignedCorrectionReceipt:
    signature = private_key.sign(canonical_body_bytes(body))
    return SignedCorrectionReceipt(body=body, key_id=key_id, signature_hex=signature.hex())


def verify_correction_signature(
    receipt: SignedCorrectionReceipt,
    trusted_keys: Mapping[tuple[str, str], Ed25519PublicKey],
) -> bool:
    key = trusted_keys.get((receipt.body.principal_id, receipt.key_id))
    if key is None:
        return False
    try:
        signature = bytes.fromhex(receipt.signature_hex)
    except ValueError:
        return False
    try:
        key.verify(signature, canonical_body_bytes(receipt.body))
    except (InvalidSignature, ValueError, TypeError):
        return False
    return True


def _declared_dependency_match(action: ActionEvidence, body: CorrectionBody) -> bool:
    if action.intent_digest == body.supersedes_digest:
        return True
    if body.supersedes_digest in action.dependency_digests:
        return True
    if action.action_id in body.affected_action_ids:
        return True
    if (
        action.delegation_root_digest
        and action.delegation_root_digest in body.affected_delegation_roots
    ):
        return True
    return bool(set(action.state_refs).intersection(body.affected_state_refs))


def _correction_is_after_commit(action: ActionEvidence, body: CorrectionBody) -> bool | None:
    if action.commit_state is not CommitState.COMMITTED:
        return False
    if action.ordering_domain is None or action.commit_position is None:
        return None
    if body.ordering_domain is None or body.ordering_position is None:
        return None
    if action.ordering_domain != body.ordering_domain:
        return None
    return body.ordering_position > action.commit_position


def evaluate_corrections(
    action: ActionEvidence,
    receipts: list[SignedCorrectionReceipt],
    trusted_keys: Mapping[tuple[str, str], Ed25519PublicKey],
) -> ApplicabilityResult:
    """Evaluate correction evidence without rewriting historical authorization."""

    valid_receipts = [
        receipt
        for receipt in receipts
        if verify_correction_signature(receipt, trusted_keys)
    ]
    for receipt in valid_receipts:
        body = receipt.body
        if body.principal_id != action.authority_principal_id:
            continue

        if not _declared_dependency_match(action, body):
            if not action.dependency_set_complete:
                return ApplicabilityResult(
                    ApplicabilityStatus.REAPPRAISAL_REQUIRED,
                    body.correction_id,
                    "authoritative correction exists but dependency evidence is incomplete",
                )
            continue

        after_commit = _correction_is_after_commit(action, body)
        if after_commit is True:
            return ApplicabilityResult(
                ApplicabilityStatus.POST_COMMIT_CORRECTION,
                body.correction_id,
                "correction is ordered after commit; history is not rewritten",
            )
        if action.commit_state is CommitState.COMMITTED and after_commit is None:
            return ApplicabilityResult(
                ApplicabilityStatus.REAPPRAISAL_REQUIRED,
                body.correction_id,
                "relative correction/commit ordering cannot be proven",
            )
        if body.effect == "require_reappraisal":
            return ApplicabilityResult(
                ApplicabilityStatus.REAPPRAISAL_REQUIRED,
                body.correction_id,
                "verified correction explicitly requires reappraisal",
            )
        return ApplicabilityResult(
            ApplicabilityStatus.SUPERSEDED,
            body.correction_id,
            "verified correction supersedes a declared pending-action dependency",
        )

    return ApplicabilityResult(
        ApplicabilityStatus.NOT_APPLICABLE,
        None,
        "no verified applicable correction established from the supplied bundle",
    )
