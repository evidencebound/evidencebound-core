# v0.3.0 Release Evidence

## Status

**EvidenceBound Core v0.3.0 is published as a GitHub source release and independently verified.**

Technical acceptance and publication remain separate evidence layers; both are recorded below. PyPI publication is a separate distribution action and has not occurred.

## Verified release source

- Repository: `moneyparking/evidencebound-core`
- URL: https://github.com/moneyparking/evidencebound-core
- Visibility: public
- Tag: `v0.3.0`
- Tag target SHA: `2477164acfbdca6a843bf7b2eac5fa21ce9901b2`
- Exact-main CI before publication: run `31991997448` — SUCCESS
- Release publisher run: `31992021940` — SUCCESS
- GitHub Release: https://github.com/moneyparking/evidencebound-core/releases/tag/v0.3.0
- Release title: `EvidenceBound Core v0.3.0`
- Published: 2026-08-17
- Draft: false
- Prerelease: false

The `v0.3.0` tag is intentionally fixed to the accepted release source. Later documentation or development commits on `main` do not move this tag.

## Acceptance evidence at tagged source

- Python 3.10 / 3.11 / 3.12 / 3.13: SUCCESS.
- Python 3.13 pytest: **32 passed**.
- Golden acceptance: SUCCESS.
- Selective-recovery benchmark acceptance: SUCCESS.
- Ruff: SUCCESS.
- strict mypy: SUCCESS across 12 source files.
- sdist/wheel build and reinstall/import: SUCCESS.
- built-wheel PEP 561 `py.typed`: VERIFIED.
- clean-room runtime-only install + typing marker + plain example + golden acceptance: SUCCESS.
- no unconditional runtime dependency assertion: SUCCESS.
- pip-audit: SUCCESS.
- Bandit core-source scan: SUCCESS.

## Acceptance invariants represented in tests

1. protected payload tamper with retained receipt -> integrity failure -> `BLOCK`;
2. historical integrity `VERIFIED` can coexist with current applicability `REVIEW_REQUIRED`;
3. digest change -> `CHANGED`, never implicit `REFUTED`;
4. missing/refuted evidence, required provenance loss, duplicate evidence IDs, or current evidence identity mismatch fail closed;
5. graph cycle/missing dependency/duplicate checkpoint IDs reject;
6. invalidating a node affects only that node and real descendants;
7. unaffected state is `reusable` only with an `ALLOW` verification receipt bound to the exact checkpoint payload in the current graph;
8. unrelated branch invalidation does not become a false recovery prerequisite;
9. consequential actions remain blocked until path-specific required checkpoints are successfully re-verified;
10. replay guard rejects one operation ID reused with a different payload.

## Reproducible benchmark acceptance

`benchmarks/selective_recovery.py` constructs a verified synthetic 100-node linear workflow and invalidates node `n075`.

Asserted scenario-specific result:

- full restart nodes: 100;
- selective recompute: 25;
- reusable: 75;
- requires verification: 0;
- recomputations avoided: 75.

Elapsed time is scenario telemetry only, not a universal performance claim.

## Package/release engineering

- Python runtime requirement: `>=3.10`.
- Unconditional runtime dependencies: none.
- Build backend: setuptools.
- License metadata: SPDX `Apache-2.0`, with `LICENSE` included in built artifacts.
- PEP 561 typed-package marker is included and verified after wheel installation.
- Repository/issues/changelog/documentation URLs point to `moneyparking/evidencebound-core`.
- GitHub Actions dependencies are pinned by commit SHA.
- Dependency and static-security scans are explicit CI jobs.
- Maintainer-led governance is documented; no external governance body is claimed.
- `CITATION.cff` identifies version `0.3.0` and the release date.

## Adapter boundary

The Google ADK seam remains dependency-free. Consequential integrations must wait for callback completion and a present EvidenceBound `ALLOW` result; a missing callback result or prematurely stopped lifecycle is unverified/blocked. Real upstream ADK compatibility CI remains unfinished work tracked in issue #9.

## Publication audit

The repository intentionally excludes SignalReview commercial logic, provider credentials, private cloud payloads, `.env` files, private keys and hackathon media. The core is a generic implementation rather than a mechanical merge of reference applications documented in `PREEXISTING_WORK.md`.

Apache-2.0 is the project license. This is an engineering OSS-license decision, not legal advice.

## Grounded unfinished work

- #7 — signed receipts/key-provider protocol;
- #8 — crash-consistent persistence and restart/recovery tests;
- #9 — maintained Google ADK compatibility lifecycle CI;
- cross-runtime conformance/property/formal testing;
- external security review and SBOM/release provenance;
- at least one independently verified external adopter/integration.

## Distribution state

### GitHub

`v0.3.0`: **PUBLISHED / VERIFIED** at `2477164acfbdca6a843bf7b2eac5fa21ce9901b2`.

### PyPI

**NOT PUBLISHED.** No registry availability/install claim is made.
