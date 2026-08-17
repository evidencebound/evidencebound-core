"""Provider-neutral digital signatures for EvidenceBound proof receipts."""
from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable

from .canonical import CANONICALIZATION_VERSION, canonical_bytes
from .models import Checkpoint, ProofReceipt, VerificationResult
from .verification import verify_receipt, verify_verification_receipt

SIGNATURE_VERSION = "1"
SIGNATURE_ENCODING = "base64url-no-pad"
_SIGNED_RECEIPT_DOMAIN = "signed-receipt"


class KeyState(str, Enum):
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"
    REVOKED = "REVOKED"
    UNKNOWN = "UNKNOWN"


class SignatureCheckStatus(str, Enum):
    VERIFIED = "VERIFIED"
    INVALID_SIGNATURE = "INVALID_SIGNATURE"
    UNSUPPORTED_ALGORITHM = "UNSUPPORTED_ALGORITHM"
    UNKNOWN_KEY = "UNKNOWN_KEY"
    REVOKED_KEY = "REVOKED_KEY"


class SignedReceiptStatus(str, Enum):
    VERIFIED = "VERIFIED"
    VERIFIED_RETIRED_KEY = "VERIFIED_RETIRED_KEY"
    UNSIGNED = "UNSIGNED"
    INVALID_ENVELOPE = "INVALID_ENVELOPE"
    INVALID_SIGNATURE = "INVALID_SIGNATURE"
    UNSUPPORTED_ALGORITHM = "UNSUPPORTED_ALGORITHM"
    UNKNOWN_KEY = "UNKNOWN_KEY"
    REVOKED_KEY = "REVOKED_KEY"
    INVALID_BINDING = "INVALID_BINDING"
    PROVIDER_ERROR = "PROVIDER_ERROR"


@dataclass(frozen=True, slots=True)
class SignatureCheck:
    status: SignatureCheckStatus
    key_state: KeyState | None = None
    reason: str = ""


@dataclass(frozen=True, slots=True)
class SignedProofReceipt:
    receipt: ProofReceipt
    algorithm: str
    key_id: str
    signature: str
    signature_version: str = SIGNATURE_VERSION
    signature_encoding: str = SIGNATURE_ENCODING

    def signed_payload(self) -> dict[str, object]:
        return {
            "algorithm": self.algorithm,
            "key_id": self.key_id,
            "receipt": self.receipt.to_dict(),
            "signature_encoding": self.signature_encoding,
            "signature_version": self.signature_version,
        }

    def to_dict(self) -> dict[str, object]:
        return {**self.signed_payload(), "signature": self.signature}


@dataclass(frozen=True, slots=True)
class SignedReceiptVerification:
    status: SignedReceiptStatus
    verified: bool
    signature_valid: bool
    binding_valid: bool
    key_state: KeyState | None
    reason: str


@runtime_checkable
class ReceiptSigner(Protocol):
    algorithm: str
    key_id: str
    key_state: KeyState

    def sign(self, message: bytes) -> bytes:
        """Return a detached signature for message."""
        ...


@runtime_checkable
class ReceiptVerifier(Protocol):
    def verify(
        self,
        *,
        algorithm: str,
        key_id: str,
        message: bytes,
        signature: bytes,
    ) -> SignatureCheck:
        """Verify a detached signature without raising for expected verification failures."""
        ...


def signed_receipt_bytes(receipt: SignedProofReceipt) -> bytes:
    """Return the exact domain-separated canonical bytes covered by a signature."""
    prefix = (
        f"evidencebound:{_SIGNED_RECEIPT_DOMAIN}:{CANONICALIZATION_VERSION}:"
        f"{receipt.signature_version}\0"
    ).encode("utf-8")
    return prefix + canonical_bytes(receipt.signed_payload())


def _encode_signature(signature: bytes) -> str:
    return base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")


def _decode_signature(signature: str) -> bytes | None:
    try:
        encoded = signature.encode("ascii")
        padding = b"=" * (-len(encoded) % 4)
        decoded = base64.b64decode(encoded + padding, altchars=b"-_", validate=True)
    except (UnicodeEncodeError, ValueError, binascii.Error):
        return None
    return decoded if decoded else None


def sign_receipt(receipt: ProofReceipt, signer: ReceiptSigner) -> SignedProofReceipt:
    """Create a signed envelope without changing the underlying ProofReceipt."""
    if signer.key_state is not KeyState.ACTIVE:
        raise ValueError("only ACTIVE signing keys may create new signed receipts")
    algorithm = signer.algorithm.strip()
    key_id = signer.key_id.strip()
    if not algorithm:
        raise ValueError("signer algorithm must be non-empty")
    if not key_id:
        raise ValueError("signer key_id must be non-empty")
    if receipt.receipt_version != "1":
        raise ValueError("unsupported receipt_version for signing")
    if receipt.canonicalization_version != CANONICALIZATION_VERSION:
        raise ValueError("unsupported canonicalization_version for signing")

    unsigned = SignedProofReceipt(receipt, algorithm, key_id, signature="")
    signature = signer.sign(signed_receipt_bytes(unsigned))
    if not isinstance(signature, bytes) or not signature:
        raise ValueError("signer returned an empty or non-bytes signature")
    return SignedProofReceipt(receipt, algorithm, key_id, _encode_signature(signature))


def _binding_valid(
    receipt: ProofReceipt,
    checkpoint: Checkpoint,
    verification_result: VerificationResult | None,
) -> bool:
    if verification_result is None:
        return verify_receipt(receipt, checkpoint)
    return (
        verification_result.receipt == receipt
        and verify_verification_receipt(verification_result, checkpoint)
    )


def verify_signed_receipt(
    receipt: ProofReceipt | SignedProofReceipt,
    checkpoint: Checkpoint,
    verifier: ReceiptVerifier,
    *,
    verification_result: VerificationResult | None = None,
) -> SignedReceiptVerification:
    """Verify signature authentication and checkpoint/result binding, failing closed."""
    if isinstance(receipt, ProofReceipt):
        binding_valid = _binding_valid(receipt, checkpoint, verification_result)
        status = SignedReceiptStatus.UNSIGNED if binding_valid else SignedReceiptStatus.INVALID_BINDING
        reason = (
            "legacy ProofReceipt has valid deterministic binding but no issuer signature"
            if binding_valid
            else "legacy ProofReceipt is unsigned and does not bind the supplied checkpoint/result"
        )
        return SignedReceiptVerification(
            status=status,
            verified=False,
            signature_valid=False,
            binding_valid=binding_valid,
            key_state=None,
            reason=reason,
        )

    if (
        receipt.signature_version != SIGNATURE_VERSION
        or receipt.signature_encoding != SIGNATURE_ENCODING
        or not receipt.algorithm.strip()
        or not receipt.key_id.strip()
        or receipt.receipt.canonicalization_version != CANONICALIZATION_VERSION
    ):
        return SignedReceiptVerification(
            SignedReceiptStatus.INVALID_ENVELOPE,
            False,
            False,
            False,
            None,
            "signed receipt envelope metadata is unsupported or incomplete",
        )

    decoded = _decode_signature(receipt.signature)
    if decoded is None:
        return SignedReceiptVerification(
            SignedReceiptStatus.INVALID_SIGNATURE,
            False,
            False,
            False,
            None,
            "signature encoding is malformed or empty",
        )

    try:
        check = verifier.verify(
            algorithm=receipt.algorithm,
            key_id=receipt.key_id,
            message=signed_receipt_bytes(receipt),
            signature=decoded,
        )
    except Exception as exc:
        return SignedReceiptVerification(
            SignedReceiptStatus.PROVIDER_ERROR,
            False,
            False,
            False,
            None,
            f"signature verifier raised {type(exc).__name__}",
        )

    status_map = {
        SignatureCheckStatus.INVALID_SIGNATURE: SignedReceiptStatus.INVALID_SIGNATURE,
        SignatureCheckStatus.UNSUPPORTED_ALGORITHM: SignedReceiptStatus.UNSUPPORTED_ALGORITHM,
        SignatureCheckStatus.UNKNOWN_KEY: SignedReceiptStatus.UNKNOWN_KEY,
        SignatureCheckStatus.REVOKED_KEY: SignedReceiptStatus.REVOKED_KEY,
    }
    if check.status is not SignatureCheckStatus.VERIFIED:
        return SignedReceiptVerification(
            status_map.get(check.status, SignedReceiptStatus.PROVIDER_ERROR),
            False,
            False,
            False,
            check.key_state,
            check.reason or check.status.value,
        )

    if check.key_state in {KeyState.REVOKED, KeyState.UNKNOWN, None}:
        status = (
            SignedReceiptStatus.REVOKED_KEY
            if check.key_state is KeyState.REVOKED
            else SignedReceiptStatus.UNKNOWN_KEY
        )
        return SignedReceiptVerification(
            status,
            False,
            False,
            False,
            check.key_state,
            "verifier returned VERIFIED with a non-trusted key state",
        )

    binding_valid = _binding_valid(receipt.receipt, checkpoint, verification_result)
    if not binding_valid:
        return SignedReceiptVerification(
            SignedReceiptStatus.INVALID_BINDING,
            False,
            True,
            False,
            check.key_state,
            "signature is valid but receipt does not bind the supplied checkpoint/result",
        )

    if check.key_state is KeyState.RETIRED:
        return SignedReceiptVerification(
            SignedReceiptStatus.VERIFIED_RETIRED_KEY,
            True,
            True,
            True,
            check.key_state,
            "signature and binding verified with a retired verification key",
        )

    return SignedReceiptVerification(
        SignedReceiptStatus.VERIFIED,
        True,
        True,
        True,
        check.key_state,
        "signature and binding verified",
    )
