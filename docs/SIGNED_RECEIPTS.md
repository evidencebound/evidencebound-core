# Signed Receipts

Status: **Unreleased on `main` after v0.3.0**. The published `v0.3.0` tag does not contain this API.

EvidenceBound's base `ProofReceipt` is deterministic and tamper-evident when retained independently enough for the application threat model. A base receipt does not authenticate an issuer.

Current `main` adds a provider-neutral signed-envelope layer without changing the underlying receipt format.

## Install

Core remains dependency-free at runtime:

```bash
python -m pip install .
```

The optional Ed25519 reference provider uses `cryptography`:

```bash
python -m pip install '.[crypto]'
```

`cryptography` is optional; custom `ReceiptSigner` / `ReceiptVerifier` implementations can use a KMS, HSM, remote signer, hardware token, another crypto library, or a testing provider without changing EvidenceBound Core.

## Core contract

```python
from evidencebound import (
    KeyState,
    ReceiptSigner,
    ReceiptVerifier,
    SignatureCheck,
    SignatureCheckStatus,
    sign_receipt,
    verify_signed_receipt,
)
```

A signer exposes:

- `algorithm: str`
- `key_id: str`
- `key_state: KeyState`
- `sign(message: bytes) -> bytes`

A verifier accepts algorithm, key ID, exact message bytes and detached signature and returns `SignatureCheck`.

Expected verification failures are data, not exceptions. Unexpected provider exceptions are caught by core and produce `PROVIDER_ERROR`.

## Ed25519 example

```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from evidencebound import KeyState, sign_receipt, verify_signed_receipt
from evidencebound.providers.ed25519 import (
    Ed25519Signer,
    Ed25519VerificationKey,
    Ed25519Verifier,
)

private_key = Ed25519PrivateKey.generate()  # example only; use real key custody in production
signer = Ed25519Signer(private_key, key_id="issuer-2026-08")
verifier = Ed25519Verifier({
    "issuer-2026-08": Ed25519VerificationKey(
        private_key.public_key(),
        KeyState.ACTIVE,
    )
})

signed = sign_receipt(verification_result.receipt, signer)

checked = verify_signed_receipt(
    signed,
    checkpoint,
    verifier,
    verification_result=verification_result,
)
assert checked.verified
```

The example generates an in-memory key only to demonstrate the API. EvidenceBound does not prescribe production private-key storage.

## What is signed

Signature format version `1` covers domain-separated canonical bytes containing:

- algorithm identifier;
- key identifier;
- the full underlying `ProofReceipt`;
- receipt version;
- canonicalization version;
- signature encoding identifier;
- signature format version.

The detached signature itself is encoded as unpadded base64url and is excluded from the signed bytes.

Changing algorithm, key ID, receipt digest, policy metadata, receipt version or other protected signed fields changes the signed message and invalidates the original signature.

Changing the checkpoint while leaving a signed receipt untouched is different: the signature may still authenticate the receipt, but the receipt/checkpoint binding fails. `verify_signed_receipt()` reports this as `INVALID_BINDING` and `verified=False`.

## Key lifecycle

Core uses four key states:

| State | New signing | Verification |
|---|---:|---:|
| `ACTIVE` | allowed | allowed |
| `RETIRED` | rejected | allowed for historical receipts |
| `REVOKED` | rejected | fail closed |
| `UNKNOWN` | rejected | fail closed |

Rotation therefore does not require rewriting historical receipts. Keep old public verification material available as `RETIRED` for as long as historical signatures must remain verifiable. If compromise policy requires invalidating a key, mark it `REVOKED`.

## Algorithm agility

The signed envelope carries the algorithm identifier. EvidenceBound Core does not maintain a global cryptographic algorithm registry.

A verifier/provider decides which algorithms it supports and MUST return `UNSUPPORTED_ALGORITHM` when it cannot verify the requested algorithm. Core treats that status as unverified/fail-closed.

Changing algorithm names or signature format semantics must be explicit; do not reinterpret historical envelopes under different rules.

## Legacy migration

Existing `ProofReceipt` values remain valid deterministic integrity bindings. They are **not** silently promoted to authenticated receipts.

Passing a legacy receipt to `verify_signed_receipt()` returns:

- `binding_valid=True` when its existing deterministic binding checks;
- `status=UNSIGNED`;
- `verified=False`;
- `signature_valid=False`.

Migration choices:

1. Keep historical receipts unsigned and preserve that fact.
2. Re-run/re-verify the underlying checkpoint under current policy and issue a new signed receipt.
3. If an application chooses to sign a pre-existing receipt later, record that signing event separately; do not claim the signature existed at the original historical decision time.

## Security limits

A successful signed-receipt verification means:

- the detached signature is valid under the configured provider/key;
- key state is acceptable;
- the signed receipt binds the supplied checkpoint (and, when supplied, verification result).

It does **not** prove:

- upstream evidence is truthful;
- provenance identity is genuine unless separately authenticated;
- a signing key was not stolen;
- an application key registry is trustworthy;
- legal/regulatory compliance;
- secure time or secure persistence.

See `THREAT_MODEL.md` and `SPEC.md`.
