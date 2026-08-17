# External Security Review Scope

Status: **review requested / not yet performed**  
Tracking issue: #23  
Canonical repository: https://github.com/moneyparking/evidencebound-core

This document is a reviewer-facing scope and reproducibility packet. Its existence is not an audit, certification, endorsement, or finding that the implementation is secure.

## Source boundary

Two source boundaries must not be conflated:

- published GitHub source release `v0.3.0`: `2477164acfbdca6a843bf7b2eac5fa21ce9901b2`;
- post-release review target baseline when this packet was prepared: `16e6e5915bcbb0888e297a5162770198fb7e38ce` on `main`.

The release tag is immutable historical evidence. Post-release signed receipts, SQLite persistence, conformance/property testing, maintained Google ADK compatibility, and trusted-main build attestations must not be retroactively attributed to `v0.3.0`.

Before starting a review, record the exact review SHA and use that SHA throughout findings and reproduction notes.

## What EvidenceBound is intended to enforce

EvidenceBound is a framework-neutral Python trust runtime for agent/application checkpoints. Its deterministic core binds evidence, provenance and policy/version metadata to protected checkpoint state, verifies historical integrity separately from current applicability, emits proof receipts, models checkpoint dependencies, computes exact descendant invalidation, separates reusable state from re-verification/recompute work, and provides fail-closed action decisions.

The application remains responsible for evidence acquisition, domain truth, trust-root selection and side-effect execution.

## Critical security invariants

A review should attempt to falsify these invariants rather than assume them:

1. Protected checkpoint payload modification after receipt creation is detectable and cannot remain `ALLOW` under receipt verification.
2. Historical integrity `VERIFIED` can coexist with current applicability `REVIEW_REQUIRED`; current change does not rewrite historical integrity.
3. A digest change is `CHANGED` and is never automatically interpreted as `REFUTED`.
4. Missing/refuted required evidence, required provenance loss, policy mismatch where applicable, malformed persisted trust state, and unverifiable protected state fail closed.
5. Invalidating one graph node affects exactly that node and real descendants, not unrelated branches.
6. Unaffected state is reusable only when an `ALLOW` verification result is cryptographically bound to the exact current checkpoint payload.
7. A consequential action remains blocked until every path-specific required re-verification succeeds.
8. Replay/idempotency conflict cannot be silently treated as a duplicate success.
9. Persisted history is not trusted merely because it exists; SQLite state is reconstructed and verification bindings are checked on load.
10. Signed receipts authenticate bytes only under configured key trust; signatures do not prove upstream evidence truth.
11. Unknown/revoked keys, unsupported algorithms, malformed signatures and provider failures fail closed; retired keys may verify historical receipts but must not sign new receipts.
12. Framework/adaptor lifecycle failure must not create an implicit `ALLOW` when EvidenceBound verification did not complete.

## Primary source scope

Review at minimum:

- `src/evidencebound/canonical.py` — EBCJ-1 canonicalization and domain-separated hashing;
- `src/evidencebound/models.py` — public trust contracts;
- `src/evidencebound/verification.py` — evidence/provenance/policy/integrity/applicability decisions and receipts;
- `src/evidencebound/signing.py` and optional signing provider(s) — signing contract, algorithm/key state and failure semantics;
- `src/evidencebound/graph.py` — DAG validation and ancestry/descendant traversal;
- `src/evidencebound/recovery.py` — reusable/recompute/reverify/blocked separation and path-specific requirements;
- `src/evidencebound/replay.py` — duplicate/conflict semantics;
- `src/evidencebound/persistence.py` plus SQLite provider — serialization, transactions, reopen/reverification, corruption and schema handling;
- `src/evidencebound/api.py` — high-level state transitions and integration facade;
- `src/evidencebound/adapters/` — plain-Python and framework lifecycle seams;
- `compat/` — real upstream compatibility acceptance;
- `tools/validate_supply_chain.py` and `.github/workflows/ci.yml` — supply-chain evidence boundaries.

Review the matching unit, adversarial, persistence, signing, graph/recovery, conformance/property and compatibility tests as evidence of intended behavior, but do not treat passing tests as proof that the implementation is secure.

## High-priority attack hypotheses

### Canonicalization and binding

- semantically distinct values serialize identically;
- semantically equivalent values unexpectedly diverge across supported use;
- Unicode, escaping, key ordering, integer boundaries or unsupported types bypass expected binding;
- domain separation is omitted at a security-sensitive digest call site;
- receipt fields can be transplanted between checkpoints/policies/results.

EBCJ-1 is EvidenceBound-specific and is **not** claimed to be RFC 8785/JCS.

### Evidence and provenance

- current-evidence mapping identity confusion;
- duplicate evidence IDs;
- provenance dropped or substituted without blocking;
- changed/stale/new evidence incorrectly remains `ALLOW`;
- `REFUTED` reachable from mere digest inequality;
- timestamp parsing or timezone handling produces unsafe applicability.

### Policy/version drift

- stale verification reused under another policy id/version;
- policy compatibility omitted from a consequential path;
- policy metadata can be altered without receipt/checkpoint binding failure.

### Signed receipts and key lifecycle

- wrong-key, unknown-key, revoked-key or unsupported-algorithm acceptance;
- signing with a retired key;
- verifier/provider exceptions converted to success;
- signature encoding ambiguity or canonical payload mismatch;
- key identifiers or algorithm metadata not bound to what was verified.

The review should explicitly separate signature authenticity from evidence truth and from authorization to perform an application action.

### Dependency graph and recovery

- graph cycles or missing dependencies accepted;
- blast radius over-invalidates unrelated branches or under-invalidates descendants;
- a verification result for one checkpoint is reused for another payload;
- path-specific re-verification omits a required ancestor;
- a consequential node becomes allowed after only a partial re-verification sequence.

### Persistence, restart and replay

- partial transaction state becomes trusted after restart;
- stored verification is accepted without reconstructing/checking its receipt binding;
- schema/version confusion leads to permissive fallback;
- SQLite corruption or malformed rows become trusted values;
- replay records are not atomically consistent with checkpoint/verification persistence;
- duplicate and conflict outcomes become indistinguishable after restart.

SQLite is a reference local backend. It is not claimed to provide immutable, authenticated or distributed storage.

### Framework/adaptor boundaries

- callback/lifecycle is skipped but application proceeds;
- malformed third-party context is interpreted as `ALLOW`;
- exceptions/timeouts fail open;
- optional provider/framework dependencies leak into the core runtime;
- adapter code smuggles application-specific policy into EvidenceBound core.

### Build and supply chain

- SBOM/checksum subjects differ from attested build subjects;
- PR code receives trusted-main OIDC/attestation write permissions;
- mutable action references are used where exact pins are required by project policy;
- clean-room wheel differs materially from the code exercised in tests;
- provenance is overstated as evidence authenticity or upstream truth.

## Known limitations / explicit non-claims

A finding should not be based solely on the absence of a guarantee the project does not claim:

- EvidenceBound does not establish that upstream evidence is factually true.
- Hashes are tamper-detection/binding mechanisms, not truth or authorization oracles.
- Signatures authenticate signed bytes under configured trust roots; they do not establish factual correctness.
- `v0.3.0` was published before the later trusted-main attestation workflow and is not retroactively attested by it.
- Property tests are engineering evidence, not formal verification.
- The project does not claim exactly-once side effects across arbitrary external systems.
- No external security audit has been completed as of this packet.
- No independent external adopter is claimed as of this packet.
- PyPI publication has not been performed.

## Reproducibility baseline

Use an isolated environment and the exact review SHA. The repository CI is the source of truth for the currently supported command set. At the packet baseline, applicable checks include:

```bash
python -m pip install -e '.[dev]'
pytest
python examples/golden_acceptance.py
python benchmarks/selective_recovery.py
ruff check .
mypy src/evidencebound --show-error-codes
python -m build
python -m pip_audit --progress-spinner=off .
bandit -r src/evidencebound -q
```

The CI additionally exercises Python 3.10–3.13, clean-room package installation, PEP 561 packaging, real Google ADK compatibility, checksum/SBOM generation and trusted-main attestations.

Historical accepted evidence before this intake packet:

- release-source CI `31991997448` for `v0.3.0` source;
- signed-receipt exact-main CI `31993226080`;
- SQLite persistence exact-main CI `31994016152`;
- Google ADK compatibility exact-main CI `31994792165`;
- conformance/property exact-main CI `31995166680`;
- supply-chain exact-main CI `31995557238`;
- post-hardening truth-sync exact-main CI `31995867781` at `16e6e5915bcbb0888e297a5162770198fb7e38ce`.

Reviewers should independently rerun relevant checks rather than relying on these historical run IDs.

## Requested review output

Preferred output is a report containing:

- exact reviewed commit SHA(s);
- methodology and scope;
- findings with severity and affected code paths;
- reproduction steps or proof-of-concept where disclosure is safe;
- recommended remediation;
- retest status after fixes;
- residual risk / accepted-risk notes;
- a statement of areas not reviewed.

A professional audit is preferred, but a well-scoped independent expert review with attributable findings is still valuable if the reviewer clearly states its limits.

## Disclosure

For suspected vulnerabilities that should not be public before remediation, follow `SECURITY.md` and use GitHub private vulnerability reporting / security advisory mechanisms where available. Do not place secrets, private provider payloads, production data or exploitable unpublished vulnerability details in a public issue.

Public issue #23 tracks scheduling/status only. Security-impact details may remain private until coordinated disclosure.
