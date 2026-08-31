# WebMCP Judge Path

Target: make the invention legible and behaviorally proved in roughly 60–90 seconds.

Canonical production path after acceptance: `https://evidencebound.org/webmcp/`

## Before judging

Use a supported environment from the official challenge rules: ChatGPT in-app browser or a Chrome build with WebMCP enabled. Start from a fresh page load and reset the controlled demo.

Required visible initial conditions:

- Runtime badge: `AVAILABLE`.
- State: `HUMAN_REQUIRED`.
- Evidence: manifest present; security evidence `PASS · CURRENT`.
- Grant: `none`.
- `execute_authorized_release` absent from both the compiler and browser-reported tool lists.

If the runtime badge is `WEBMCP_UNAVAILABLE`, stop. That is an environment failure, not a product PASS.

## Exact sequence

### 1. Inspect current authority

Prompt the browser agent to inspect the release control state using the page's WebMCP tool.

Expected tool: `inspect_release_control`.

Expected result:

- `status = HUMAN_REQUIRED`
- current evidence fingerprint
- no grant
- safe next action tells the agent to request authority and wait for a human

Judge point: the agent gets structured authority/evidence state from WebMCP rather than scraping prose.

### 2. Request authority

Prompt the agent to request release authority with a short reason.

Expected tool: `request_release_authority`.

Expected result/UI change:

- request recorded
- state remains `HUMAN_REQUIRED`
- pending request becomes `true`
- `humanGrantCreated = false`
- execution tool remains absent

Judge point: agent request is not approval; authority mutation remains outside model-callable tools.

### 3. Human grants the exact snapshot

Human clicks **Grant exact evidence snapshot**.

Expected result:

- state becomes `AUTHORIZED`
- grant ID is bound to the exact current evidence fingerprint
- `execute_authorized_release` appears in compiler output
- browser-reported tools also show it after the tool lifecycle propagates

Judge point: capability availability itself is an authority projection.

### 4. Agent executes the controlled action

Prompt the agent to execute the authorized controlled release with a short note.

Expected tool: `execute_authorized_release`.

Expected result:

- execute callback re-checks live state
- `status = AUTHORIZED`
- `effect = CONTROLLED_RELEASE_EXECUTED`
- `externalSideEffect = false`
- a tab-local receipt appears, bound to the evidence fingerprint and grant ID

Judge point: this is a controlled consequential-action proof, not a fake claim of an external production deployment.

### 5. Human corrects evidence

Human clicks **Correct security evidence**.

Expected result:

- security evidence revision changes
- current fingerprint changes
- prior grant no longer matches
- state becomes `INVALIDATED`
- `execute_authorized_release` disappears from compiler and browser tool lists

Judge point: correction changes the agent's future capability surface.

### 6. Explain defense in depth

State briefly that removal is not the only gate: the adversarial test retains the old execution descriptor, changes evidence, invokes the retained callback directly, and receives:

- `status = INVALIDATED`
- `effect = BLOCKED_BEFORE_EFFECT`
- zero success receipts

This closes the discovery-to-execution stale-reference gap in the tested adapter contract.

## Optional 20-second extensions

Use only if time remains or a judge asks.

- **STALE:** Reset → grant → **Expire security evidence**. Expected `STALE`, mutation tool absent.
- **BLOCKED:** Reset → **Remove required evidence**. Expected `BLOCKED`, mutation tool absent.
- **REVOCATION:** Reset → grant → **Revoke grant**. Expected `INVALIDATED`, mutation tool absent.
- **RECOVERY:** From invalidated/stale/blocked → **Restore fresh evidence**. Expected `HUMAN_REQUIRED`, prior grant cleared; a new human grant is required.

## Failure conditions

Do not describe the judge path as PASS if any of these occur:

- WebMCP runtime is unavailable.
- mutation tool appears before `AUTHORIZED`.
- agent can grant/revoke/correct/restore authority using a WebMCP tool.
- mutation tool remains browser-visible after invalidation beyond ordinary tool lifecycle propagation.
- an execution callback succeeds after current state is no longer `AUTHORIZED`.
- receipt claims an external deployment/action that did not occur.
- page requires private IDs, credentials or developer intervention.

## Evidence capture order

1. Initial `HUMAN_REQUIRED` screen with WebMCP `AVAILABLE` and safe tool list.
2. Agent inspection result.
3. Agent request + pending human request, still no execution tool.
4. Human grant → `AUTHORIZED` + execution tool visible in browser-reported list.
5. Agent execution result + controlled receipt.
6. Human correction → `INVALIDATED` + execution tool removed.
7. Terminal/test evidence for retained stale descriptor fail-closed.
8. Exact commit + public URL in final closing frame.
