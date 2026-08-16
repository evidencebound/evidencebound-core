# Autonomous Worklog

## 2026-08-16

### Reality refresh and extraction
- Reviewed current EvidenceBound reference repositories and the SignalReview boundary before implementation.
- Chose `moneyparking/EvidenceBound-OSS-Core-Funding-Adoption` as the independent public OSS repository. It initially contained only an initial README.
- Kept cloud/hackathon/product implementations as reference material rather than mechanically merging their code.
- Locked the core boundary as stdlib-only Python, framework/cloud/LLM independent, with structured deterministic inputs and outputs.

### v0.1 — independent core
- Added typed evidence, provenance, policy, checkpoint, verification and receipt contracts.
- Added versioned `EBCJ-1` deterministic canonicalization and domain-separated SHA-256 binding.
- Separated historical integrity from current applicability.
- Added fail-closed outcomes: `ALLOW`, `REVIEW_REQUIRED`, `BLOCK`.
- Added tamper detection, missing evidence/provenance handling and policy-version binding.
- Explicitly preserved `hash changed != REFUTED`.

### v0.2 — graph and recovery
- Added deterministic DAG validation, ancestors/descendants and exact blast-radius invalidation.
- Added selective recovery with reusable/recompute/blocked sets.
- Added replay/idempotency guard without an exactly-once claim.
- Added provider-neutral structured events.
- Added plain Python integration and a dependency-free Google ADK callback seam checked against the current upstream callback shape.
- Hardened recovery so a consequential action remains blocked until every affected recompute prerequisite has an `ALLOW` re-verification result.
- Added explicit `NEW` current-evidence semantics and duplicate evidence-ID rejection/fail-closed behavior.

### v0.3 — public API, security, adoption and funding readiness
- Added README, architecture, specification, threat model, security policy, contribution guide, roadmap, changelog, integration/troubleshooting docs, pre-existing-work boundary and Apache-2.0 license decision.
- Added reproducible selective-recovery benchmark. Scenario: 100-node linear graph, invalidate node 75 -> 25 recompute, 75 reusable, 75 recomputations avoided. This is scenario-specific, not a universal savings claim.
- Added Python 3.10-3.13 CI, Ruff, strict mypy, package build, wheel reinstall/import, pip-audit and Bandit.
- GitHub Actions are pinned to exact current Node24-native action SHAs.
- Added Dependabot configuration and candidate contributor issue templates.
- Added grounded funding-readiness work packages and a point-in-time funding-target matrix.

### Executed gates
- Local progression exposed and repaired real regressions rather than treating the first green run as acceptance.
- Final pre-merge local suite: **27 tests PASS**.
- Plain Python example: PASS.
- Golden external acceptance: PASS.
- Synthetic recovery benchmark: PASS.
- Compileall: PASS.
- Local wheel build using installed build backend: PASS.
- Fresh local wheel venv import: PASS.
- Branch exact-head CI `2a1ab0a38792693c252a6975f361c0e92457bdc1`, run `31968014291`: SUCCESS, including all test, lint, strict type, build, clean-wheel import, pip-audit and Bandit gates.
- PR #1 was squash-merged to `main` as `6ca6ff78abf0012f4d7c216497394e9edb848bd1`.
- Exact-main push CI run `31968100914` on that merge commit: SUCCESS.

### Current hardening wave
- Branch `agent/public-clean-room-acceptance` adds an explicit clean-room gate: fresh GitHub checkout -> fresh venv -> `pip install .` with runtime-only package -> plain Python example -> golden acceptance -> assert no declared runtime dependencies.
- This wave also refreshes autonomous handoff evidence. Its CI/merge status must be checked at the exact head before release/tag claims.

### Known distribution boundary
- No PyPI publication has been performed. Package-name ownership/availability is not considered verified enough for autonomous publication.
