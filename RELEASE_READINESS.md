# v0.4.0 Release Candidate Evidence

## Status

**RELEASE PREPARATION ONLY — NOT TAGGED, NOT RELEASED, NOT PUBLISHED TO PYPI.**

Prepared from exact `main` SHA `1d128d2bfae6627802be403e84bb114ffcb36580`.

The exact release-candidate commit is the draft pull-request head containing this file. A Git
commit cannot embed its own SHA without changing that SHA, so exact-head identity is recorded
by GitHub PR metadata and exact-head CI/readback rather than by a self-referential literal
inside the commit.

## Minimal v0.4.0 release delta

- package metadata version: `0.4.0`;
- public runtime version: `0.4.0`;
- current signed-receipt, persistence/restart, compatibility, conformance and supply-chain
  hardening frozen from `Unreleased` into `0.4.0`, with no new trust semantics;
- `CITATION.cff` updated to version `0.4.0`, intended release date `2026-10-05`, and
  canonical repository `https://github.com/evidencebound/evidencebound-core`;
- manual-only guarded GitHub/PyPI release workflow using PyPI Trusted Publishing.

The intended date above is release-preparation metadata. It does not establish that publication
has occurred.

No AgenTrust-specific semantics or adapter behavior are added to EvidenceBound Core.

## Required exact-head acceptance before publication

The draft PR head must have a successful `CI` pull-request run covering:

- Python 3.10 / 3.11 / 3.12 / 3.13 test matrix;
- golden acceptance and deterministic benchmark acceptance;
- Ruff and strict mypy;
- sdist/wheel build, wheel reinstall/import and PEP 561 marker verification;
- clean-room runtime-only installation and zero-unconditional-runtime-dependency assertion;
- pip-audit and Bandit security gates;
- exact `google-adk==2.7.0` compatibility lane;
- supply-chain build, SHA-256 manifest, CycloneDX SBOM and validation.

The `attest-supply-chain` job is intentionally not a pull-request job. It is restricted to
trusted `main` pushes. The release workflow additionally refuses publication unless the
approved exact `main` SHA has a successful completed `CI` push run; that post-merge CI run
includes the trusted-main provenance/SBOM attestation job.

## Publication guard

`.github/workflows/release-v0.4.0.yml` is `workflow_dispatch` only and requires:

1. invocation from `refs/heads/main`;
2. confirmation string `publish-v0.4.0`;
3. an explicit approved `accepted_sha` equal to both the workflow SHA and live `main` SHA;
4. a successful completed `CI` push run for that exact SHA;
5. a locally rebuilt `0.4.0` sdist/wheel whose installed metadata and runtime version agree;
6. PyPI Trusted Publishing through the protected `pypi` environment;
7. live PyPI `0.4.0` readback before creating the non-draft GitHub Release;
8. exact tag and release readback after publication.

The workflow may create/reuse only tag `v0.4.0` at the accepted SHA. It refuses a mismatched
existing tag.

## External prerequisite

Before the publication workflow can succeed, PyPI must have a Trusted Publisher (or pending
Trusted Publisher for the first project release) matching:

- PyPI project: `evidencebound-core`;
- GitHub owner: `evidencebound`;
- repository: `evidencebound-core`;
- workflow: `release-v0.4.0.yml`;
- environment: `pypi`.

Absence or mismatch of that external configuration is a release blocker, not a condition the
repository workflow may bypass.

## Prior published release

- GitHub release: `v0.3.0`;
- tag target: `2477164acfbdca6a843bf7b2eac5fa21ce9901b2`;
- published: `2026-08-17`;
- PyPI: not published.
