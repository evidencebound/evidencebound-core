# Autonomous Handoff

## Canonical repository

- Repository: `moneyparking/EvidenceBound-OSS-Core-Funding-Adoption`
- Visibility: public
- Canonical branch: `main`
- Last fully verified `main` before release-readiness metadata wave: `6317d0701a7873c4711357bd140062aac00965d1`
- Exact-main CI: run `31968785923` — SUCCESS
- Active branch: `agent/v0.3-release-readiness`

Never use the SHA embedded in this file as a substitute for fetching the current branch/main ref. The exact commit containing a release must be re-verified after any metadata or documentation merge.

## Milestone state

- v0.1 independent core: PASS on accepted main.
- v0.2 trust graph/selective recovery: PASS on accepted main.
- v0.3 technical feature/adoption/security acceptance: PASS on accepted main.
- v0.3.0 GitHub tag/release: NOT CREATED / NOT VERIFIED.
- PyPI: NOT PUBLISHED.

## Latest proven gates

At accepted main `6317d0701a7873c4711357bd140062aac00965d1`:

- Python 3.10–3.13 CI matrix SUCCESS.
- Python 3.13: 32 pytest tests PASS.
- Protected payload tamper -> integrity failure -> BLOCK.
- Historical integrity VERIFIED can coexist with current applicability REVIEW_REQUIRED.
- Hash change -> CHANGED, never implicit REFUTED.
- Missing/refuted evidence, provenance loss, duplicate evidence IDs and evidence identity mismatch fail closed.
- DAG cycle/missing dependency/duplicate checkpoint rejection.
- Exact descendant-only blast radius across branch/diamond cases.
- Unverified unaffected state is not reusable.
- Reusable verification is receipt-bound to the exact graph checkpoint payload.
- Consequential recovery uses path-specific re-verification requirements.
- Replay duplicate/conflict semantics.
- Plain Python and dependency-free Google ADK integration seams.
- Golden external acceptance SUCCESS.
- Clean-room fresh checkout/venv/runtime-only install/plain/golden SUCCESS.
- Ruff, strict mypy, sdist/wheel build and clean-wheel import SUCCESS.
- pip-audit and Bandit SUCCESS.

## Current release-readiness branch

The branch changes package/release metadata and benchmark gating. Required next actions:

1. Run exact-head CI on `agent/v0.3-release-readiness`.
2. Repair every failing test/lint/type/build/clean-room/security/benchmark gate.
3. Inspect build logs and confirm deprecated license-metadata warnings are removed.
4. Merge only after branch CI is fully green.
5. Verify exact resulting `main` CI is fully green.
6. Resolve current `main` SHA and use that exact SHA as the only valid `v0.3.0` tag target.
7. Create/fetch/verify GitHub tag and release only with a release-capable authenticated tool or explicit owner UI action.
8. Do not claim PyPI publication until registry/account ownership and post-upload clean install are verified.

## Remaining post-v0.3 engineering gaps

- signed receipts/key-provider interface;
- persistence backend protocol and crash-consistency tests;
- cross-runtime canonicalization/conformance fixtures;
- property/fuzz and formal state-machine testing;
- maintained upstream-framework compatibility CI;
- external security review and release provenance/SBOM;
- at least one integration by a project not owned by the maintainer.
