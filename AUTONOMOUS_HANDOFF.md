# Autonomous Handoff

## Canonical repository

- Repository: `moneyparking/evidencebound-core`
- URL: https://github.com/moneyparking/evidencebound-core
- Visibility: public
- Canonical branch: `main`
- Latest accepted pre-truth-sync main: `f6f46d4f21d6fcb2dc53cfeb0ebe70a742a34d9c`
- Exact-main CI: run `31995557238` — SUCCESS
- Published release: `v0.3.0`
- Release source SHA: `2477164acfbdca6a843bf7b2eac5fa21ce9901b2`
- Release-source exact-main CI: run `31991997448` — SUCCESS
- Release URL: https://github.com/moneyparking/evidencebound-core/releases/tag/v0.3.0

The release tag is fixed historical evidence. Never move `v0.3.0` to a later `main` commit. Post-release capabilities below are Unreleased `main` work unless a later release is independently verified.

## Milestone state

- v0.1 independent core: PASS.
- v0.2 trust graph/selective recovery: PASS.
- v0.3 technical/adoption/security baseline: PASS.
- GitHub `v0.3.0` source release: PUBLISHED / VERIFIED.
- PyPI: NOT PUBLISHED.
- Independent external adopter: NOT YET VERIFIED.

## Post-release hardening accepted on exact main

- #7 signed receipt provider protocol / key lifecycle / optional Ed25519 — CLOSED completed; exact-main run `31993226080` SUCCESS.
- #8 crash-consistent SQLite persistence/restart/replay — CLOSED completed; exact-main run `31994016152` SUCCESS.
- #9 real Google ADK 2.7.0 lifecycle compatibility — CLOSED completed; exact-main run `31994792165` SUCCESS.
- #17 EBCJ-1 conformance corpus + deterministic property invariants — CLOSED completed; exact-main run `31995166680` SUCCESS.
- #19 SHA-256 manifest + CycloneDX SBOM + trusted-main SLSA/SBOM attestations — CLOSED completed; exact-main run `31995557238` SUCCESS.

At `f6f46d4f21d6fcb2dc53cfeb0ebe70a742a34d9c`, standard Python matrix, golden acceptance, benchmark, Ruff, strict mypy, clean-room runtime dependency gate, security, real ADK compatibility, supply-chain validation and trusted-main attestation jobs all completed successfully.

## Trust boundaries that remain explicit

- signatures authenticate signed bytes under configured trust roots; they do not prove evidence truth;
- persisted database state is reverified and is not trusted solely because it was stored;
- SQLite is not immutable/authenticated/distributed storage;
- ADK compatibility is proven only for exact tested `google-adk==2.7.0` until another version passes the compatibility lane;
- EBCJ-1 is EvidenceBound-specific and not claimed RFC 8785/JCS;
- property tests are engineering evidence, not formal verification;
- trusted-main build attestations apply to exact generated subject digests, not retroactively to `v0.3.0`;
- no independent external adopter or external security audit is claimed.

## Highest-value remaining work

1. Build a clean-room external-consumer/conformance fixture that installs EvidenceBound as a third-party dependency through public APIs only; label it maintainer-authored, not external adoption.
2. Seek/enable a genuinely independently owned integration and record only externally attributable evidence actually obtained.
3. Create a future release workflow linking tag → exact wheel/sdist digests → SBOM → provenance attestations; do not alter `v0.3.0`.
4. Formalize invalidation/recovery as a state machine/model where useful.
5. Prepare an external security review scope and funding work package.
6. Recheck current official OSS funding calls when preparing an application.
