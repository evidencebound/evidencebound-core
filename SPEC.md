# EvidenceBound Core Specification — alpha

## 1. Canonical representation

`EBCJ-1` supports: `null`, boolean, integer, Unicode string, array, and string-keyed object. Floats and unsupported Python types MUST fail canonicalization. Object keys are lexicographically sorted; separators are compact; output is UTF-8 JSON. Domain digests are SHA-256 over:

`evidencebound:<domain>:EBCJ-1\0 || canonical_bytes(payload)`

Changing canonicalization semantics requires a new version identifier.

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

A receipt stores checkpoint digest, verification digest, policy ID/version, canonicalization version, checkpoint ID and receipt version.

`verify_receipt()` validates receipt version, digest shape, policy metadata, canonicalization metadata, checkpoint identity, and binding to the exact protected checkpoint payload.

`verify_verification_receipt()` additionally recomputes the historical verification payload digest and checks the supplied `VerificationResult` binding.

The built-in receipt is an integrity binding, not a digital signature or source-authenticity proof. Its security value assumes the receipt/digest is retained or anchored independently enough for the application threat model.

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

`ReplayGuard` associates an operation ID with one payload digest. First observation is `APPLIED`; equal replay is `ALREADY_APPLIED`; same ID with different payload is a conflict. This is an in-process idempotency guard, not an exactly-once distributed execution guarantee.

## 9. Versioning boundary

`0.x` releases are alpha/pre-1.0. Public imports are curated, but compatibility changes remain possible when documented. Canonicalization and receipt-version changes require explicit version changes rather than silent reinterpretation of historical records.
