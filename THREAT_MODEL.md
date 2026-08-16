# Threat Model

## Security goal

Make evidence-dependent agent state explicit, bind protected records deterministically, fail closed when required trust inputs are missing, and prevent unsafe reuse from silently crossing dependency invalidation boundaries.

## Helps detect / contain

- mutation of a checkpoint while an independently retained receipt is available;
- missing required evidence or provenance;
- evidence staleness when a validity horizon and caller-supplied current time are available;
- explicit evidence refutation supplied by a trusted upstream verifier;
- policy ID/version drift;
- dependency contamination through exact descendant invalidation;
- unsafe reuse after invalidation;
- duplicate operation replay under the in-process replay guard;
- malformed graph state such as cycles, missing dependencies and duplicate checkpoint IDs.

## Does not automatically solve

- truthfulness, completeness or honesty of an upstream source;
- authenticity when provenance cannot be externally authenticated;
- an attacker who can replace both mutable checkpoint and trusted receipt anchor;
- compromised host/runtime/interpreter;
- stolen signing keys (signed receipts are not yet part of core);
- arbitrary Byzantine consensus;
- model alignment or prompt-injection generally;
- correctness of an application’s policy;
- legal/regulatory compliance;
- distributed exactly-once side effects;
- secure persistence, backup or key lifecycle.

## Main attacker/error cases

| Case | Expected behavior |
|---|---|
| Protected output modified | prior receipt mismatch → BLOCK |
| Provenance deleted | required provenance incomplete → BLOCK |
| Current evidence missing | MISSING → BLOCK |
| Digest changes | CHANGED → REVIEW_REQUIRED, never implicit REFUTED |
| Explicit refutation | REFUTED → BLOCK |
| Policy version changes | historical integrity may remain VERIFIED; reuse requires review |
| Graph cycle | construction fails |
| Replay ID reused with different payload | conflict exception |
| Worker result untrusted | application must represent required supporting evidence; absence fails closed |

## Trust assumptions

The application must protect or independently anchor receipts if it relies on tamper detection across persistence boundaries. Provenance locators are assertions unless independently verified by an adapter/application. System time is a caller input; EvidenceBound does not silently claim secure time.

## Future hardening

Signed receipts with algorithm agility, external key management, persistence backends with atomic state transitions, fuzz/property suites, interoperability fixtures and independent security review are roadmap work.
