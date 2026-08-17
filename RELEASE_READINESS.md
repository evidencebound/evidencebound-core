# v0.3.0 Release Readiness

## Status

EvidenceBound Core is technically at a **v0.3.0 release-candidate** boundary. The source package version is `0.3.0`, but `CHANGELOG.md` remains `Unreleased` until a GitHub `v0.3.0` tag/release is actually created and independently verified.

Technical acceptance and distribution/publication are separate states. A green source tree is not itself a published release.

## Latest accepted main before this evidence-sync commit

- Repository: `moneyparking/EvidenceBound-OSS-Core-Funding-Adoption`
- Visibility: public
- Branch: `main`
- SHA: `ffb4aa2ed317640b76f2590c859dfc60d533be28`
- GitHub Actions run: `31990753200` — SUCCESS
- Python matrix: 3.10 / 3.11 / 3.12 / 3.13 — SUCCESS
- Python 3.13 pytest: **32 passed**
- Golden acceptance: SUCCESS
- Selective-recovery benchmark acceptance: SUCCESS
- Ruff: SUCCESS
- strict mypy: SUCCESS across 12 source files
- package sdist/wheel build: SUCCESS
- wheel reinstall/import: SUCCESS
- built-wheel PEP 561 `py.typed` marker: VERIFIED
- clean-room fresh-venv runtime-only install + typing marker + plain example + golden acceptance: SUCCESS
- no unconditional runtime dependency assertion: SUCCESS
- pip-audit: SUCCESS
- Bandit core-source scan: SUCCESS

This SHA is acceptance evidence only. A later docs-only merge creates a new `main` SHA, which must itself pass CI before it can become a release target.

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

Expected and asserted scenario-specific result:

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
- Repository/issues/changelog/documentation URLs are present in package metadata.
- License rationale: `LICENSE_DECISION.md`.
- Pre-existing/reference implementation boundary: `PREEXISTING_WORK.md`.
- GitHub Actions dependencies are pinned by commit SHA.
- Dependency and static-security scans are explicit CI jobs.
- Maintainer-led governance is documented in `GOVERNANCE.md`; no external governance body is claimed.
- `CITATION.cff` provides software citation metadata.

## Adapter boundary

The Google ADK seam remains dependency-free. `docs/INTEGRATION.md` explicitly requires consequential integrations to wait for callback completion and a present EvidenceBound `ALLOW` result; a missing callback result or prematurely stopped lifecycle is unverified/blocked. Real upstream ADK compatibility CI is unfinished work tracked in issue #9.

## Publication audit

The repository intentionally excludes SignalReview commercial logic, provider credentials, private cloud payloads, `.env` files, private keys and hackathon media. The core is a generic implementation rather than a mechanical merge of reference applications documented in `PREEXISTING_WORK.md`.

Apache-2.0 is the project license. This is an engineering OSS-license decision, not legal advice.

## Grounded unfinished work

Public issues make important post-v0.3 gaps explicit rather than implying completion:

- #7 — signed receipts/key-provider protocol;
- #8 — crash-consistent persistence and restart/recovery tests;
- #9 — maintained Google ADK compatibility lifecycle CI.

Independent external adoption, external security review, cross-runtime conformance, formal/property testing and release provenance/SBOM remain unverified gaps.

## Distribution state

### GitHub tag/release

Not created or verified as of this evidence sync. Do not describe `v0.3.0` as released until a tag is fetched and verified to point to the final accepted `main` SHA and the GitHub Release is visible.

### PyPI

Not published. PyPI namespace/account ownership and exact package-name availability have not been established strongly enough for autonomous publication. PyPI is optional for technical v0.3 acceptance and is a separate distribution action.

## Release stop rule

Create or announce `v0.3.0` only after:

1. this final evidence sync is merged;
2. exact resulting `main` CI is SUCCESS;
3. the current `main` SHA is fetched after that success;
4. a `v0.3.0` tag is created at exactly that accepted SHA;
5. the tag and GitHub Release are independently fetched and verified.

If tag/release mutation is unavailable to the execution environment, that is a publication-tooling blocker, not a reason to weaken or fabricate release evidence.
