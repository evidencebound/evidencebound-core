# Changelog

All notable changes are documented here. The project follows Semantic Versioning for published releases, with pre-1.0 APIs allowed to change when documented.

## [Unreleased]

No user-facing changes recorded yet.

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
