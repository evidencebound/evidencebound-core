from dataclasses import replace

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.agentrust_correction_evidence import (
    ActionEvidence,
    ApplicabilityStatus,
    CommitState,
    CorrectionBody,
    canonical_body_bytes,
    evaluate_corrections,
    sign_correction,
    verify_correction_signature,
)


def _keys():
    private = Ed25519PrivateKey.generate()
    trusted = {("spiffe://example.org/principal/alice", "alice-1"): private.public_key()}
    return private, trusted


def _action(**changes):
    base = ActionEvidence(
        action_id="action-42",
        authority_principal_id="spiffe://example.org/principal/alice",
        intent_digest="sha256:" + "1" * 64,
        delegation_root_digest="sha256:" + "2" * 64,
        state_refs=("state-7",),
        dependency_digests=("sha256:" + "3" * 64,),
        dependency_set_complete=True,
        ordering_domain="trace-log-A",
        decision_position=10,
    )
    return replace(base, **changes)


def _correction(**changes):
    base = CorrectionBody(
        correction_id="corr-1",
        principal_id="spiffe://example.org/principal/alice",
        supersedes_kind="intent",
        supersedes_digest="sha256:" + "1" * 64,
        replacement_digest="sha256:" + "4" * 64,
        effect="invalidate_authority",
        reason_digest="sha256:" + "5" * 64,
        ordering_domain="trace-log-A",
        ordering_position=11,
        ordering_anchor_digest="sha256:" + "6" * 64,
    )
    return replace(base, **changes)


def test_no_correction_leaves_correction_axis_not_applicable():
    _, trusted = _keys()
    assert evaluate_corrections(_action(), [], trusted).status is ApplicabilityStatus.NOT_APPLICABLE


def test_unrelated_correction_does_not_invalidate_complete_dependencies():
    private, trusted = _keys()
    receipt = sign_correction(
        _correction(supersedes_digest="sha256:" + "9" * 64), "alice-1", private
    )
    result = evaluate_corrections(_action(), [receipt], trusted)
    assert result.status is ApplicabilityStatus.NOT_APPLICABLE


def test_direct_intent_correction_supersedes_pending_action():
    private, trusted = _keys()
    receipt = sign_correction(_correction(), "alice-1", private)
    result = evaluate_corrections(_action(), [receipt], trusted)
    assert result.status is ApplicabilityStatus.SUPERSEDED
    assert result.correction_id == "corr-1"


def test_declared_root_scope_supersedes_descendant_action():
    private, trusted = _keys()
    body = _correction(
        supersedes_digest="sha256:" + "8" * 64,
        affected_delegation_roots=("sha256:" + "2" * 64,),
    )
    receipt = sign_correction(body, "alice-1", private)
    result = evaluate_corrections(_action(), [receipt], trusted)
    assert result.status is ApplicabilityStatus.SUPERSEDED


def test_incomplete_dependencies_require_reappraisal():
    private, trusted = _keys()
    body = _correction(supersedes_digest="sha256:" + "9" * 64)
    receipt = sign_correction(body, "alice-1", private)
    result = evaluate_corrections(_action(dependency_set_complete=False), [receipt], trusted)
    assert result.status is ApplicabilityStatus.REAPPRAISAL_REQUIRED


def test_invalid_signature_cannot_revoke_valid_authority():
    private, trusted = _keys()
    receipt = sign_correction(_correction(), "alice-1", private)
    tampered = replace(receipt, signature_hex="00" * 64)
    assert not verify_correction_signature(tampered, trusted)
    result = evaluate_corrections(_action(), [tampered], trusted)
    assert result.status is ApplicabilityStatus.NOT_APPLICABLE


def test_post_commit_correction_does_not_rewrite_history():
    private, trusted = _keys()
    receipt = sign_correction(_correction(ordering_position=21), "alice-1", private)
    committed = _action(commit_state=CommitState.COMMITTED, commit_position=20)
    result = evaluate_corrections(committed, [receipt], trusted)
    assert result.status is ApplicabilityStatus.POST_COMMIT_CORRECTION


def test_tampering_signed_body_breaks_signature():
    private, trusted = _keys()
    receipt = sign_correction(_correction(), "alice-1", private)
    tampered = replace(receipt, body=replace(receipt.body, effect="require_reappraisal"))
    assert not verify_correction_signature(tampered, trusted)


def test_canonical_bytes_are_deterministic_and_utf8():
    body = _correction(principal_id="spiffe://example.org/principal/álîçé")
    assert canonical_body_bytes(body) == canonical_body_bytes(body)
    assert "álîçé".encode() in canonical_body_bytes(body)


def test_unprovable_post_commit_order_requires_reappraisal():
    private, trusted = _keys()
    receipt = sign_correction(
        _correction(ordering_domain="other-log", ordering_position=21), "alice-1", private
    )
    committed = _action(commit_state=CommitState.COMMITTED, commit_position=20)
    result = evaluate_corrections(committed, [receipt], trusted)
    assert result.status is ApplicabilityStatus.REAPPRAISAL_REQUIRED
