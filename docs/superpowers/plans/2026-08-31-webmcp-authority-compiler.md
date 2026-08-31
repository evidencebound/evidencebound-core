# WebMCP Authority Compiler Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publicly deploy a credential-free WebMCP judge surface where current evidence and human authority determine the live agent capability set, and stale tool references fail closed after correction/revocation.

**Architecture:** A dependency-free static browser application under `site/webmcp/` uses a pure deterministic control module plus a thin WebMCP adapter. WebMCP registration is lifecycle-bound with `AbortController`; the mutation tool exists only while the state is `AUTHORIZED`, and its execute callback repeats the authority/evidence check before writing a controlled receipt.

**Tech Stack:** Static HTML/CSS, ES modules, WebMCP Imperative API, Node.js 22 built-in test runner, existing pytest/Core CI, existing Vercel static deployment.

**Spec:** `docs/superpowers/specs/2026-08-31-webmcp-authority-compiler-design.md`

## Global Constraints

- Competition baseline parent: `9a2137fe29d0532120a774398a45fa90a9850153`.
- Work branch: `feat/webmcp-authority-compiler-2026`.
- No Sibyl competition implementation before 2026-09-01 00:00 UTC.
- No new npm package or runtime dependency.
- No network calls, credentials or external consequential side effects in the canonical WebMCP judge path.
- Human grant/revoke/correction controls MUST NOT be exposed as WebMCP tools.
- WebMCP mutation capability is defense-in-depth: execution MUST re-evaluate current authority even after discovery.
- Use `document.modelContext` and lifecycle removal via registration `AbortSignal`.
- `PASS` requires executed evidence; unsupported browser WebMCP testing remains `UNRUN` or `BLOCKED`.

---

### Task 1: RED — Authority State Contract

**Files:**
- Create: `site/webmcp/control-core.test.mjs`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: planned exports from `./control-core.mjs`.
- Produces: executable RED tests and a dedicated Node CI job.

- [ ] **Step 1: Add the failing tests**

Create tests equivalent to:

```js
import test from 'node:test';
import assert from 'node:assert/strict';
import {
  createInitialState,
  evaluateControl,
  grantCurrentAuthority,
  expireSecurityEvidence,
  correctSecurityEvidence,
  removeRequiredEvidence,
} from './control-core.mjs';

test('initial current evidence requires a human grant', async () => {
  const state = createInitialState();
  const decision = await evaluateControl(state);
  assert.equal(decision.status, 'HUMAN_REQUIRED');
});

test('grant bound to current evidence authorizes execution', async () => {
  let state = createInitialState();
  state = await grantCurrentAuthority(state);
  assert.equal((await evaluateControl(state)).status, 'AUTHORIZED');
});

test('expired evidence is stale even with a previous grant', async () => {
  let state = await grantCurrentAuthority(createInitialState());
  state = expireSecurityEvidence(state);
  assert.equal((await evaluateControl(state)).status, 'STALE');
});

test('corrected evidence invalidates an existing grant', async () => {
  let state = await grantCurrentAuthority(createInitialState());
  state = correctSecurityEvidence(state);
  assert.equal((await evaluateControl(state)).status, 'INVALIDATED');
});

test('missing required evidence blocks', async () => {
  const state = removeRequiredEvidence(createInitialState());
  assert.equal((await evaluateControl(state)).status, 'BLOCKED');
});
```

- [ ] **Step 2: Add Node test execution to CI**

Add a `webmcp` job using pinned `actions/checkout` and pinned `actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020`, Node `22`, then run:

```bash
node --test site/webmcp/*.test.mjs
```

- [ ] **Step 3: Push the RED commit and verify the WebMCP job fails for the expected reason**

Expected failure: module `site/webmcp/control-core.mjs` does not exist. This is the required TDD RED proof, not a typo or infrastructure failure.

---

### Task 2: GREEN — Deterministic Authority Core

**Files:**
- Create: `site/webmcp/control-core.mjs`

**Interfaces:**
- Produces:
  - `createInitialState(): ControlState`
  - `evaluateControl(state): Promise<ControlDecision>`
  - `grantCurrentAuthority(state): Promise<ControlState>`
  - `revokeAuthority(state): ControlState`
  - `expireSecurityEvidence(state): ControlState`
  - `correctSecurityEvidence(state): ControlState`
  - `removeRequiredEvidence(state): ControlState`
  - `restoreFreshEvidence(state): ControlState`
  - `recordPendingAuthorityRequest(state): ControlState`
  - `createExecutionReceipt(state, decision): Promise<Receipt>`

- [ ] **Step 1: Implement only the state logic required by Task 1**

Use canonical JSON input and Web Crypto SHA-256 to fingerprint the exact evidence snapshot. `evaluateControl()` applies the precedence:

```text
BLOCKED > STALE > INVALIDATED > HUMAN_REQUIRED > AUTHORIZED
```

A grant stores the current evidence fingerprint. A corrected evidence revision changes that fingerprint, so the old grant evaluates to `INVALIDATED`.

- [ ] **Step 2: Verify Task 1 becomes GREEN**

Run in CI:

```bash
node --test site/webmcp/control-core.test.mjs
```

Expected: all state tests PASS.

- [ ] **Step 3: Extend tests before extending behavior**

Add failing tests for explicit revocation, restored fresh evidence returning to `HUMAN_REQUIRED`, pending requests never granting authority, and receipt creation only from `AUTHORIZED`.

- [ ] **Step 4: Implement the minimal additional behavior and verify all control-core tests pass**

Receipt output must include only controlled identifiers/status/fingerprint and must not claim immutable/authenticated storage.

---

### Task 3: RED→GREEN — WebMCP Capability Lifecycle

**Files:**
- Create: `site/webmcp/webmcp-adapter.test.mjs`
- Create: `site/webmcp/webmcp-adapter.mjs`

**Interfaces:**
- Consumes: `evaluateControl`, `recordPendingAuthorityRequest`, `createExecutionReceipt` from `control-core.mjs`.
- Produces:
  - `createWebMCPController({ modelContext, getState, setState, onReceipt }): WebMCPController`
  - `controller.sync(): Promise<ControlDecision>`
  - `controller.dispose(): void`
  - `controller.getRegisteredToolNames(): string[]` for deterministic local evidence only.

- [ ] **Step 1: Write a fake ModelContext in the test**

The fake records tool descriptors and removes them when each provided registration signal aborts. It must not mock the production controller internals.

- [ ] **Step 2: Write failing lifecycle tests**

Tests must prove:

```text
HUMAN_REQUIRED -> inspect/request/list tools only
AUTHORIZED     -> execute_authorized_release additionally present
STALE          -> execute tool removed
INVALIDATED    -> execute tool removed
BLOCKED        -> execute tool removed
```

Also assert that no registered tool name contains grant/approve/revoke/correct/restore semantics.

- [ ] **Step 3: Write the adversarial stale-descriptor RED test**

Capture the actual `execute_authorized_release` descriptor while authorized, mutate state to corrected/invalidated, call the retained descriptor's `execute()` directly, and assert:

```js
assert.equal(result.status, 'INVALIDATED');
assert.equal(receipts.length, 0);
```

This proves execute-time validation independently of WebMCP tool removal.

- [ ] **Step 4: Implement `webmcp-adapter.mjs` minimally**

Register tools with `modelContext.registerTool(tool, { signal })`. On each `sync()`, abort the previous conditional mutation registration and re-register it only if `evaluateControl()` returns `AUTHORIZED`. Always re-evaluate inside the mutation tool's `execute()` before effect/receipt.

Use current annotations only:

```js
annotations: { readOnlyHint: true|false, untrustedContentHint: false }
```

- [ ] **Step 5: Verify adapter tests and full WebMCP Node suite GREEN**

```bash
node --test site/webmcp/*.test.mjs
```

---

### Task 4: RED→GREEN — Judge UI and Static Security Contract

**Files:**
- Create: `site/webmcp/index.html`
- Create: `site/webmcp/styles.css`
- Create: `site/webmcp/app.mjs`
- Create: `tests/test_webmcp_site.py`
- Modify: `site/vercel.json`

**Interfaces:**
- UI consumes `control-core.mjs` and `webmcp-adapter.mjs`.
- Human-only buttons call the state mutators directly; they never register as WebMCP tools.

- [ ] **Step 1: Write failing pytest static-contract tests**

Assert:

- `/site/webmcp/index.html`, `control-core.mjs`, `webmcp-adapter.mjs`, `app.mjs` exist;
- index uses only self-hosted module script `/webmcp/app.mjs`;
- no external `<script src="http...">` exists;
- UI includes visible labels for all five states and a “controlled demo / no external deployment” boundary;
- no WebMCP tool string exposes human grant/revoke/correct/restore actions;
- Vercel CSP permits `script-src 'self'` and retains `connect-src 'self'`, `frame-ancestors 'none'`, `base-uri 'self'`.

- [ ] **Step 2: Push RED and confirm expected missing-file/CSP failures**

- [ ] **Step 3: Implement the UI**

The first viewport must show:

- thesis: `Capability follows current authority.`
- WebMCP runtime badge: `AVAILABLE` or `WEBMCP_UNAVAILABLE` from real feature detection;
- current control state;
- current model-visible tool names;
- evidence cards and authority fingerprint;
- exact five-step judge path;
- event/receipt ledger.

Human controls:

- Grant exact evidence snapshot
- Revoke grant
- Expire security evidence
- Correct security evidence
- Remove required evidence
- Restore fresh evidence
- Reset controlled demo

After every human state transition call `controller.sync()` and rerender.

- [ ] **Step 4: Modify CSP narrowly enough for the static module app**

Change global `script-src 'none'` to `script-src 'self'`. Do not add CDN/script origins or unsafe-inline. Existing static pages contain no script, so their runtime behavior remains unchanged while the self-hosted challenge module can execute.

- [ ] **Step 5: Verify pytest static contract, Node suite and existing Python suite in CI**

---

### Task 5: README/Evidence Pack, PR, Merge and Production Acceptance

**Files:**
- Modify: `README.md`
- Create: `docs/competitions/webmcp/README.md`
- Create: `docs/competitions/webmcp/CLAIMS_LEDGER.md`
- Create: `docs/competitions/webmcp/JUDGE_PATH.md`
- Create: `docs/competitions/webmcp/VIDEO_SCRIPT.md`
- Create: `docs/competitions/webmcp/PRODUCTION_ACCEPTANCE.md` only with observed evidence.

**Interfaces:**
- Judge docs point to `/webmcp/`, critical source files and exact commits.

- [ ] **Step 1: Add judge-facing documentation without unsupported claims**

README must distinguish pre-existing EvidenceBound Core from WebMCP-period work and link to the ledger/rules/design.

- [ ] **Step 2: Run/observe quality gates**

Required statuses before merge:

```text
WebMCP Node unit/adversarial tests: PASS
Existing Core pytest 3.10–3.13: PASS
ruff/mypy/build: PASS through existing CI
security/supply-chain jobs: PASS
Vercel preview: READY/success
Browser WebMCP invocation: PASS only if actually observed; otherwise UNRUN/BLOCKED
```

- [ ] **Step 3: Create PR and review diff against `main`**

Verify every WebMCP-attributed file is post-baseline and no Sibyl implementation exists.

- [ ] **Step 4: Merge only after required repository gates pass**

- [ ] **Step 5: Verify `main` CI and Vercel deployment**

Production acceptance must bind the exact merge commit to the Vercel deployment and publicly read back `/webmcp/` plus module assets.

- [ ] **Step 6: Rehearse the judge path**

If a supported WebMCP browser is available, prove real discovery/invocation and correction-driven capability removal. If not, record the exact browser-environment blocker and leave this gate non-PASS for the final Cloud Browser/Chrome handoff.

- [ ] **Step 7: Run the WINNER GAP audit**

Do not declare technical READY while a feasible scoring-critical gap remains.
