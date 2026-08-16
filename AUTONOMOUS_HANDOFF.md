# Autonomous Handoff

## Canonical repository

- Repository: `moneyparking/EvidenceBound-OSS-Core-Funding-Adoption`
- Visibility: public
- Canonical branch: `main`
- Last verified `main` before this hardening wave: `6ca6ff78abf0012f4d7c216497394e9edb848bd1`
- Exact-main CI: run `31968100914` — SUCCESS
- Active hardening branch: `agent/public-clean-room-acceptance`

The exact commit containing this file must be re-checked against GitHub CI before making a release claim; do not substitute an older SHA from this document for `git rev-parse HEAD` / the GitHub branch ref.

## Milestone state at handoff creation

- v0.1 independent core: executable acceptance satisfied.
- v0.2 graph/selective recovery: executable acceptance satisfied.
- v0.3 branch/main feature set: implemented; exact-main CI was green before the explicit clean-room gate wave.
- Release/tag: not yet created.
- PyPI: not published; ownership/name availability remains unverified.

## Proven gates

- 27-test suite.
- Protected payload tamper -> integrity failure -> BLOCK.
- Historical integrity VERIFIED can coexist with current applicability REVIEW_REQUIRED.
- Hash change yields CHANGED, never implicit REFUTED.
- Missing/refuted evidence and required provenance loss fail closed.
- Duplicate evidence IDs reject/fail closed.
- DAG cycle/missing dependency/duplicate checkpoint rejection.
- Exact descendant-only blast radius across branch/diamond cases.
- Selective recovery reusable/recompute separation.
- Consequential action remains blocked until all affected recompute prerequisites are successfully re-verified.
- Replay duplicate detection/conflict semantics.
- Plain Python and dependency-free Google ADK integration seams.
- Python 3.10-3.13 CI, Ruff, strict mypy, package build, wheel reinstall/import.
- pip-audit and Bandit security jobs.

## Current wave acceptance

The branch adds a dedicated GitHub `clean-room` job:

1. fresh checkout;
2. fresh Python 3.13 venv;
3. `pip install .` without dev extras;
4. plain Python example;
5. golden external acceptance;
6. assertion that the package declares no runtime dependencies.

Do not mark the clean-room gate PASS until the exact branch/main job is green.

## Next exact actions

1. Verify CI on the exact head of `agent/public-clean-room-acceptance`.
2. Repair any failures and rerun.
3. Merge only after all test/security/clean-room jobs are green.
4. Verify the resulting exact `main` push CI.
5. If green, update release metadata consistently and create a GitHub v0.3.0 release/tag only if the release commit itself remains accepted.
6. Do not publish to PyPI until package ownership/name/account state is verified.

## Remaining high-value gaps after v0.3

- signed receipts/key-provider interface;
- persistence backend protocol and crash consistency tests;
- cross-runtime canonicalization/conformance fixtures;
- property/fuzz and formal state-machine testing;
- maintained upstream-framework compatibility tests;
- external security review and release provenance/SBOM;
- at least one integration by a project not owned by the maintainer.
