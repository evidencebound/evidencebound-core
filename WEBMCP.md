# EvidenceBound WebMCP Challenge 2026

## The problem in one minute

A release manager wants an AI agent to help with one exact release. The agent should get the consequential release capability only while the human approval and the evidence behind it are still current.

EvidenceBound makes that human decision change the browser-native WebMCP tool surface:

**`3 tools → human approval → 4 tools → human correction/revocation → 3 tools`**

The agent can inspect release state and request approval, but it cannot approve, revoke, correct, or restore its own authority. When a human approves the current release snapshot, `execute_authorized_release` appears. If that approval is revoked or the governing security evidence is corrected, the tool disappears. Execution also re-checks current authority, so a stale retained descriptor cannot succeed after the decision changes.

**Live demo:** https://evidencebound.org/webmcp/

The demo action is intentionally controlled and records `externalSideEffect=false`; it does not claim to perform a real external deployment.

## 60-second judge path

1. Open the live demo in ChatGPT's in-app browser or Chrome with WebMCP enabled. The agent starts with three safe tools and the release requires human approval.
2. Ask the agent to call `inspect_release_control`.
3. Ask it to call `request_release_authority`. A request becomes pending, but the AI still cannot approve itself.
4. Human clicks **Approve this exact release**. State becomes `AUTHORIZED` and `execute_authorized_release` appears as the fourth tool.
5. Ask the agent to execute. The app revalidates current authority before recording a controlled receipt.
6. Human clicks **Correct security evidence** or **Revoke approval**. Authority is no longer current and the release tool disappears.
7. Adversarial tests separately prove stale retained descriptors, correction during asynchronous verification, and concurrent execution attempts fail closed before an invalid success receipt can commit.

Use the detailed [`docs/competitions/webmcp/JUDGE_PATH.md`](docs/competitions/webmcp/JUDGE_PATH.md) for the exact supported-browser flow.

## Why WebMCP is load-bearing

The project uses the real browser API, `document.modelContext.registerTool(...)`. Three baseline tools are registered for safe inspection/request/receipt access. The consequential `execute_authorized_release` tool is registered only while current human authority is valid.

This is stronger than permanently exposing a release tool and hiding a denial inside it: the set of tools the agent can discover changes when the human decision changes. Execution-time revalidation remains as a second fail-closed boundary for stale discovery state.

The human-only grant/revoke/correct/restore controls are deliberately not WebMCP tools, so the agent cannot mint or repair its own authority.

## Submission-baseline production evidence

The submitted production baseline before this final human-first copy/UX sprint was commit `101832d2a8cff418f64e25980e97482d65340c55`.

At that baseline:

- WebMCP GitHub Actions: **PASS** (`33407673073`)
- full Core GitHub Actions: **PASS** (`33407673069`)
- Vercel production deployment: **READY** (`dpl_4yPLr7n99joJK7PFqU9BGLq396hR`)
- production deployment metadata matched the same GitHub SHA
- real ChatGPT Desktop WebMCP acceptance had previously demonstrated the model-visible surface changing `3 → 4 → 3`; the current execution environment used for repository automation does not itself expose a WebMCP-capable browser runtime

Final-sprint acceptance must be read from current `main`, current GitHub Actions, and current Vercel production rather than assuming this baseline remains current.

Historical evidence for the original challenge implementation is retained in [`docs/competitions/webmcp/PRODUCTION_ACCEPTANCE.md`](docs/competitions/webmcp/PRODUCTION_ACCEPTANCE.md).

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
- [`docs/competitions/webmcp/PRODUCTION_ACCEPTANCE.md`](docs/competitions/webmcp/PRODUCTION_ACCEPTANCE.md) — historical post-merge production evidence
- [`docs/competitions/webmcp/CLAIMS_LEDGER.md`](docs/competitions/webmcp/CLAIMS_LEDGER.md) — allowed/prohibited wording
- [`docs/superpowers/specs/2026-08-31-webmcp-authority-compiler-design.md`](docs/superpowers/specs/2026-08-31-webmcp-authority-compiler-design.md) — architecture tournament / design freeze

## Claim boundary

The deployed page is a real public production surface. The demo action is intentionally controlled and has `externalSideEffect=false`; do not describe it as an actual external deployment or customer mutation. Do not claim first/only/unique invention, guaranteed safety, security certification, customers, traction, or completed submission without separate authoritative evidence.
