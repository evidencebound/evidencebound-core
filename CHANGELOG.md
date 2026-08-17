# Changelog

All notable changes are documented here. The project follows Semantic Versioning for published releases, with pre-1.0 APIs allowed to change when documented.

## [Unreleased]

### Added
- provider-neutral `ReceiptSigner` / `ReceiptVerifier` protocols and detached `SignedProofReceipt` envelopes;
- explicit ACTIVE / RETIRED / REVOKED / UNKNOWN signing-key lifecycle semantics;
- fail-closed signed-receipt verification statuses for malformed signatures, unknown/revoked keys, unsupported algorithms, provider errors and receipt/checkpoint binding failures;
- optional `crypto` extra with an Ed25519 reference provider while preserving zero unconditional runtime dependencies;
- signed-receipt migration/security documentation and adversarial tests;
- provider-neutral `PersistenceStore` contract for durable checkpoint/receipt/verification/replay state;
- stdlib `SQLiteStore` and `SQLiteReplayGuard` reference providers with explicit transaction and schema/version semantics;
- restart, persisted-tamper, transaction crash-injection, replay persistence and graph-reconstruction tests;
- durable persistence/recovery documentation;
- pinned real-framework compatibility CI for `google-adk==2.7.0` on Python 3.13 using real `BaseAgent`, `Runner`, callback validation, event streaming and `InMemorySessionService` without model/cloud credentials;
- dependency-free `adk_consequential_action_allowed()` application gate that requires explicit serialized EvidenceBound `ALLOW` callback state.

### Hardened
- legacy unsigned receipts remain distinguishable as `UNSIGNED` and are never silently upgraded to authenticated trust;
- retired keys may verify historical receipts but cannot create new signatures through core;
- algorithm, key ID, receipt/version/canonicalization metadata are covered by the detached signed payload;
- persisted verification state is re-bound to the exact stored checkpoint/receipt on load rather than trusted because it was previously stored;
- partial SQLite bundle writes roll back before commit, and unknown/incomplete persistence schemas fail closed rather than being silently repaired;
- durable replay records preserve duplicate/conflict semantics across restart but do not imply exactly-once execution or authorization to reuse mismatched checkpoint state;
- Google ADK event consumption is fail-closed: a completed v2.7.0 lifecycle persists EvidenceBound verification before the consequential gate allows action, while deliberately closing the real async event stream before the after-agent callback leaves verification missing and the gate blocked;
- `google-adk` remains isolated from EvidenceBound runtime dependencies and Core imports.

## [0.3.0] - 2026-08-17

### Added
- independent stdlib-only Python core and typed contracts;
- EBCJ-1 deterministic canonicalization and domain-separated SHA-256;
- integrity/applicability separation and fail-closed verification;
- explicit `UNCHANGED`, `NEW`, `CHANGED`, `STALE`, `MISSING`, and `REFUTED` evidence semantics;
- tamper-evident checkpoint receipts plus verification-result receipt validation;
- exact dependency blast radius and selective recovery planning;
- `reusable`, `requires_verification`, `recompute`, and `blocked` recovery separation;
- path-specific post-recovery consequential action gate;
- replay/idempotency guard;
- provider-neutral structured event hooks;
- plain Python and dependency-free Google ADK callback integration seams;
- threat model, specification, adoption/funding docs, benchmark and release checklist;
- Python 3.10-3.13 CI, clean-room installation, Ruff, strict mypy, package build, pip-audit and Bandit gates.

### Hardened
- hash changes never imply `REFUTED` without explicit upstream refutation;
- duplicate evidence IDs reject/fail closed;
- current evidence mapping keys must match contained evidence IDs;
- unaffected state is reusable only with an `ALLOW` result bound to the exact graph checkpoint payload;
- unrelated invalidations cannot become false prerequisites for independent branches;
- receipt policy/version/result/digest tampering fails verification;
- package licensing metadata uses an SPDX expression rather than deprecated setuptools metadata.

GitHub source release `v0.3.0` was published from exact accepted commit `2477164acfbdca6a843bf7b2eac5fa21ce9901b2` after CI run `31991997448` completed successfully. PyPI publication is a separate distribution action and is **not** implied by this changelog.
