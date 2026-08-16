# EvidenceBound Core Specification — alpha

## 1. Canonical representation

`EBCJ-1` supports: `null`, boolean, integer, Unicode string, array, and string-keyed object. Floats and unsupported Python types MUST fail canonicalization. Object keys are lexicographically sorted; separators are compact; output is UTF-8 JSON. Domain digests are SHA-256 over:

`evidencebound:<domain>:EBCJ-1\0 || canonical_bytes(payload)`

Changing canonicalization semantics requires a new version identifier.

## 2. Checkpoint binding

A checkpoint protected payload includes checkpoint ID, agent, evidence records including provenance, output, policy binding, dependencies, operation ID and schema version. `checkpoint_digest` binds this complete payload.

## 3. Evidence state

For a protected snapshot and a supplied current record:
- absent/payload null → `MISSING`;
- explicit refutation marker → `REFUTED`;
- expired `valid_until` at caller-supplied `now` → `STALE`;
- equal evidence payload digest → `UNCHANGED`;
- unequal digest → `CHANGED`;
- a supplied current evidence ID absent from the protected snapshot → `NEW`.

A digest mismatch MUST NOT by itself yield `REFUTED`.

## 4. Verification

Default fail-closed rules:
- receipt/checkpoint mismatch → integrity `FAILED`, action `BLOCK`;
- no evidence → `BLOCK`;
- duplicate evidence IDs → `BLOCK` (and high-level checkpoint creation rejects them);
- required provenance incomplete → `BLOCK`;
- evidence `MISSING` or `REFUTED` → `BLOCK`;
- evidence `CHANGED`/`STALE`/`NEW` or policy mismatch → `REVIEW_REQUIRED`;
- otherwise → applicability `VERIFIED`, action `ALLOW`.

Historical integrity may remain `VERIFIED` while applicability is `REVIEW_REQUIRED` or `BLOCKED`.

## 5. Receipts

A receipt stores checkpoint digest, verification digest, policy ID/version, canonicalization version, checkpoint ID and receipt version. `verify_receipt()` validates receipt metadata and the checkpoint binding. `verify_verification_receipt()` additionally recomputes the historical verification payload digest and checks the supplied `VerificationResult` binding. The built-in receipt is an integrity binding, not a signature or source-authenticity proof.

## 6. Graph

Dependencies form a directed acyclic graph from prerequisite → dependent. Missing dependencies, duplicate IDs and cycles are errors. Blast radius of invalidated roots is exactly the roots plus reachable descendants.

## 7. Recovery

Recovery planning is pure with respect to supplied graph/invalidations/verification results. `reusable` means an unaffected checkpoint with a supplied `ALLOW` verification result whose verification receipt is bound to the exact checkpoint payload currently present in the graph. Unaffected checkpoints without such a bound `ALLOW` result are reported separately as `requires_verification`; they are not silently trusted. `recompute` contains affected checkpoints only.

For a non-reusable checkpoint, `reverification_requirements` contains only the non-reusable ancestors on its dependency path plus itself. This prevents an invalidation in an unrelated branch from becoming a false prerequisite. Consequential actions remain blocked until their path-specific requirements have matching checkpoint IDs and `ALLOW` re-verification results.

## 8. Replay

ReplayGuard associates an operation ID with one payload digest. First observation is `APPLIED`; equal replay is `ALREADY_APPLIED`; same ID with different payload is a conflict. This is not an exactly-once distributed execution guarantee.
