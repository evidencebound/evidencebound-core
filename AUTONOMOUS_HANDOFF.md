# Autonomous Handoff

## Canonical repository

- Repository: `moneyparking/evidencebound-core`
- URL: https://github.com/moneyparking/evidencebound-core
- Visibility: public
- Canonical branch: `main`
- Latest fully verified `main` before this rename-consistency commit: `4bed13c0a2b5113e7e9b90aa2b3d92a1c3d7adcd`
- Exact-main CI: run `31990950455` — SUCCESS
- Active branch for this consistency wave: `agent/repo-rename-consistency`

The SHA embedded here is historical acceptance evidence, not a permanent release target. Before creating a tag or release, fetch the current `main` ref again and verify CI for that exact SHA.

## Milestone state

- v0.1 independent core: PASS on accepted `main`.
- v0.2 trust graph/selective recovery: PASS on accepted `main`.
- v0.3 technical feature/adoption/security acceptance: PASS on accepted `main`.
- v0.3 package metadata: `0.3.0` release candidate.
- GitHub `v0.3.0` tag/release: NOT CREATED / NOT VERIFIED.
- PyPI: NOT PUBLISHED.
- Independent external adopter: NOT YET VERIFIED.

## Latest proven gates

At accepted `main` `4bed13c0a2b5113e7e9b90aa2b3d92a1c3d7adcd`, GitHub Actions run `31990950455` is SUCCESS.

- Python 3.10 / 3.11 / 3.12 / 3.13 jobs: SUCCESS.
- Python 3.13 pytest: **32 passed**.
- Protected payload tamper -> integrity failure -> `BLOCK`.
- Historical integrity `VERIFIED` can coexist with current applicability `REVIEW_REQUIRED`.
- Digest change -> `CHANGED`, never implicit `REFUTED`.
- Missing/refuted evidence, required provenance loss, duplicate evidence IDs and current-evidence identity mismatch fail closed.
- DAG cycle/missing dependency/duplicate checkpoint rejection.
- Exact descendant-only blast radius across branch/diamond cases.
- Unverified unaffected state is not reusable.
- Reusable verification is receipt-bound to the exact graph checkpoint payload.
- Consequential recovery uses path-specific re-verification requirements.
- Replay duplicate/conflict semantics.
- Plain Python and dependency-free Google ADK integration seams.
- Golden external acceptance: SUCCESS.
- Selective-recovery benchmark acceptance: 100 full restart / 25 recompute / 75 reusable / 0 requires-verification / 75 avoided in the synthetic scenario.
- Ruff: SUCCESS.
- strict mypy: SUCCESS across 12 source files.
- sdist/wheel build and wheel reinstall/import: SUCCESS.
- PEP 561 `py.typed` marker verified in the built wheel and clean-room installation.
- Clean-room fresh-venv runtime-only install/plain/golden/no-unconditional-runtime-dependency gate: SUCCESS.
- pip-audit and Bandit: SUCCESS.

## Adoption/release hardening merged

PR #5 prepared v0.3 release metadata and made the benchmark an executable CI gate.

PR #6 added PEP 561 package typing, project metadata URLs, maintainer-led governance, citation metadata and explicit fail-closed Google ADK lifecycle guidance. It changed no trust-engine semantics and passed full exact-head plus exact-main acceptance.

PR #10 synchronized final pre-rename v0.3 acceptance evidence and merged as `4bed13c0a2b5113e7e9b90aa2b3d92a1c3d7adcd`; exact-main CI `31990950455` succeeded.

The repository was then renamed from legacy slug `moneyparking/EvidenceBound-OSS-Core-Funding-Adoption` to canonical `moneyparking/evidencebound-core`; repository identity/history were preserved by GitHub.

## Grounded post-v0.3 work packages

Open issues describe unfinished work rather than claimed capabilities:

- #7 — signed receipt provider protocol with algorithm agility;
- #8 — crash-consistent SQLite persistence adapter and restart/recovery tests;
- #9 — maintained Google ADK end-to-end callback lifecycle compatibility CI.

Additional real gaps remain: cross-runtime canonicalization/conformance fixtures, property/fuzz and formal state-machine testing, external security review, SBOM/release provenance, and at least one integration by a project not owned by the maintainer.

## Next exact actions

1. Merge the rename-consistency PR only after its exact-head CI is fully green.
2. Verify the resulting exact `main` push CI under `moneyparking/evidencebound-core`.
3. Fetch the resulting current `main` SHA; that SHA is the only valid candidate target for `v0.3.0`.
4. Create and independently fetch/verify the GitHub `v0.3.0` tag and release at that exact accepted SHA.
5. Do not claim PyPI publication until namespace/account ownership and a post-upload clean installation are verified.
