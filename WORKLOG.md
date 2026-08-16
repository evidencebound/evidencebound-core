# Autonomous Worklog

## 2026-08-16

### Reality refresh and extraction
- Reviewed current EvidenceBound reference repositories and the SignalReview boundary before implementation.
- Chose `moneyparking/EvidenceBound-OSS-Core-Funding-Adoption` as the independent public OSS repository; it initially contained only an initial README.
- Kept cloud/hackathon/product implementations as reference material rather than mechanically merging their code.
- Locked the core boundary as stdlib-only Python, framework/cloud/LLM independent, with structured deterministic inputs and outputs.

### v0.1 — independent core
- Added typed evidence, provenance, policy, checkpoint, verification and receipt contracts.
- Added versioned `EBCJ-1` deterministic canonicalization and domain-separated SHA-256 binding.
- Separated historical integrity from current applicability.
- Added fail-closed `ALLOW` / `REVIEW_REQUIRED` / `BLOCK` semantics.
- Added tamper detection, missing evidence/provenance handling and policy-version binding.
- Preserved the invariant `hash changed != REFUTED`.

### v0.2 — graph and recovery
- Added deterministic DAG validation, ancestors/descendants and exact blast-radius invalidation.
- Added selective recovery, replay/idempotency guard and provider-neutral structured events.
- Added plain Python integration and a dependency-free Google ADK callback seam.
- Hardened recovery so unverified unaffected state is not labeled reusable.
- Bound reusable verification to the exact graph checkpoint payload.
- Added path-specific re-verification requirements so unrelated invalidations do not contaminate independent branches.
- Added explicit `NEW` semantics, duplicate evidence-ID rejection and current-evidence identity binding.

### v0.3 — public API, security, adoption and funding readiness
- Added README, architecture, specification, threat model, security policy, contribution guide, roadmap, changelog, integration/troubleshooting docs, pre-existing-work boundary and Apache-2.0 license decision.
- Added reproducible selective-recovery benchmark and executable golden acceptance.
- Added Python 3.10–3.13 CI, Ruff, strict mypy, build/wheel reinstall, clean-room install, pip-audit and Bandit.
- Pinned GitHub Actions by exact commit SHA.
- Added Dependabot, issue templates, adoption docs and grounded funding work packages/matrix.

### Merged hardening history
- PR #1 -> `main` `6ca6ff78abf0012f4d7c216497394e9edb848bd1`: independent core candidate; exact-main CI `31968100914` SUCCESS.
- PR #2 -> `main` `56aba73a0a5cb12b539740a3720d3629310232f6`: explicit clean-room acceptance; exact-main CI `31968333678` SUCCESS.
- PR #3 -> `main` `c1ba29d748157001a31521f47b0358f0f29862ac`: graph-bound reusable state, receipt verification and path-specific recovery; exact-main CI `31968624967` SUCCESS.
- PR #4 -> `main` `6317d0701a7873c4711357bd140062aac00965d1`: current evidence identity mismatch fail-closed; exact-main CI `31968785923` SUCCESS.

### Latest accepted main evidence before release-readiness metadata wave
- Exact `main`: `6317d0701a7873c4711357bd140062aac00965d1`.
- CI run `31968785923`: SUCCESS.
- Python 3.10 / 3.11 / 3.12 / 3.13 jobs: SUCCESS.
- Python 3.13 pytest: **32 passed in 0.12s**.
- Golden acceptance: PASS.
- Ruff: PASS.
- strict mypy: PASS (`12 source files`).
- sdist/wheel build: PASS.
- wheel reinstall/import: PASS.
- clean-room fresh-venv runtime-only install/plain/golden/no-unconditional-runtime-dependency gate: PASS.
- pip-audit and Bandit jobs: PASS.

### Release-readiness wave
Active branch: `agent/v0.3-release-readiness`.

Changes in this wave are release engineering/documentation rather than new trust semantics:
- modernize setuptools license metadata to SPDX `Apache-2.0` and declare `LICENSE` explicitly;
- remove deprecated license classifier;
- raise build-backend floor to a setuptools version supporting the modern metadata;
- make the 100-node selective-recovery benchmark counts executable assertions and run it in CI;
- align README/SPEC/CHANGELOG with accepted trust semantics;
- add `RELEASE_READINESS.md` and `docs/RELEASE_CHECKLIST.md`.

This branch is not releasable merely because earlier `main` was green; it must pass its own exact-head CI and then exact-main CI after merge.

### Distribution boundary
- GitHub `v0.3.0` tag/release: not yet created.
- PyPI: not published; namespace/account ownership is not sufficiently verified for autonomous publication.
