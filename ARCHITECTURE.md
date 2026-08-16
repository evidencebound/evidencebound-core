# Architecture

## Decision

EvidenceBound Core is a deterministic Python library. Agent/model/framework integration is outside the core boundary and communicates through structured records.

## Components

1. **Contracts** — evidence, provenance, policy binding, checkpoints, verification and receipts.
2. **Canonicalization** — versioned deterministic byte representation and domain-separated SHA-256.
3. **Verifier** — historical integrity, provenance completeness, policy compatibility, current evidence state and final action decision.
4. **Dependency graph** — acyclic checkpoint dependencies, ancestors/descendants and exact blast radius.
5. **Recovery planner** — reusable/recompute/blocked sets with deterministic ordering.
6. **Replay guard** — operation-ID + payload digest duplicate guard.
7. **Events** — provider-neutral structured event sink.
8. **Adapters** — optional integration seams; never required by core.

## Boundaries

Core does not own data retrieval, source authentication, model execution, persistence, remote key management, telemetry backend, or business policy. These are application/adaptor concerns.

## State model

Historical integrity answers whether the protected checkpoint still matches a retained receipt. Current applicability answers whether current evidence/provenance/policy permit reuse. These values are intentionally independent.

## Determinism

Given equal supported structured inputs, policy, current evidence and time input, core produces equal digests, graph ordering and recovery plans. Wall-clock time is never silently read by verification; callers pass `now` when staleness evaluation is required.
