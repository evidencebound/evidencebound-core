# v0.3.0 Release Readiness

## Status

EvidenceBound Core is technically at a **v0.3.0 release-candidate** boundary. The package version is `0.3.0`, but `CHANGELOG.md` intentionally remains `Unreleased` until a GitHub `v0.3.0` tag/release is actually created and verified.

This file separates **technical acceptance** from **distribution/publication**. A green source tree is not the same thing as a published release.

## Last accepted main baseline before release-metadata hardening

- Repository: `moneyparking/EvidenceBound-OSS-Core-Funding-Adoption`
- Visibility: public
- Branch: `main`
- SHA: `6317d0701a7873c4711357bd140062aac00965d1`
- GitHub Actions run: `31968785923` — SUCCESS
- Python matrix: 3.10 / 3.11 / 3.12 / 3.13 — SUCCESS
- Python 3.13 pytest result: **32 passed**
- Golden acceptance: SUCCESS
- Ruff: SUCCESS
- strict mypy: SUCCESS
- package sdist/wheel build: SUCCESS
- wheel reinstall/import: SUCCESS
- clean-room fresh-venv install + plain example + golden acceptance: SUCCESS
- pip-audit: SUCCESS
- Bandit core-source scan: SUCCESS

The active release-readiness branch must itself pass the same gates before merge because it changes package metadata and adds the benchmark as an executable CI gate.

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

Expected scenario-specific result:

- full restart nodes: 100;
- selective recompute: 25;
- reusable: 75;
- requires verification: 0;
- recomputations avoided: 75.

The script asserts these counts. Elapsed time is reported only as local scenario telemetry and is not a universal performance claim.

## Package/release engineering

- Python runtime requirement: `>=3.10`.
- Unconditional runtime dependencies: none.
- Build backend: setuptools.
- License metadata: SPDX `Apache-2.0` with `LICENSE` declared as the license file.
- License rationale: `LICENSE_DECISION.md`.
- Pre-existing/reference implementation boundary: `PREEXISTING_WORK.md`.
- GitHub Actions dependencies are pinned by commit SHA.
- Dependency/security scans are explicit CI jobs.

## Publication audit

The repository intentionally excludes SignalReview commercial logic, provider credentials, private cloud payloads, `.env` files, private keys and hackathon media. The core is a generic implementation rather than a mechanical merge of the reference applications documented in `PREEXISTING_WORK.md`.

Apache-2.0 is the project license. This is an engineering OSS-license decision, not legal advice.

## Distribution state

### GitHub tag/release

Not yet created. Do not describe `v0.3.0` as released until a tag is verified to point to the final accepted `main` SHA and the GitHub Release is visible.

### PyPI

Not published. PyPI namespace/account ownership and exact package-name availability have not been established strongly enough for autonomous publication. PyPI is optional for v0.3 technical acceptance and must be treated as a separate distribution action.

## Release stop rule

Create or announce `v0.3.0` only after:

1. the release-readiness changes are merged;
2. exact resulting `main` CI is SUCCESS;
3. the tag is created at that exact accepted SHA;
4. the tag/release relationship is independently fetched and verified.

If tag/release mutation is unavailable to the execution environment, that is a publication-tooling blocker, not a reason to weaken or fabricate release evidence.
