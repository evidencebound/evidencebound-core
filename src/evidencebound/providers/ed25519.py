"""Optional Ed25519 reference provider for EvidenceBound signed receipts.

Importing this module requires the ``crypto`` extra (``cryptography``).
The core signing protocol itself has no unconditional cryptography dependency.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from ..signing import KeyState, SignatureCheck, SignatureCheckStatus

ED25519_ALGORITHM = "Ed25519"


@dataclass(frozen=True, slots=True)
class Ed25519VerificationKey:
    public_key: Ed25519PublicKey
    state: KeyState = KeyState.ACTIVE


class Ed25519Signer:
    algorithm = ED25519_ALGORITHM

    def __init__(
        self,
        private_key: Ed25519PrivateKey,
        key_id: str,
        *,
        key_state: KeyState = KeyState.ACTIVE,
    ) -> None:
        self._private_key = private_key
        self.key_id = key_id
        self.key_state = key_state

    def sign(self, message: bytes) -> bytes:
        return self._private_key.sign(message)


class Ed25519Verifier:
    def __init__(self, keys: Mapping[str, Ed25519VerificationKey]) -> None:
        self._keys = dict(keys)

    def verify(
        self,
        *,
        algorithm: str,
        key_id: str,
        message: bytes,
        signature: bytes,
    ) -> SignatureCheck:
        if algorithm != ED25519_ALGORITHM:
            return SignatureCheck(
                SignatureCheckStatus.UNSUPPORTED_ALGORITHM,
                reason=f"unsupported algorithm: {algorithm}",
            )

        key = self._keys.get(key_id)
        if key is None:
            return SignatureCheck(
                SignatureCheckStatus.UNKNOWN_KEY,
                KeyState.UNKNOWN,
                f"unknown key_id: {key_id}",
            )
        if key.state is KeyState.REVOKED:
            return SignatureCheck(
                SignatureCheckStatus.REVOKED_KEY,
                KeyState.REVOKED,
                f"key_id is revoked: {key_id}",
            )

        try:
            key.public_key.verify(signature, message)
        except InvalidSignature:
            return SignatureCheck(
                SignatureCheckStatus.INVALID_SIGNATURE,
                key.state,
                "Ed25519 signature is invalid",
            )

        return SignatureCheck(
            SignatureCheckStatus.VERIFIED,
            key.state,
            "Ed25519 signature verified",
        )
