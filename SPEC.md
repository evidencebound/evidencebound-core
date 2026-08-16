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
- unequal digest → `CHANGED`.

A digest mismatch MUST NOT by itself yield `REFUTED`.

## 4. Verification

Default fail-closed rules:
- receipt/checkpoint mismatch → integrity `FAILED`, action `BLOCK`;
- no evidence → `BLOCK`;
- required provenance incomplete → `BLOCK`;
- evidence `MISSING` or `REFUTED` → `BLOCK`;
- evidence `CHANGED`/`STALE` or policy mismatch → `REVIEW_REQUIRED`;
- otherwise → applicability `VERIFIED`, action `ALLOW`.

Historical integrity may remain `VERIFIED` while applicability is `REVIEW_REQUIRED` or `BLOCKED`.

## 5. Receipts

A receipt stores checkpoint digest, verification digest, policy ID/version, canonicalization version, checkpoint ID and receipt version. The built-in receipt is an integrity binding, not a signature or source-authenticity proof.

## 6. Graph

Dependencies form a directed acyclic graph from prerequisite → dependent. Missing dependencies, duplicate IDs and cycles are errors. Blast radius of invalidated roots is exactly the roots plus reachable descendants.

## 7. Recovery

Recovery planning is pure with respect to supplied graph/invalidations/verification results. Unaffected nodes are reusable; affected nodes are recompute candidates. Consequential affected nodes remain blocked until an `ALLOW` re-verification result is supplied to the action-after-recovery gate.

## 8. Replay

ReplayGuard associates an operation ID with one payload digest. First observation is `APPLIED`; equal replay is `ALREADY_APPLIED`; same ID with different payload is a conflict. This is not an exactly-once distributed execution guarantee.
