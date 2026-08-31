# WebMCP Challenge Demo Video Script

Target length: 2:20–2:45. Hard ceiling: under 3:00.
Canonical demo: `https://evidencebound.org/webmcp/`

The video should be one concise behavioral proof, not a feature tour. Use a supported WebMCP browser. Keep the URL visible at the beginning or end. Do not record the final version if the runtime badge is not `AVAILABLE`.

## 0:00–0:15 — Thesis

**Visual:** Canonical page, initial `HUMAN_REQUIRED`, safe tool list, runtime `AVAILABLE`.

**Narration:**

> WebMCP exposes browser capability. EvidenceBound determines whether that capability is authorized now. This demo compiles current evidence, policy, and explicit human authority into the live WebMCP tool surface.

**On-screen proof:** `HUMAN_REQUIRED`; no `execute_authorized_release`.

## 0:15–0:38 — Agent can inspect and request, not approve

**Visual:** Ask the browser agent to call `inspect_release_control`, then `request_release_authority` with a short reason.

**Narration:**

> The agent can inspect the structured control state and request authority. It cannot grant, revoke, correct, or restore authority through WebMCP.

**On-screen proof:** request becomes pending; state remains `HUMAN_REQUIRED`; `humanGrantCreated=false`; execution tool remains absent.

## 0:38–0:58 — Human grant changes capability

**Visual:** Human clicks **Grant exact evidence snapshot**. Show state and both compiler/browser tool lists.

**Narration:**

> A human grants this exact evidence fingerprint. The state becomes AUTHORIZED, and only now does the consequential WebMCP capability appear.

**On-screen proof:** `AUTHORIZED`; grant ID; `execute_authorized_release` visible.

## 0:58–1:20 — Controlled execution with provenance receipt

**Visual:** Ask the agent to call `execute_authorized_release` with a short note. Show returned result and receipt ledger.

**Narration:**

> Execution re-checks live authority before committing the controlled effect. The receipt binds the grant and evidence fingerprint. This judge action is deliberately controlled: `externalSideEffect` is false, so no external deployment is being claimed.

**On-screen proof:** `CONTROLLED_RELEASE_EXECUTED`, receipt ID, `externalSideEffect=false`.

## 1:20–1:48 — Correction revokes future capability

**Visual:** Human clicks **Correct security evidence**. Show revision/fingerprint change, state, and tool lists.

**Narration:**

> Now the human records corrected evidence. The old grant no longer matches. EvidenceBound marks it INVALIDATED, and WebMCP removes the execution capability from the agent's current tool surface.

**On-screen proof:** `INVALIDATED`; execution tool absent.

## 1:48–2:10 — Defense in depth

**Visual:** Briefly show GitHub test names or CI evidence, not dense terminal scrolling.

**Narration:**

> Tool removal is not the only defense. Automated adversarial tests retain an old descriptor and prove it fails closed after correction. They also cover correction during asynchronous verification and concurrent execution races, so stale authority cannot commit a success receipt.

**On-screen proof:** green WebMCP CI / relevant test names. Do not imply these race cases were manually reproduced in the browser unless they were.

## 2:10–2:35 — Why WebMCP is load-bearing

**Visual:** Return to judge page flow diagram and public URL.

**Narration:**

> Without WebMCP, the agent loses the structured browser capability surface whose lifecycle is changing. Without EvidenceBound, that surface does not encode current authority. The result is a browser-native human control plane where capability follows evidence and revocable human authority.

**Final frame:**

```text
EvidenceBound WebMCP Authority Compiler
https://evidencebound.org/webmcp/
Public source: github.com/evidencebound/evidencebound-core
Production merge: 1655514e60e8266331cb431c7726f37725608c99
```

## Capture checklist

Before recording the final submission video:

- runtime badge is `AVAILABLE`;
- browser agent visibly uses WebMCP tools, not DOM scraping or manual simulation;
- initial execution tool is absent;
- authority request does not grant authority;
- human grant causes the execution tool to appear;
- execution creates exactly one controlled receipt;
- correction causes `INVALIDATED` and removes the execution tool;
- no private credentials, account IDs, emails, browser bookmarks, notifications, or unrelated tabs are visible;
- narration says `controlled` / `externalSideEffect=false` rather than implying a real deployment;
- video remains under 3 minutes;
- YouTube visibility and audio work from a logged-out/incognito check before submission.

## Do not say

Do not use unsupported statements such as:

- "first", "only", "unique", or "never done before";
- "production release executed" or "deployed by the agent";
- "guarantees safety";
- "unhackable", "race-free", or "formally verified";
- customer/traction/compliance claims not backed by separate evidence;
- "submission complete" before authoritative Devpost confirmation.
