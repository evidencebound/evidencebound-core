# EvidenceBound Core Specification — alpha

## 1. Canonical representation

`EBCJ-1` supports: `null`, boolean, integer, Unicode string, array, and string-keyed object. Floats and unsupported Python types MUST fail canonicalization. Object keys are lexicographically sorted; separators are compact; output is UTF-8 JSON. EBCJ-1 does **not** normalize Unicode: canonically equivalent Unicode strings with different code-point sequences remain different bytes.

Domain digests are SHA-256 over:

`evidencebound:<domain>:EBCJ-1\0 || canonical_bytes(payload)`

The versioned, language-neutral conformance corpus is under `conformance/EBCJ-1/`. `vectors.json` fixes expected canonical UTF-8 text/hex plus representative domain digests; Python-specific non-JSON invalid inputs are documented in `invalid-python.json`. Changing canonicalization semantics requires a new version identifier rather than silently changing EBCJ-1 vectors. EBCJ-1 is an EvidenceBound format and is **not** a claim of RFC 8785/JCS compliance.

## 2. Checkpoint binding

A checkpoint protected payload includes checkpoint ID, agent, evidence records including provenance, output, policy binding, dependencies, operation ID and schema version. `checkpoint_digest` binds this complete payload.

Evidence IDs within one checkpoint MUST be unique when created through the high-level API. A directly constructed checkpoint containing duplicate evidence IDs MUST fail closed during verification.

## 3. Evidence state and identity

For a protected snapshot and supplied current evidence:

- absent/payload null → `MISSING`;
- current mapping key whose contained `EvidenceRecord.evidence_id` differs from that key → fail closed; a mismatched record cannot satisfy the protected evidence identity;
- explicit refutation marker → `REFUTED`;
- expired `valid_until` at caller-supplied `now` → `STALE`;
- equal evidence identity and payload digest → `UNCHANGED`;
- unequal digest → `CHANGED`;
- a supplied current evidence ID absent from the protected snapshot → `NEW`.

A digest mismatch MUST NOT by itself yield `REFUTED`.

## 4. Verification

Default fail-closed rules:

- prior receipt/checkpoint digest mismatch → integrity `FAILED`, action `BLOCK`;
- no evidence → `BLOCK`;
- duplicate evidence IDs → `BLOCK`;
- current evidence identity mismatch → `BLOCK`;
- required provenance incomplete → `BLOCK`;
- evidence `MISSING` or `REFUTED` → `BLOCK`;
- evidence `CHANGED`/`STALE`/`NEW` or policy mismatch → `REVIEW_REQUIRED`;
- otherwise → applicability `VERIFIED`, action `ALLOW`.

Historical integrity may remain `VERIFIED` while applicability is `REVIEW_REQUIRED` or `BLOCKED`. Historical integrity describes the retained protected record; current applicability describes whether that record may safely be reused under current evidence and policy.

Staleness evaluation never silently reads wall-clock time. A caller that needs time-based staleness MUST supply a timezone-aware `now` value.

## 5. Receipts

A `ProofReceipt` stores checkpoint digest, verification digest, policy ID/version, canonicalization version, checkpoint ID and receipt version.

`verify_receipt()` validates receipt version, digest shape, policy metadata, canonicalization metadata, checkpoint identity, and binding to the exact protected checkpoint payload.

`verify_verification_receipt()` additionally recomputes the historical verification payload digest and checks the supplied `VerificationResult` binding.

An unsigned `ProofReceipt` is an integrity binding, not a digital signature or source-authenticity proof. Its security value assumes the receipt/digest is retained or anchored independently enough for the application threat model.

### 5.1 Signed receipt envelope

`SignedProofReceipt` wraps, rather than mutates, a `ProofReceipt`. Signature format version `1` signs detached, domain-separated bytes:

`evidencebound:signed-receipt:EBCJ-1:1\0 || canonical_bytes(signed_payload)`

The signed payload contains:

- `algorithm`;
- `key_id`;
- the complete underlying `ProofReceipt`, including receipt and canonicalization versions;
- `signature_encoding`;
- `signature_version`.

The signature itself is encoded as unpadded base64url and is excluded from the signed payload.

`ReceiptSigner` and `ReceiptVerifier` are provider-neutral protocols. Core does not require a cloud KMS, HSM, crypto vendor or agent framework.

New signatures MUST use an `ACTIVE` signing key. A verifier MAY accept a cryptographically valid `RETIRED` key for historical verification. `REVOKED` and `UNKNOWN` keys MUST fail closed. Unsupported algorithm metadata, malformed signature encoding, provider exceptions, and invalid signature results MUST fail closed.

`verify_signed_receipt()` separates signature validity from receipt/checkpoint binding:

- valid signature + valid binding + ACTIVE key → `VERIFIED`;
- valid signature + valid binding + RETIRED key → `VERIFIED_RETIRED_KEY`;
- valid unsigned legacy receipt → `UNSIGNED`, never authenticated;
- valid signature over a receipt that does not bind the supplied checkpoint/result → `INVALID_BINDING`;
- all invalid/unknown/revoked/unsupported/provider-error cases → not verified.

A valid signature authenticates possession/use of a configured signing key under the application's key-identity trust model. It does **not** establish that upstream evidence is truthful, complete, current, or non-malicious.

## 6. Graph

Dependencies form a directed acyclic graph from prerequisite → dependent. Missing dependencies, duplicate checkpoint IDs and cycles are errors. Blast radius of invalidated roots is exactly the roots plus reachable descendants.

Topological order and traversal-derived recovery sets are deterministic for the same graph.

## 7. Recovery

Recovery planning is pure with respect to supplied graph, invalidations and verification results.

- `recompute` contains checkpoints in the exact invalidation blast radius.
- `reusable` contains only unaffected checkpoints with a supplied `ALLOW` verification result whose verification receipt is bound to the exact checkpoint payload currently present in the graph.
- `requires_verification` contains unaffected checkpoints that cannot yet be safely classified as reusable.
- `blocked` contains consequential actions that may not proceed under the current plan.

For a non-reusable checkpoint, `reverification_requirements` contains only the non-reusable ancestors on its dependency path plus itself. This prevents an invalidation in an unrelated branch from becoming a false prerequisite.

A consequential action remains blocked until every path-specific required checkpoint has a matching checkpoint ID and an `ALLOW` re-verification result. This is a deterministic trust gate; EvidenceBound does not itself schedule or rerun workers.

## 8. Replay

`ReplayGuard` associates an operation ID with one payload digest. First observation is `APPLIED`; equal replay is `ALREADY_APPLIED`; same ID with different payload is a conflict. The base guard is in-process only.

A persistence provider MAY implement the same semantics durably. `SQLiteReplayGuard` stores the existing `operation` domain digest so duplicate/conflict behavior survives process restart. This remains an idempotency primitive, not an exactly-once distributed execution guarantee.

## 9. Persistence

`PersistenceStore` is the provider-neutral durability contract. Persisted state MUST NOT be treated as trusted solely because it exists in storage.

### 9.1 Persisted bundle

A persistence implementation that stores verification state for reuse MUST preserve the logical relationship between:

- checkpoint;
- proof receipt;
- verification state;
- optional replay/idempotency record associated with the checkpoint operation.

Before a `VerificationResult` is accepted for persistence, its receipt MUST verify against the exact checkpoint being stored.

On load, a persistence implementation MUST reconstruct the stored checkpoint, receipt and verification state and verify the result binding again before returning verification state for recovery/reuse. Missing or malformed trust-bearing records MUST fail closed.

### 9.2 SQLite reference provider

The version-1 SQLite provider uses:

- persistence schema version `1`;
- individual record version `1`;
- explicit SQLite transactions for bundle writes;
- foreign-key enforcement;
- deterministic canonical JSON text for structured records;
- `synchronous=FULL` and WAL for file-backed stores.

Checkpoint, receipt, verification and optional replay rows are committed in one transaction. An injected failure before commit MUST leave no partial bundle visible after reopen. A failure after commit MAY leave the complete bundle durable; that bundle still MUST pass receipt/result binding verification when loaded.

An existing replay record does not by itself authorize a repeated bundle. For a same-payload duplicate, the stored checkpoint, receipt and verification payloads MUST exactly match the intended bundle; otherwise replay fails as a persistence integrity error.

### 9.3 Reconstruction

`load_checkpoint()` reconstructs stored data only and MUST NOT be interpreted as a trust decision.

`load_graph()` reconstructs all stored checkpoints and runs normal dependency-graph validation. Invalid IDs, missing dependencies and cycles fail closed.

`load_verification()` returns a persisted verification result only after deterministic receipt/result binding succeeds against the exact loaded checkpoint.

`load_recovery_state()` returns a graph plus verified persisted results. The reference SQLite provider requires complete valid verification state for every persisted checkpoint; it does not silently omit corrupted verification rows.

### 9.4 Schema evolution

Unknown persistence schema versions or record versions MUST fail closed. The alpha version-1 provider does not silently auto-migrate unknown trust-bearing schemas. A future migration mechanism must be explicit, versioned and tested for semantic preservation.

### 9.5 Security boundary

SQLite is not claimed immutable or authenticated. The reference provider protects transactional consistency under its supported failure model and detects persisted modifications when EvidenceBound receipt/result binding no longer matches. If an attacker can consistently replace checkpoint and receipt/trust-root state together, applications need an independent receipt anchor and/or signed receipts with independently protected verification roots.

See `docs/PERSISTENCE.md` and `THREAT_MODEL.md`.

## 10. Versioning boundary

`0.x` releases are alpha/pre-1.0. Public imports are curated, but compatibility changes remain possible when documented. Canonicalization, receipt-version, signed-envelope-version and persistence-schema changes require explicit version changes rather than silent reinterpretation of historical records.
