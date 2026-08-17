# Autonomous Worklog

## 2026-08-16 — 2026-08-17

### Foundation and release
- Built the independent Python core, typed evidence/provenance/policy/checkpoint/verification/receipt contracts, EBCJ-1 canonicalization, fail-closed trust semantics, exact dependency graph/recovery, replay/idempotency, provider-neutral events and thin integration seams.
- Added public architecture/spec/threat/security/contribution/governance/funding/release documentation, Apache-2.0 licensing, Python 3.10–3.13 CI, clean-room installation, Ruff, strict mypy, package build, pip-audit and Bandit.
- Renamed the repository to canonical `moneyparking/evidencebound-core` and synchronized package/docs/citation/security/funding URLs.
- Published and independently verified GitHub source release `v0.3.0` at exact commit `2477164acfbdca6a843bf7b2eac5fa21ce9901b2`; release-source CI `31991997448` SUCCESS. PyPI was not published.

### Post-release hardening

#### #7 — signed receipts
- Added provider-neutral signer/verifier protocols, detached signed envelopes, ACTIVE/RETIRED/REVOKED/UNKNOWN key states and optional Ed25519 implementation without unconditional crypto dependency.
- Added wrong-key/tamper/malformed/provider-error/legacy-unsigned tests and signing security/migration docs.
- PR #14 accepted; merged main `eb2268e34260720690eb2ee7c0e70955c1e60ddb`; exact-main CI `31993226080` SUCCESS; issue #7 closed completed.

#### #8 — persistence/restart
- Added provider-neutral persistence contract, stdlib SQLite reference store, atomic checkpoint/receipt/verification/replay bundle, reverify-on-load semantics and durable replay guard.
- Added crash injection, tamper, missing state, schema/version and restart graph/blast-radius tests.
- PR #15 accepted; merged main `92a913c3896642c2ad67ee076d85dad5bec5bdef`; exact-main CI `31994016152` SUCCESS; issue #8 closed completed.

#### #9 — Google ADK compatibility
- Verified current upstream `google-adk==2.7.0`; diagnosed real runtime contracts rather than relying on stale assumptions: callback is invoked via `callback_context=...`, and fresh Runner invocation requires `new_message` or resume `invocation_id`.
- Added real credential-free BaseAgent/Runner/InMemorySessionService compatibility lane and fail-closed consequential gate. Complete lifecycle persists ALLOW/state delta; early stream close leaves verification absent/BLOCK.
- PR #16 accepted; merged main `48c5bf8d8847bc25a9d6e0580f634d2a8b57c562`; exact-main CI `31994792165` SUCCESS; issue #9 closed completed.

#### #17 — conformance/property invariants
- Added versioned EBCJ-1 language-neutral vectors, Python invalid-input expectations and explicit no-Unicode-normalization semantics.
- Added dev-only deterministic Hypothesis properties for canonical ordering/round-trip, digest domain separation, CHANGED-not-REFUTED, receipt mutation and exact generated-DAG blast radius.
- PR #18 accepted; merged main `73dcf936806c2d1f73842df01fbadb5f6b2661a3`; exact-main CI `31995166680` SUCCESS; issue #17 closed completed.

#### #19 — supply-chain evidence
- Added read-only PR build/checksum/CycloneDX validation and isolated trusted-main attestation job; PR code never receives OIDC/attestation write permissions.
- Official `actions/attest` v4.2.2 pinned at `1e69f48acb82d1966a394da916b4c1698aa569d6`.
- Trusted-main job rebuilds artifacts, validates SHA-256 subjects/SBOM, creates SLSA build-provenance and SBOM attestations, and emits exact hashes plus attestation IDs/URLs.
- PR #20 accepted; merged main `f6f46d4f21d6fcb2dc53cfeb0ebe70a742a34d9c`; exact-main CI `31995557238` SUCCESS including `attest-supply-chain`; issue #19 closed completed.
- `v0.3.0` predates this workflow and is not claimed to be retroactively attested.

### Current verified state before truth-sync
- `main`: `f6f46d4f21d6fcb2dc53cfeb0ebe70a742a34d9c`.
- exact-main CI: `31995557238` — SUCCESS.
- published release remains `v0.3.0` → `2477164acfbdca6a843bf7b2eac5fa21ce9901b2`.
- PyPI: NOT PUBLISHED.
- Independent external adopter: NOT VERIFIED.
- External security audit: NOT PERFORMED.

### Highest-value next work
- clean-room external-consumer package/integration fixture through public APIs only;
- genuinely independent external integration evidence;
- future release artifact/tag/SBOM/attestation linkage;
- formal state-machine/model and external security review preparation.
