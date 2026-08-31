# EvidenceBound Competition Pre-existing Work Ledger

Frozen for WebMCP baseline: 2026-08-31

WebMCP competition branch: `feat/webmcp-authority-compiler-2026`
Baseline parent: `evidencebound/evidencebound-core@9a2137fe29d0532120a774398a45fa90a9850153`

This ledger is deliberately conservative. If a concept or working behavior existed before the WebMCP submission period, it is treated as prior work even if the new challenge integration makes it more visible or reusable.

## EvidenceBound Core — pre-existing

Repository: `evidencebound/evidencebound-core`

Pre-existing before this branch includes:

- evidence and provenance records;
- deterministic canonicalization and digests;
- policy binding;
- historical integrity vs current applicability;
- `ALLOW`, `REVIEW_REQUIRED`, and `BLOCK` action decisions;
- current-evidence states including `UNCHANGED`, `CHANGED`, `NEW`, `STALE`, `MISSING`, and `REFUTED`;
- dependency graphs, cycle rejection and exact descendant/blast-radius computation;
- invalidation and selective recovery planning;
- proof receipts and optional Ed25519 signed receipts;
- durable SQLite persistence with revalidation after restart;
- replay/idempotency guards;
- plain-Python and Google ADK adapter seams;
- fail-closed consequential-action gating;
- adversarial, persistence, signing, recovery and conformance tests.

Public release `v0.3.0` predates the WebMCP competition. Current baseline main also contains unreleased hardening. None of these generic primitives are claimed as WebMCP-period inventions.

## Authority Cut — pre-existing

Repository: `evidencebound/evidencebound-authority-cut`

Pre-existing before WebMCP includes:

- semantic human authority atoms;
- policy-defined authority bundles and minimal actionable authority-cut computation;
- external-human-only grant/revocation boundary;
- model-callable tool boundary separate from authority mutation;
- downstream correction/revocation propagation;
- reversible compensation of executed descendants;
- preservation of unrelated safe work;
- invalidation of a pending irreversible descendant;
- Strands/AgentCore judge implementation and evidence.

Therefore WebMCP work must not claim to invent human approval, revocable grants, semantic authority, correction propagation, compensation, or irreversible-action invalidation generally.

## Recovery Mesh — pre-existing

Repository: `evidencebound/evidencebound-recovery-mesh`

Pre-existing before WebMCP includes:

- trust as a dependency graph;
- exact blast-radius computation;
- fail-closed blocked action state;
- selective recomputation and reuse of unaffected verified work;
- durable Firestore trust ledger;
- deterministic rehydration validation;
- idempotent action receipts;
- production Cloud Run/Cloud Logging acceptance for its controlled workload.

Therefore WebMCP work must not claim selective recovery, trust-graph invalidation, durable trust state or exact blast radius as new.

## Verified Memory — pre-existing and especially relevant to Sibyl

Repository: `moneyparking/moneyparking-evidencebound-verified-memory`

Pre-existing before the Sibyl build window includes:

- durable verified-memory records in CockroachDB;
- fresh-session reload;
- historical integrity separated from current applicability;
- deterministic time-travel diff with `UNCHANGED`, `CHANGED`, `STALE`, and `NEW`;
- fail-closed tamper detection;
- provenance-aware snapshot hashing;
- vector incident recall;
- bounded Bedrock explanation after deterministic state is finalized.

Therefore the Sibyl submission must go materially beyond “persistent verified memory”, “fresh session recall”, or “historical record remains intact while applicability changes”. The planned competition-period contribution is correction-aware authority memory: later correction/revocation must invalidate dependent operational authority across fresh sessions without erasing historical recall, and the Sibyl layer must pass an explicit deletion test.

## DataHub Gate — pre-existing

Repository: `moneyparking/evidencebound-datahub-gate`

Pre-existing before WebMCP/Sibyl includes:

- verify-before-use DataHub MCP read path;
- deterministic fail-closed current/stale schema gates;
- claim-to-evidence binding;
- tamper-evident and Ed25519-sealed proof packs;
- native DataHub MCP write-back receipts;
- mandatory human review kept outside automated promotion.

Therefore generic MCP integration, MCP read/write, proof packs and a mandatory human-review boundary are not new WebMCP claims.

## SignalReview and other applications — pre-existing

SignalReview and other EvidenceBound reference applications predate these competitions. Their business logic, production metrics, provider data and customer claims are not part of either competition contribution unless explicitly and truthfully re-established in the relevant submission.

## New WebMCP contribution boundary

The WebMCP branch may claim only behavior added after the official submission-period start and evidenced by commits on/after the baseline above. Target contribution:

1. a browser-native authority compiler that maps current EvidenceBound control state into the live WebMCP tool surface;
2. lifecycle-bound WebMCP registration/removal so the model-visible capability set changes when authority validity changes;
3. execute-time authority revalidation that fails closed even if an agent holds a stale tool reference;
4. browser-visible typed control states `AUTHORIZED`, `HUMAN_REQUIRED`, `STALE`, `INVALIDATED`, and `BLOCKED` derived from evidence/policy/authority inputs;
5. WebMCP invocation receipts tied to the authority snapshot used at execution;
6. a credential-free judge path proving correction/revocation changes future agent behavior.

This is a new browser/WebMCP integration of prior EvidenceBound primitives, not a claim that the underlying authority, provenance, invalidation or receipt ideas originated during the WebMCP period.

## New Sibyl contribution boundary

No Sibyl competition implementation is permitted by this project before 2026-09-01 00:00 UTC. The planned new contribution is intentionally not implemented yet. Its target novelty claim must remain narrower than pre-existing Verified Memory:

- persisted memory records retain history and provenance;
- later corrections/revocations create explicit validity transitions;
- dependency-linked operational authority becomes invalidated;
- a fresh session recalls both original history and correction;
- obsolete authority remains historically queryable but cannot become operational again;
- removing Sibyl Memory breaks the correction-aware fresh-session control behavior.

Prior-art research, design, threat modeling and acceptance planning before the build window are preparation, not competition implementation.
