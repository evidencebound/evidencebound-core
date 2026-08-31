# EvidenceBound WebMCP Challenge 2026

## Judge entry point

**Live demo:** https://evidencebound.org/webmcp/

**Thesis:** WebMCP exposes browser capability; EvidenceBound determines whether that capability is authorized now from current evidence, policy, and explicit human authority.

> **Capability follows current authority.**

The consequential tool `execute_authorized_release` is absent until an exact human grant matches current evidence. Correction, revocation, stale evidence, or a hard evidence/policy failure removes or blocks that capability. Execution also re-checks authoritative state before a controlled success receipt can commit.

## 60-second proof

1. Start at `HUMAN_REQUIRED`; execution tool absent.
2. Agent calls `inspect_release_control`.
3. Agent calls `request_release_authority`; request becomes pending, but no grant is created.
4. Human clicks **Grant exact evidence snapshot**; state becomes `AUTHORIZED`; `execute_authorized_release` appears.
5. Agent executes; controlled receipt is created with `externalSideEffect=false`.
6. Human clicks **Correct security evidence**; state becomes `INVALIDATED`; execution capability disappears.
7. Automated adversarial tests separately prove retained stale descriptors, correction during async verification, and concurrent execution attempts fail closed before an invalid success receipt can commit.

Use the full [`docs/competitions/webmcp/JUDGE_PATH.md`](docs/competitions/webmcp/JUDGE_PATH.md) in a supported WebMCP browser.

## Production evidence

Production merge: `1655514e60e8266331cb431c7726f37725608c99`

Final competition implementation head: `14f7a81200daafa717af474c0747ac4e215b195d`

Observed post-merge status:

- WebMCP GitHub Actions: **PASS** (`33393610245`)
- full Core GitHub Actions: **PASS** (`33393610270`)
- Vercel production deployment: **READY** (`dpl_GFsK47tx8z4P5F1G42rrgSJuin5N`)
- public `/webmcp/`, `app.mjs`, `webmcp-adapter.mjs`, `control-core.mjs`: **HTTP 200**
- restrictive CSP/HSTS/nosniff/frame-deny/Permissions-Policy: **observed**
- real browser-native WebMCP discovery/invocation in this Project environment: **UNRUN** because this environment does not expose a supported WebMCP browser runtime

Exact evidence: [`docs/competitions/webmcp/PRODUCTION_ACCEPTANCE.md`](docs/competitions/webmcp/PRODUCTION_ACCEPTANCE.md).

## What is new vs. pre-existing

This repository existed before the challenge. The competition contribution is the browser-native WebMCP authority projection and its judge surface/adversarial contract. It does not claim pre-existing EvidenceBound primitives such as provenance, human approval, revocation, recovery, persistence, signed receipts, dependency invalidation, or verified-memory ideas as new challenge-period inventions.

Read:

- [`docs/competitions/2026-preexisting-work-ledger.md`](docs/competitions/2026-preexisting-work-ledger.md)
- [`PREEXISTING_WORK.md`](PREEXISTING_WORK.md)
- [`docs/competitions/webmcp/CLAIMS_LEDGER.md`](docs/competitions/webmcp/CLAIMS_LEDGER.md)

## Judge / submission pack

- [`docs/competitions/webmcp/README.md`](docs/competitions/webmcp/README.md) — architecture + competition evidence index
- [`docs/competitions/webmcp/JUDGE_PATH.md`](docs/competitions/webmcp/JUDGE_PATH.md) — exact browser flow
- [`docs/competitions/webmcp/VIDEO_SCRIPT.md`](docs/competitions/webmcp/VIDEO_SCRIPT.md) — <3 minute claim-safe video script
- [`docs/competitions/webmcp/PRODUCTION_ACCEPTANCE.md`](docs/competitions/webmcp/PRODUCTION_ACCEPTANCE.md) — post-merge production evidence
- [`docs/competitions/webmcp/CLAIMS_LEDGER.md`](docs/competitions/webmcp/CLAIMS_LEDGER.md) — allowed/prohibited wording
- [`docs/superpowers/specs/2026-08-31-webmcp-authority-compiler-design.md`](docs/superpowers/specs/2026-08-31-webmcp-authority-compiler-design.md) — architecture tournament / design freeze

## Claim boundary

The deployed page is a real public production surface. The demo action is intentionally controlled and has `externalSideEffect=false`; do not describe it as an actual external deployment or customer mutation. Do not claim first/only/unique invention, guaranteed safety, security certification, customers, traction, or completed submission without separate authoritative evidence.
