# WebMCP Authority Compiler — Design

Date: 2026-08-31
Status: Architecture frozen for autonomous execution
Competition: OpenAI WebMCP Challenge 2026

## One-line thesis

**WebMCP exposes browser capability; EvidenceBound compiles current evidence, policy and human authority into which capability is valid now, then re-checks that authority at execution time.**

The WebMCP-period invention claim is intentionally narrow: not approval, revocation, dynamic tools, provenance or receipts individually, but a deterministic browser authority projection where correction/revocation changes the model-visible WebMCP capability surface and stale tool references still fail closed.

## Judge problem

A release operator wants an AI agent to inspect a change and execute an approved release from the same website. A static tool schema is dangerous: an approval can become stale or invalid after evidence changes, yet the agent may still hold a previously discovered tool reference.

The controlled judge workload is a release-control console. It makes no real production deployment and no external customer/traction claim. The consequential effect is a controlled local “release executed” receipt.

## Non-goals

- No claim to invent HITL, permissions, capability security, dynamic tool lists, provenance, invalidation, proof receipts or correction propagation generally.
- No external deployment/payment/vendor mutation in the public judge path.
- No server, database, authentication system or third-party runtime added unless required by evidence.
- No claim that a client-side demo fingerprint is an independently anchored cryptographic audit log.

## Prior art checked

### Native WebMCP and Chrome

- Current imperative API: `document.modelContext.registerTool(...)`; registration can be lifecycle-bound with an `AbortSignal` for removal.
  - https://developer.chrome.com/docs/ai/webmcp/imperative-api
- Tool lifecycle should follow visible UI/component state.
  - https://github.com/GoogleChromeLabs/use-webmcp-tool
- Current WebMCP annotations include `readOnlyHint` and `untrustedContentHint`; origin exposure can be bounded with `exposedTo`.
  - https://developer.chrome.com/docs/ai/webmcp/
- Declarative WebMCP already supports a manual human-submit path when `toolautosubmit` is omitted.
  - https://developer.chrome.com/docs/ai/webmcp/declarative-api

### Dynamic tools

- WebMCP issue #167 proposes state-dependent schemas and a future `disabled`/`updateTool` mechanism. It explicitly notes that `execute` still needs defensive validation because an enumeration-to-execution stale window remains.
  - https://github.com/webmachinelearning/webmcp/issues/167
- WebMCP issue #30 discusses dynamic tool registration races and describes WebMCP tools as naturally a function of UI state.
  - https://github.com/webmachinelearning/webmcp/issues/30
- MCP itself supports `notifications/tools/list_changed` and recommends human confirmation for sensitive operations.
  - https://modelcontextprotocol.io/specification/2025-11-25/server/tools

### EvidenceBound prior work

See `docs/competitions/2026-preexisting-work-ledger.md`. Authority Cut already has revocable human authority and correction propagation. Recovery Mesh already has invalidation/blast radius. Verified Memory already has fresh-session historical integrity/current applicability. DataHub Gate already has fail-closed MCP gating. These are dependencies/prior art, not new WebMCP claims.

## Falsifiable differentiation thesis

A stronger competitor could disprove the differentiation claim by showing an earlier WebMCP implementation that already binds model-visible tool availability to provenance/evidence validity plus revocable human authority, propagates correction/revocation into future discoverability, and revalidates the same authority snapshot inside `execute()` with an auditable receipt.

Current research found pieces of this pattern — dynamic tool availability, human confirmation, permission middleware, EvidenceBound's own prior authority work — but not that exact composed browser authority-projection behavior. Therefore wording must remain “our WebMCP-period contribution combines…” rather than “first”, “only” or “unique”.

## Architecture tournament

Scale: 1–5 for positive dimensions and execution risk; score =
`Prize Fit × Technical Novelty × Core Improvement × Judge Demonstrability × Defensibility × Commercial Potential × Evidence Strength ÷ Execution Risk`.

| Candidate | Fit | Novelty | Core | Demo | Defensibility | Commercial | Evidence | Risk | Score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A. Static WebMCP policy middleware around always-registered tools | 4 | 2 | 3 | 4 | 3 | 4 | 4 | 2 | 2,304 |
| B. Declarative forms + manual submit approval | 3 | 2 | 2 | 5 | 2 | 3 | 5 | 1.5 | 1,200 |
| C. Authority Compiler: EvidenceBound state → lifecycle-bound WebMCP surface + execute-time recheck | 5 | 4 | 5 | 5 | 4 | 5 | 5 | 2.5 | **20,000** |
| D. Generic server-backed multi-site WebMCP gateway/control plane | 5 | 4 | 5 | 4 | 5 | 5 | 4 | 5 | 8,000 |

### Decision

Choose **Candidate C**. It maximizes WebMCP leverage and judge clarity without adding a new backend or generic gateway. Candidate D is commercially broader but materially increases deadline, deployment and integration risk. Candidate B is robust but too close to native declarative approval. Candidate A looks like generic middleware and does not make browser capability state itself part of the control proof.

## Controlled state contract

The judge page has five explicit operational states:

- `AUTHORIZED`: required evidence is current and a human grant is bound to the exact current evidence fingerprint.
- `HUMAN_REQUIRED`: evidence is usable but no current human grant is bound to it.
- `STALE`: required evidence exceeded its validity horizon.
- `INVALIDATED`: an existing grant/decision no longer matches current evidence or was explicitly revoked.
- `BLOCKED`: required evidence is missing/invalid or a hard policy block exists.

State precedence is fail-closed:

`BLOCKED > STALE > INVALIDATED > HUMAN_REQUIRED > AUTHORIZED`.

A human grant is never exposed as a model-callable tool. The agent may request authority, but the browser user must perform the grant/revoke/correction actions through visible UI controls.

## WebMCP tool contract

Always discoverable:

1. `inspect_release_control`
   - read-only;
   - returns current evidence summary, typed control state, authority fingerprint and safe next step.
2. `request_release_authority`
   - non-read-only only in the sense that it sets a visible pending-request flag;
   - never grants authority;
   - returns `HUMAN_REQUIRED` until a human acts.
3. `list_control_receipts`
   - read-only;
   - returns bounded controlled receipts generated in this tab.

Conditionally discoverable:

4. `execute_authorized_release`
   - registered only while the current control state is `AUTHORIZED`;
   - removed by aborting its registration signal immediately when authority ceases to be valid;
   - its `execute()` closure re-evaluates current state and current evidence fingerprint immediately before effect;
   - if a stale previously retained descriptor is invoked after correction/revocation, it returns a typed fail-closed result and writes no success receipt.

No tool can approve, revoke, correct evidence, mark evidence fresh or bypass the gate.

## Browser implementation

Static files under `site/webmcp/`:

- `index.html` — judge UI and no inline script.
- `styles.css` — challenge-scoped UI.
- `control-core.mjs` — pure deterministic state/evidence/receipt logic.
- `webmcp-adapter.mjs` — WebMCP registration lifecycle and execute-time authority check.
- `app.mjs` — DOM adapter for human controls and visible evidence timeline.
- `*.test.mjs` — dependency-free Node tests.

The site remains serverless and credential-free. Browser state is tab-local only and is explicitly presented as a controlled demo, not durable production authorization.

## Security boundary

1. Use `document.modelContext`; feature-detect and display `WEBMCP_UNAVAILABLE` rather than silently simulating an agent API.
2. Use an `AbortController` for every registration; never depend on a nonexistent `unregisterTool()` API.
3. Use only current WebMCP annotations (`readOnlyHint`, `untrustedContentHint`).
4. The mutation tool is absent unless `AUTHORIZED`, but absence is defense-in-depth, not the sole gate.
5. `execute_authorized_release` re-evaluates current state and exact grant/evidence fingerprint inside the execution callback.
6. Human approval/correction/revocation is UI-only and never included in the WebMCP tool registry.
7. No network fetch, secret, token, cookie or external side effect is required for the canonical judge path.
8. Challenge JS is self-hosted. CSP changes from `script-src 'none'` to `script-src 'self'`; tests reject external script sources.
9. Receipt fingerprints are deterministic controlled-demo identifiers. They are not claimed independently immutable/authenticated.

## State scenarios / judge proof

### Path 1 — human gate to authorized execution

1. Page loads with current evidence and no grant → `HUMAN_REQUIRED`.
2. Agent calls `inspect_release_control` → sees `HUMAN_REQUIRED`.
3. Agent calls `request_release_authority` → visible pending request appears; still `HUMAN_REQUIRED`.
4. Human clicks **Grant exact evidence snapshot** → `AUTHORIZED`.
5. `execute_authorized_release` appears in WebMCP tool surface.
6. Agent calls it → controlled effect succeeds and receipt binds the exact authority/evidence snapshot.

### Path 2 — correction invalidates future agent behavior

1. Human changes the security evidence after a grant.
2. State becomes `INVALIDATED`.
3. `execute_authorized_release` registration is aborted/removed.
4. A retained stale descriptor invoked directly in the adversarial test still returns `INVALIDATED` and creates no success receipt.
5. New grant is impossible until evidence is restored/reverified by the visible human control path.

### Path 3 — stale evidence

1. Human advances the controlled scan past its validity horizon.
2. State becomes `STALE`.
3. Mutation tool is absent and stale descriptor invocation returns `STALE`.

### Path 4 — hard block

1. Human injects controlled missing required evidence.
2. State becomes `BLOCKED`.
3. Mutation tool is absent and the agent receives a typed blocked reason from inspection.

## Evidence and acceptance

Required executed gates before merge:

- Node unit tests for all five states.
- Node lifecycle test proving mutation tool registration only under `AUTHORIZED`.
- Adversarial stale-descriptor test proving execute-time revalidation.
- Test proving no model-callable grant/revoke/correct tool exists.
- Static-site security test proving no external script and correct CSP.
- Existing Python 3.10–3.13 Core CI remains green.
- Vercel preview/production deployment is READY.
- Public readback of `/webmcp/` returns the challenge page and self-hosted modules.
- Browser/Judge WebMCP invocation is `PASS` only after actually observed in a supported browser. If the available browser environment cannot expose WebMCP, this gate remains `UNRUN`/`BLOCKED`, never inferred from JavaScript tests.

## Winner-gap loop after first green build

Ask in order:

1. Can a judge understand “capability follows authority” in under 30 seconds?
2. Does correction visibly remove a previously available mutation tool?
3. Does a stale descriptor still fail closed?
4. Is the WebMCP layer irreplaceable without materially degrading the agent journey?
5. Are all new claims traceable to post-August-25 commits?
6. Is the controlled release effect clearly labeled non-production?
7. Would a server/backend add scoring value greater than its deployment risk? Default answer is no unless evidence changes.
