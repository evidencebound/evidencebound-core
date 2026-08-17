# Autonomous Worklog

## 2026-08-16 — 2026-08-17

### Reality refresh and extraction
- Reviewed current EvidenceBound reference repositories and the SignalReview boundary before implementation.
- Initialized the independent public OSS repository under legacy slug `moneyparking/EvidenceBound-OSS-Core-Funding-Adoption`; it initially contained only an initial README.
- Renamed the canonical repository on 2026-08-17 to `moneyparking/evidencebound-core` without changing repository identity/history.
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
- PR #5 -> `main` `f1dace847af3e2073f06e8410dc422a929823941`: release-readiness metadata, benchmark CI acceptance and modern license metadata; exact-main CI `31969049837` SUCCESS.
- PR #6 -> `main` `ffb4aa2ed317640b76f2590c859dfc60d533be28`: PEP 561 typed distribution, project URLs, governance/citation metadata and fail-closed ADK lifecycle guidance; exact-main CI `31990753200` SUCCESS.
- PR #10 -> `main` `4bed13c0a2b5113e7e9b90aa2b3d92a1c3d7adcd`: final pre-rename acceptance evidence sync; exact-main CI `31990950455` SUCCESS.

### Latest accepted main evidence before repository-rename consistency wave
At `main` `4bed13c0a2b5113e7e9b90aa2b3d92a1c3d7adcd` under canonical repository `moneyparking/evidencebound-core`:

- CI run `31990950455`: SUCCESS.
- Python 3.10 / 3.11 / 3.12 / 3.13 jobs: SUCCESS.
- Python 3.13 pytest: **32 passed in 0.12s**.
- Golden acceptance: PASS.
- Selective-recovery benchmark acceptance: PASS (`100` full restart / `25` recompute / `75` reusable / `0` requires verification / `75` avoided in the synthetic scenario).
- Ruff: PASS.
- strict mypy: PASS (`12 source files`).
- sdist/wheel build: PASS.
- wheel reinstall/import: PASS.
- PEP 561 `py.typed` present in built wheel: PASS.
- clean-room runtime-only install + typing marker + plain/golden + no-unconditional-runtime-dependency gate: PASS.
- pip-audit and Bandit: PASS.

### Repository rename consistency wave
Branch: `agent/repo-rename-consistency`.

Scope is metadata/documentation only; runtime source and trust semantics are unchanged:
- update `[project.urls]` to `https://github.com/moneyparking/evidencebound-core`;
- add canonical README CI/Python/license badges;
- update `CITATION.cff`;
- make SECURITY/funding/release docs point to the canonical repository;
- preserve the prior long repository name only as explicit historical/legacy context;
- require exact-head CI and exact-main CI before tagging `v0.3.0`.

### Grounded funding/adoption backlog
Created public issues for real unfinished work:

- #7 signed receipt provider protocol and algorithm agility;
- #8 crash-consistent SQLite persistence/restart recovery;
- #9 maintained real Google ADK callback lifecycle compatibility CI.

These issues are work packages, not claims that the capabilities already exist.

### Distribution boundary
- GitHub `v0.3.0` tag/release: NOT CREATED / NOT VERIFIED.
- PyPI: NOT PUBLISHED.
- Independent external adopter: NOT VERIFIED.
- The current release target must always be re-resolved from `main` after the latest docs/code merge and exact-main CI; no SHA embedded in this worklog is a permanent tag target.
