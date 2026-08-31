# WebMCP × Sibyl 2026 Rules Freeze

Frozen: 2026-08-31 UTC

This file records the competition constraints used for engineering. Official rules remain authoritative if they change. Any later material change must be recorded before submission.

## OpenAI WebMCP Challenge

Authoritative sources:

- https://webmcp.devpost.com/rules
- https://webmcp.devpost.com/
- https://openai.com/webmcp-challenge/
- https://developer.chrome.com/docs/ai/webmcp/

### Compliance matrix

| Item | Frozen requirement | Engineering consequence |
|---|---|---|
| Submission period | Devpost official rules: 2026-08-25 11:00 PDT through 2026-09-03 13:00 PDT. Deadline = 2026-09-03 20:00 UTC = 23:00 Europe/Kyiv. | All competition-attributed WebMCP implementation must be traceable to post-start commits. |
| Existing work | Existing apps are allowed only if meaningfully extended using WebMCP after the submission period begins. Pre-existing work is not the judged contribution. | Maintain an explicit pre-existing-work ledger and baseline commit. |
| Required technology | Working WebMCP-powered web application. | WebMCP must be behavioral, not branding. Removing the WebMCP layer must materially degrade the agent path. |
| Judge access | Working live URL accessible in the ChatGPT in-app browser or Chrome 149+ with WebMCP enabled. Testing access must be free/unrestricted during judging; private credentials, if needed, must be supplied. | Prefer a public, credential-free controlled judge path. |
| Repository | Public source repository with source/assets/instructions and an open-source license. | Use `evidencebound/evidencebound-core` (Apache-2.0) with a clearly isolated challenge subtree and commit boundary. |
| Description | Explain why WebMCP is a fit, how it improves UX, what humans/agents can now do, and how it was implemented. | Claims ledger and README must point to exact behavior and files. |
| Video | Public YouTube demo, under 3 minutes, clear demo/audio, no unauthorized marks/music. English or English translation. | Prepare a <3 minute judge script and shot list; browser upload remains handoff work. |
| Stage One | Viability/theme/API gate. | Live app and WebMCP registration/execution must be directly inspectable. |
| Stage Two scoring | Four equally weighted criteria: WebMCP Leverage, Execution, Potential Impact, Creativity & Ambition. | Winner-gap scorecard uses 25 points per criterion. |
| Tie-break | Highest WebMCP Leverage, then Execution, then Potential Impact, then Creativity & Ambition, then judge vote. | Optimize first for load-bearing WebMCP and observable execution quality. |
| Sponsor support restriction | Rules prohibit projects developed/derived from a project that received prohibited sponsor/admin financial or preferential support before the end of the submission period. | Do not make unsupported support/partner claims; record any relevant support before submission. |
| Prize/partner scoring | No scoring multiplier was identified in the official judging rubric. Partner benefits are prize-package benefits rather than score multipliers. | Do not trade scoring-critical work for partner-logo integration. |
| Optional support | Devpost lists optional ecosystem benefits such as Netlify credits with separate eligibility/deadlines. | Treat these as funding/ops options, not judging criteria. |

### Source discrepancy

OpenAI's launch page and Devpost have shown different opening-hour text for August 25. For provenance accounting this project uses the Devpost official rules start time of 11:00 PDT, which is the stricter competition-specific source. No WebMCP implementation predating that boundary is claimed as competition work.

## Sibyl Labs — “Forgetting is a Bug”

Authoritative sources:

- https://hack.sibyllabs.org/
- https://hack.sibyllabs.org/rules

### Compliance matrix

| Item | Frozen requirement | Engineering consequence |
|---|---|---|
| Registration | 2026-08-16 through 2026-08-31 23:59 UTC. | Registration/browser confirmation is owner/browser handoff if not already authoritative. |
| Build window | 2026-09-01 00:00 UTC through 2026-09-10 23:59 UTC. In Europe/Kyiv: starts 2026-09-01 03:00 and ends 2026-09-11 02:59. | No Sibyl competition implementation before 2026-09-01 00:00 UTC. Pre-window activity is limited conservatively to rules verification, prior-art research, architecture/specification, threat modeling, acceptance design and planning. |
| Submission | Project must be marked ready by 2026-09-10 23:59 UTC. | Prepare all non-browser artifacts before handoff. |
| Judging/results | Judging 2026-09-11–12; winners 2026-09-13–15. | Do not claim outcome before authoritative result. |
| Mandatory technology | Sibyl Memory is required. | The memory integration must own core behavior, not merely record logs. |
| Load-bearing gate | Fresh session must recall persisted context and change a decision/action/result. README must point judges to critical memory write/read calls in under two minutes. Deleting the memory layer must break or materially degrade the core function. | Build an explicit deletion test and cold-start proof. |
| Cold-start demo evidence | Fresh-session recall must be shown in one continuous unedited segment with on-screen timestamp or commit hash. | Video script includes an uncut cold-start beat bound to exact commit. |
| Gate decision | Majority of panel; tie fails the gate. | Treat every load-bearing requirement as a hard acceptance gate. |
| Rubric | Memory load-bearing 40%; Innovation & originality 25%; Technical execution 20%; Pitch & presentation 15%. | Prioritize behavioral memory semantics over UI polish. |
| PMF bonus | Up to +10 for genuine publicly verifiable audience/pain/traction evidence; fabricated evidence disqualifies. | Use only real public evidence. No market-size or customer claims without proof. |
| Partner multiplier | One verified partner stack: ×1.15. Two verified stacks: ×1.25 cap. Base requires a real executed onchain action visible in demo; deployment alone does not earn the bonus. Virtuals requires a real native integration exercised in the project. | Only add partner stacks if authentic, load-bearing enough to survive the deletion/novelty story, and not harmful to WebMCP priority or reliability. |
| Repository/license | Public GitHub repository with real commit history and OSI license (MIT or Apache-2.0 accepted). | Maintain a clean competition-period commit boundary and prior-work disclosure. |
| README | Must explain why memory is load-bearing, partner stacks, how memory enabled behavior, and Prior Work. | Prepare explicit critical-call pointers and deletion test. |
| Video | 2–5 minutes; must explain problem/audience/product/memory and include fresh-session behavior. | Prepare exact script and evidence capture list. |
| Public posts | Demo video plus at least one build-log post, tagging @sibylcap and partner stacks as applicable. | Browser/social publication remains final handoff; draft copy can be prepared here. |
| Eligibility/IP | 18+; sanctioned jurisdictions excluded; project IP retained; event coverage license applies. | Never infer eligibility from code; final entrant eligibility remains owner-submission responsibility. |

## Compliance policy

1. WebMCP and Sibyl remain distinct competition submissions with separate theses, claims ledgers, judge paths and prior-work declarations.
2. Historical EvidenceBound capabilities are cited as prior work even when reused as dependencies.
3. No controlled fixture is described as external production truth.
4. `PASS` is used only for executed evidence; otherwise use `FAIL`, `UNRUN` or `BLOCKED`.
5. Final browser forms, uploads, public posts and authoritative Submitted confirmations are outside this Project Chat and require a separate browser handoff.
