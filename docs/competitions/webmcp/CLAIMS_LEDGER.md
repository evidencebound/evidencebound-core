# WebMCP Claims Ledger

Date: 2026-08-31

Every submission/demo claim should map to one of these evidence classes. Do not upgrade a claim when its evidence is only historical, controlled, preview-only, or unrun.

| Claim | Evidence class | Evidence | Allowed wording | Prohibited/unsupported wording |
|---|---|---|---|---|
| EvidenceBound Core predates this challenge. | Repository history / prior-work disclosure | Baseline `9a2137fe29d0532120a774398a45fa90a9850153`, `PREEXISTING_WORK.md`, competition prior-work ledger. | “We extended an existing EvidenceBound control runtime with a new WebMCP authority projection.” | “EvidenceBound Core was built for this challenge.” |
| The WebMCP implementation was added after the challenge start. | Git history | Competition branch forks from the post-start baseline and every `site/webmcp/` implementation commit is later than the official start boundary. | “The WebMCP integration and judge surface were implemented during the submission period.” | Any claim that older authority/provenance/recovery primitives are challenge-period work. |
| The app exposes five deterministic control states. | Source + executed unit tests | `control-core.mjs`; `control-core.test.mjs`; dedicated WebMCP workflow. | “The controlled workflow evaluates AUTHORIZED, HUMAN_REQUIRED, STALE, INVALIDATED and BLOCKED.” | “These states prove upstream truth.” |
| Human authority is not model-callable. | Source + executed adversarial/static tests | Tool registry contains only inspect/request/list/execute; tests reject grant/approve/revoke/correct/restore tool names. | “The agent can request authority but cannot grant, revoke, correct, or restore it through WebMCP.” | “The agent can never affect any human-controlled state under every possible host integration.” |
| `execute_authorized_release` is conditional on current authority. | Source + executed lifecycle tests | `webmcp-adapter.mjs`; FakeModelContext lifecycle tests. | “The WebMCP mutation capability is registered only while the current state is AUTHORIZED.” | “Chrome production behavior was observed” until supported-browser proof exists. |
| Correction removes future mutation capability. | Source + executed lifecycle test | Test transitions AUTHORIZED → corrected `INVALIDATED`, `sync()` aborts conditional registration. | “In the tested WebMCP adapter contract, correction removes the mutation capability.” After browser proof: “The live browser removes it.” | “All browsers immediately forget stale tools” without real supported-browser evidence. |
| A retained stale callback fails closed. | Executed adversarial test | Test retains actual execution descriptor, changes evidence, calls retained callback, receives `INVALIDATED` + `BLOCKED_BEFORE_EFFECT`, zero receipts. | “Capability removal is defense in depth; execute-time revalidation blocks a retained stale descriptor.” | “No TOCTOU risk exists.” |
| Re-grant cannot bypass invalidation. | Executed unit test | RED on commit `57510a0...`, GREEN after `1adda44...`. | “Invalidated/revoked authority requires explicit recovery before a replacement grant.” | “Revocation is globally irreversible.” |
| Agent authority request never grants authority. | Source + executed test | `request_release_authority` calls `recordPendingAuthorityRequest`; test asserts grant remains null. | “An agent request is a visible request only.” | “The request tool is read-only.” It intentionally changes a local pending-request flag. |
| Controlled execution emits a receipt. | Source + executed test | `createExecutionReceipt()` requires AUTHORIZED; adapter test confirms receipt. | “Authorized controlled execution produces a tab-local receipt bound to the evidence/grant snapshot.” | “Immutable ledger”, “externally anchored”, “production deployment receipt”, “cryptographically authenticated issuer”. |
| Judge app has no external side effect. | Source + static test | `externalSideEffect:false`; no fetch/XHR/WebSocket; controlled boundary visible. | “The canonical judge path does not deploy or mutate an external system.” | “Production release automation.” |
| Browser modules are dependency-free/self-hosted. | Source + CI/static test | ES modules only, no package install; CSP `script-src 'self'`; static test rejects external script sources. | “The challenge browser app adds no npm/runtime dependency and loads self-hosted JS.” | “Supply-chain risk is zero.” |
| Full Core CI passes at critical implementation head. | Executed GitHub Actions | CI run `33364696242`, exact SHA `1adda44a35d4b96c937e4fa5dd4f7ac7c7cd5e7b`, conclusion success. | “Full Core CI passed at the critical implementation head.” | “Every future commit is green.” Re-verify final head/merge. |
| Exact implementation preview built successfully. | Deployment evidence | Vercel `dpl_CmNKp1zRBgcEjHPCVHddY9vjx1v9`, SHA `1adda44...`, state READY. | “The exact implementation head has a READY Vercel preview build.” | “The preview is publicly judge-accessible” — project-tool readback hit SSO protection. |
| Public production URL works. | Production smoke | Not yet observed at this ledger revision. | **Do not claim yet.** | “Live at evidencebound.org/webmcp/” until post-merge HTTP/browser evidence. |
| Real WebMCP discovery/invocation works in a supported browser. | Browser acceptance | Not yet executed in this Project Chat. | **Do not claim PASS yet.** | Any statement that Node/FakeModelContext tests alone prove Chrome/ChatGPT browser behavior. |
| This is the first/only implementation of the pattern. | None | Prior-art research found related dynamic-tool and permission patterns; exhaustive novelty proof was not established. | “Our challenge-period contribution combines authority projection, correction-driven tool lifecycle and execute-time revalidation.” | “First”, “only”, “unique”, or equivalent absolute novelty claims. |

## Submission wording policy

1. Prefer falsifiable behavioral claims over adjectives.
2. Distinguish tested adapter behavior, preview deployment state, public production state, and supported-browser observation.
3. Treat WebMCP issue/discussion prior art as overlapping context, not as evidence that the exact composition is novel.
4. Do not claim users, revenue, enterprise adoption, partner support, competition outcome or judge reaction without external evidence.
5. If final production behavior contradicts this ledger, downgrade the claim and fix/retest before submission rather than preserving the narrative.
