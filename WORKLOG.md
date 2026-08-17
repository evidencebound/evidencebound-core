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
- PR #11 -> `main` `9a4aa995d7cd71d14443369ced5ae6b220c5cb86`: canonical repo rename links/metadata/badges; exact-main CI `31991814352` SUCCESS.
- PR #12 -> `main` `2477164acfbdca6a843bf7b2eac5fa21ce9901b2`: guarded release publisher; exact-main CI `31991997448` SUCCESS.

### v0.3.0 publication
- Exact accepted release source: `2477164acfbdca6a843bf7b2eac5fa21ce9901b2`.
- Release-source CI: `31991997448` — SUCCESS.
- Release publisher run: `31992021940` — SUCCESS.
- `refs/tags/v0.3.0` independently fetched and verified to resolve exactly to the accepted release source.
- GitHub Release `EvidenceBound Core v0.3.0` independently fetched and verified public, non-draft and non-prerelease.
- Release date: 2026-08-17.
- PyPI publication: NOT PERFORMED / NOT CLAIMED.

### Release-source acceptance
- Python 3.10 / 3.11 / 3.12 / 3.13: SUCCESS.
- Python 3.13 pytest: **32 passed**.
- Golden acceptance: PASS.
- Synthetic benchmark: 100 full restart / 25 recompute / 75 reusable / 0 requires verification / 75 avoided.
- Ruff: PASS.
- strict mypy: PASS across 12 source files.
- sdist/wheel build and reinstall/import: PASS.
- PEP 561 `py.typed`: PASS.
- clean-room runtime-only install/plain/golden/no-unconditional-runtime-dependency gate: PASS.
- pip-audit and Bandit: PASS.

### Post-release consistency wave
Branch: `agent/post-v0.3-release-sync`.

Scope is documentation/release-state cleanup only:
- mark README/CHANGELOG/CITATION as released `v0.3.0`;
- record immutable release evidence in readiness/handoff/worklog;
- update funding readiness so a public release is no longer listed as missing;
- remove the one-time publisher workflow to prevent future main CI runs from attempting to republish `v0.3.0`.

### Grounded funding/adoption backlog
- #7 signed receipt provider protocol and algorithm agility;
- #8 crash-consistent SQLite persistence/restart recovery;
- #9 maintained real Google ADK callback lifecycle compatibility CI.

These issues are work packages, not claims that the capabilities already exist. Independent external adoption, external security review, cross-runtime conformance and release provenance/SBOM remain unfinished.
