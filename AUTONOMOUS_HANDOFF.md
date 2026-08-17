# Autonomous Handoff

## Canonical repository

- Repository: `moneyparking/evidencebound-core`
- URL: https://github.com/moneyparking/evidencebound-core
- Visibility: public
- Canonical branch: `main`
- Published release: `v0.3.0`
- Release source SHA: `2477164acfbdca6a843bf7b2eac5fa21ce9901b2`
- Release-source exact-main CI: run `31991997448` — SUCCESS
- Release publisher: run `31992021940` — SUCCESS
- Release URL: https://github.com/moneyparking/evidencebound-core/releases/tag/v0.3.0
- Active post-release branch: `agent/post-v0.3-release-sync`

The release tag is fixed historical evidence. Never move `v0.3.0` to a later `main` commit to make documentation catch up.

## Milestone state

- v0.1 independent core: PASS.
- v0.2 trust graph/selective recovery: PASS.
- v0.3 technical/adoption/security acceptance: PASS.
- GitHub `v0.3.0` source release: PUBLISHED / VERIFIED.
- PyPI: NOT PUBLISHED.
- Independent external adopter: NOT YET VERIFIED.

## Latest proven release gates

At tagged commit `2477164acfbdca6a843bf7b2eac5fa21ce9901b2`:

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
- Synthetic selective-recovery benchmark: 100 full restart / 25 recompute / 75 reusable / 0 requires-verification / 75 avoided.
- Ruff and strict mypy: SUCCESS.
- sdist/wheel build, reinstall/import and PEP 561 marker: SUCCESS.
- Clean-room runtime-only install/plain/golden/no-unconditional-runtime-dependency gate: SUCCESS.
- pip-audit and Bandit: SUCCESS.

## Release history

- PR #11 synchronized the repository rename to `moneyparking/evidencebound-core`; exact-main run `31991814352` succeeded.
- PR #12 added a guarded one-time publisher; exact-head CI succeeded.
- `main` `2477164acfbdca6a843bf7b2eac5fa21ce9901b2` passed exact-main run `31991997448`.
- Publisher run `31992021940` created `refs/tags/v0.3.0` and the GitHub Release, then re-read both objects and succeeded.
- Independent API verification confirmed the tag target and public Release metadata.

## Grounded post-v0.3 work packages

- #7 — signed receipt provider protocol with algorithm agility;
- #8 — crash-consistent SQLite persistence adapter and restart/recovery tests;
- #9 — maintained Google ADK end-to-end callback lifecycle compatibility CI.

Additional gaps remain: cross-runtime canonicalization/conformance fixtures, property/fuzz/formal state-machine testing, external security review, SBOM/release provenance, and independent external adoption.

## Next autonomous focus

1. Keep release `v0.3.0` immutable at its verified SHA.
2. Remove the one-time publisher from post-release `main` and keep CI green.
3. Pursue external-style integration evidence and the real work packages above rather than inflating release claims.
4. Re-evaluate funding targets against current official calls when an application is being prepared.
5. Treat PyPI as a separate distribution decision requiring namespace/account verification and a post-upload clean install.
