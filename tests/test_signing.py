from dataclasses import replace

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from evidencebound import (
    ActionDecision,
    Checkpoint,
    EvidenceRecord,
    KeyState,
    PolicyBinding,
    ProofReceipt,
    ProvenanceRecord,
    SignatureCheck,
    SignatureCheckStatus,
    SignedProofReceipt,
    SignedReceiptStatus,
    sign_receipt,
    signed_receipt_bytes,
    verify_checkpoint,
    verify_signed_receipt,
)
from evidencebound.providers.ed25519 import (
    ED25519_ALGORITHM,
    Ed25519Signer,
    Ed25519VerificationKey,
    Ed25519Verifier,
)


def checkpoint() -> Checkpoint:
    evidence = EvidenceRecord(
        "e1",
        {"value": 1},
        ProvenanceRecord("source", "urn:test:1"),
    )
    return Checkpoint(
        "cp-sign",
        "agent",
        (evidence,),
        {"answer": 42},
        PolicyBinding("policy", "1"),
    )


def signing_material(
    *,
    state: KeyState = KeyState.ACTIVE,
) -> tuple[Ed25519Signer, Ed25519Verifier]:
    private_key = Ed25519PrivateKey.generate()
    signer = Ed25519Signer(private_key, "key-1", key_state=state)
    verifier = Ed25519Verifier(
        {"key-1": Ed25519VerificationKey(private_key.public_key(), state)}
    )
    return signer, verifier


def test_ed25519_signed_receipt_verifies_with_active_key():
    cp = checkpoint()
    result = verify_checkpoint(cp)
    signer, verifier = signing_material()
    signed = sign_receipt(result.receipt, signer)

    checked = verify_signed_receipt(
        signed,
        cp,
        verifier,
        verification_result=result,
    )

    assert checked.status is SignedReceiptStatus.VERIFIED
    assert checked.verified
    assert checked.signature_valid
    assert checked.binding_valid
    assert checked.key_state is KeyState.ACTIVE


def test_protected_receipt_tamper_breaks_signature():
    cp = checkpoint()
    result = verify_checkpoint(cp)
    signer, verifier = signing_material()
    signed = sign_receipt(result.receipt, signer)

    changed_inner = replace(
        signed.receipt,
        verification_digest="0" * 64,
    )
    tampered = replace(signed, receipt=changed_inner)
    checked = verify_signed_receipt(tampered, cp, verifier)

    assert checked.status is SignedReceiptStatus.INVALID_SIGNATURE
    assert not checked.verified
    assert not checked.signature_valid


def test_checkpoint_tamper_keeps_signature_authentic_but_fails_binding():
    cp = checkpoint()
    result = verify_checkpoint(cp)
    signer, verifier = signing_material()
    signed = sign_receipt(result.receipt, signer)

    tampered_checkpoint = replace(cp, output={"answer": 7})
    checked = verify_signed_receipt(signed, tampered_checkpoint, verifier)

    assert checked.status is SignedReceiptStatus.INVALID_BINDING
    assert not checked.verified
    assert checked.signature_valid
    assert not checked.binding_valid


def test_wrong_existing_key_id_fails_signature():
    cp = checkpoint()
    result = verify_checkpoint(cp)
    private_a = Ed25519PrivateKey.generate()
    private_b = Ed25519PrivateKey.generate()
    signer = Ed25519Signer(private_a, "key-a")
    verifier = Ed25519Verifier(
        {
            "key-a": Ed25519VerificationKey(private_a.public_key()),
            "key-b": Ed25519VerificationKey(private_b.public_key()),
        }
    )
    signed = sign_receipt(result.receipt, signer)

    changed_key_id = replace(signed, key_id="key-b")
    checked = verify_signed_receipt(changed_key_id, cp, verifier)

    assert checked.status is SignedReceiptStatus.INVALID_SIGNATURE
    assert not checked.verified


def test_unknown_key_and_algorithm_metadata_fail_closed():
    cp = checkpoint()
    result = verify_checkpoint(cp)
    signer, verifier = signing_material()
    signed = sign_receipt(result.receipt, signer)

    unknown_key = verify_signed_receipt(replace(signed, key_id="missing"), cp, verifier)
    assert unknown_key.status is SignedReceiptStatus.UNKNOWN_KEY
    assert not unknown_key.verified

    wrong_algorithm = verify_signed_receipt(
        replace(signed, algorithm="example-unsupported"),
        cp,
        verifier,
    )
    assert wrong_algorithm.status is SignedReceiptStatus.UNSUPPORTED_ALGORITHM
    assert not wrong_algorithm.verified


def test_signature_and_version_metadata_are_signed_or_fail_closed():
    cp = checkpoint()
    result = verify_checkpoint(cp)
    signer, verifier = signing_material()
    signed = sign_receipt(result.receipt, signer)

    changed_receipt_version = replace(
        signed,
        receipt=replace(signed.receipt, receipt_version="2"),
    )
    assert signed_receipt_bytes(changed_receipt_version) != signed_receipt_bytes(signed)
    checked_version = verify_signed_receipt(changed_receipt_version, cp, verifier)
    assert checked_version.status is SignedReceiptStatus.INVALID_SIGNATURE

    changed_canonicalization = replace(
        signed,
        receipt=replace(signed.receipt, canonicalization_version="EBCJ-2"),
    )
    assert signed_receipt_bytes(changed_canonicalization) != signed_receipt_bytes(signed)
    checked_canonicalization = verify_signed_receipt(
        changed_canonicalization,
        cp,
        verifier,
    )
    assert checked_canonicalization.status is SignedReceiptStatus.INVALID_ENVELOPE
    assert not checked_canonicalization.verified


def test_malformed_signature_fails_before_provider_verification():
    cp = checkpoint()
    result = verify_checkpoint(cp)
    signer, verifier = signing_material()
    signed = sign_receipt(result.receipt, signer)

    malformed = replace(signed, signature="%%%not-base64url%%%")
    checked = verify_signed_receipt(malformed, cp, verifier)

    assert checked.status is SignedReceiptStatus.INVALID_SIGNATURE
    assert not checked.verified


def test_unsigned_legacy_receipt_is_never_authenticated():
    cp = checkpoint()
    result = verify_checkpoint(cp)
    _, verifier = signing_material()

    checked = verify_signed_receipt(
        result.receipt,
        cp,
        verifier,
        verification_result=result,
    )

    assert checked.status is SignedReceiptStatus.UNSIGNED
    assert not checked.verified
    assert not checked.signature_valid
    assert checked.binding_valid


def test_retired_key_verifies_history_but_cannot_sign_new_receipts():
    cp = checkpoint()
    result = verify_checkpoint(cp)
    private_key = Ed25519PrivateKey.generate()
    active_signer = Ed25519Signer(private_key, "rotated-key")
    retired_verifier = Ed25519Verifier(
        {
            "rotated-key": Ed25519VerificationKey(
                private_key.public_key(),
                KeyState.RETIRED,
            )
        }
    )
    signed = sign_receipt(result.receipt, active_signer)

    checked = verify_signed_receipt(signed, cp, retired_verifier)
    assert checked.status is SignedReceiptStatus.VERIFIED_RETIRED_KEY
    assert checked.verified
    assert checked.key_state is KeyState.RETIRED

    retired_signer = Ed25519Signer(
        private_key,
        "rotated-key",
        key_state=KeyState.RETIRED,
    )
    with pytest.raises(ValueError, match="only ACTIVE signing keys"):
        sign_receipt(result.receipt, retired_signer)


def test_revoked_key_fails_closed():
    cp = checkpoint()
    result = verify_checkpoint(cp)
    private_key = Ed25519PrivateKey.generate()
    signer = Ed25519Signer(private_key, "revoked-key")
    signed = sign_receipt(result.receipt, signer)
    verifier = Ed25519Verifier(
        {
            "revoked-key": Ed25519VerificationKey(
                private_key.public_key(),
                KeyState.REVOKED,
            )
        }
    )

    checked = verify_signed_receipt(signed, cp, verifier)
    assert checked.status is SignedReceiptStatus.REVOKED_KEY
    assert not checked.verified


def test_changed_verification_result_fails_signed_binding():
    cp = checkpoint()
    result = verify_checkpoint(cp)
    signer, verifier = signing_material()
    signed = sign_receipt(result.receipt, signer)
    changed_result = replace(result, action=ActionDecision.BLOCK)

    checked = verify_signed_receipt(
        signed,
        cp,
        verifier,
        verification_result=changed_result,
    )
    assert checked.status is SignedReceiptStatus.INVALID_BINDING
    assert checked.signature_valid
    assert not checked.verified


def test_provider_exception_is_fail_closed():
    cp = checkpoint()
    result = verify_checkpoint(cp)
    signer, _ = signing_material()
    signed = sign_receipt(result.receipt, signer)

    class BrokenVerifier:
        def verify(
            self,
            *,
            algorithm: str,
            key_id: str,
            message: bytes,
            signature: bytes,
        ) -> SignatureCheck:
            raise RuntimeError("provider unavailable")

    checked = verify_signed_receipt(signed, cp, BrokenVerifier())
    assert checked.status is SignedReceiptStatus.PROVIDER_ERROR
    assert not checked.verified


def test_reference_provider_reports_expected_algorithm_name():
    assert ED25519_ALGORITHM == "Ed25519"


def test_defensive_verified_with_unknown_key_state_is_rejected():
    cp = checkpoint()
    result = verify_checkpoint(cp)
    signer, _ = signing_material()
    signed = sign_receipt(result.receipt, signer)

    class BadVerifier:
        def verify(
            self,
            *,
            algorithm: str,
            key_id: str,
            message: bytes,
            signature: bytes,
        ) -> SignatureCheck:
            return SignatureCheck(
                SignatureCheckStatus.VERIFIED,
                KeyState.UNKNOWN,
                "bad provider result",
            )

    checked = verify_signed_receipt(signed, cp, BadVerifier())
    assert checked.status is SignedReceiptStatus.UNKNOWN_KEY
    assert not checked.verified


def test_signer_rejects_unsupported_receipt_version_before_signing():
    cp = checkpoint()
    result = verify_checkpoint(cp)
    signer, _ = signing_material()
    unsupported: ProofReceipt = replace(result.receipt, receipt_version="2")

    with pytest.raises(ValueError, match="unsupported receipt_version"):
        sign_receipt(unsupported, signer)


def test_signed_receipt_serialization_is_json_shape():
    cp = checkpoint()
    result = verify_checkpoint(cp)
    signer, _ = signing_material()
    signed: SignedProofReceipt = sign_receipt(result.receipt, signer)

    data = signed.to_dict()
    assert data["algorithm"] == ED25519_ALGORITHM
    assert data["key_id"] == "key-1"
    assert isinstance(data["receipt"], dict)
    assert data["receipt"]["checkpoint_id"] == cp.checkpoint_id
