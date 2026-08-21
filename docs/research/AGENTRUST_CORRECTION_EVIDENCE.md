# AgenTrust research note: correction-aware supersession

Status: research prototype, not a normative EvidenceBound or AgenTrust standard  
Upstream issue: <https://github.com/agentrust-io/ca2a/issues/129>  
Related boundary: <https://github.com/agentrust-io/ca2a/issues/36>

## Question

A cA2A delegation can be authentic, attenuated, in-window, and authorized at decision time while a later authoritative principal correction changes the intent on which downstream authority or a pending action depended. How should an offline verifier preserve historical validity while reporting that the evidence is no longer currently applicable?

This note records the prototype used to test that boundary before proposing any AgenTrust wire-format change.

## Decision tested

The prototype treats correction as **new signed evidence**, never as mutation of a historical credential or action record. A detached correction identifies:

- the correcting principal/key;
- the digest of the superseded intent/decision/delegation root/state;
- optional declared affected action, delegation-root, and state identifiers;
- an effect: `invalidate_authority` or `require_reappraisal`;
- an optional replacement/reason digest;
- an optional tamper-evident ordering domain/position.

The verifier returns a separate correction-applicability result:

- `not_applicable`
- `superseded`
- `reappraisal_required`
- `post_commit_correction`

These states do not replace provenance validity, authorization validity, or execution outcome.

## Safety invariants

1. Invalid or untrusted correction signatures cannot revoke previously valid authority.
2. Historical evidence is never rewritten.
3. Semantic dependencies are not inferred from model text; only declared identifiers/digests propagate correction.
4. A relevant same-authority correction plus an incomplete dependency set fails visibly to `reappraisal_required`.
5. A correction ordered after irreversible commit yields `post_commit_correction`, not retroactive invalidation of execution history.
6. Absence of correction evidence means only that no applicable correction was established from the supplied bundle.
7. The prototype's canonicalization is deliberately constrained; any upstream implementation should reuse the repository-owned RFC 8785/JCS primitive.

## Executable evidence

Reference implementation: `tools/agentrust_correction_evidence.py`  
Tests: `tests/test_agentrust_correction_evidence.py`

The test suite covers ten cases:

1. no correction;
2. unrelated correction;
3. direct intent supersession;
4. declared descendant delegation-root scope;
5. incomplete dependency evidence;
6. forged correction signature;
7. post-commit correction;
8. signed-body tampering;
9. deterministic UTF-8 canonical bytes;
10. committed action with unprovable relative ordering.

The implementation deliberately lives under `tools/` rather than `src/evidencebound/`. It is public research evidence and is not exported by the EvidenceBound runtime package.

## Placement remains an upstream decision

The prototype does not assume that cA2A should own the final artifact. Plausible placements are:

- a cA2A companion profile because the effect is delegated-authority applicability;
- a detached TRACE correction/applicability record consumed by cA2A;
- a PIC/TRACE correction event with cA2A defining descendant consumption semantics.

Issue #129 asks maintainers to choose that container before a normative schema PR.

## AI assistance disclosure

OpenAI assisted with repository inspection, gap comparison, prototype implementation, tests, and draft wording. The public gap was checked against the cited current cA2A/TRACE work before filing upstream.
