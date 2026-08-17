# Architecture

## Decision

EvidenceBound Core is a deterministic Python library. Agent/model/framework integration is outside the core boundary and communicates through structured records.

## Components

1. **Contracts** — evidence, provenance, policy binding, checkpoints, verification and receipts.
2. **Canonicalization** — versioned deterministic byte representation and domain-separated SHA-256.
3. **Verifier** — historical integrity, provenance completeness, policy compatibility, current evidence state and final action decision.
4. **Signed receipt boundary** — provider-neutral signer/verifier protocols with optional concrete crypto providers.
5. **Dependency graph** — acyclic checkpoint dependencies, ancestors/descendants and exact blast radius.
6. **Recovery planner** — reusable/recompute/blocked sets with deterministic ordering.
7. **Replay guard** — operation-ID + payload digest duplicate/conflict semantics.
8. **Persistence boundary** — provider-neutral durable-state protocol plus optional/reference stores that must re-verify persisted trust state on load.
9. **Events** — provider-neutral structured event sink.
10. **Adapters** — optional integration seams; never required by core.

## Boundaries

Core does not own data retrieval, source truth, model execution, remote key management, telemetry backend or business policy. Persistence is defined as a protocol boundary; the stdlib SQLite implementation is a reference provider under `evidencebound.providers.sqlite`, not a mandatory database architecture.

The core package has no unconditional database or cryptography dependency. Framework, signing and persistence implementations remain replaceable behind thin contracts.

## State model

Historical integrity answers whether the protected checkpoint still matches a retained receipt. Current applicability answers whether current evidence/provenance/policy permit reuse. These values are intentionally independent.

Durability is a third dimension. A durable record proves only that bytes survived a storage transition; it does not prove those bytes remain trustworthy. Persistence providers therefore reconstruct stored checkpoints/results and re-run EvidenceBound binding checks before verification state can feed recovery as reusable state.

## Persistence transaction boundary

The SQLite reference store treats checkpoint, proof receipt, verification state and optional replay/idempotency state as one commit bundle. A crash before transaction commit must expose none of that bundle after reopen. A crash after commit may expose the complete bundle, which must still pass deterministic binding verification before reuse.

A durable replay record is not itself authorization to reuse consequential checkpoint state. When replay state is committed with a checkpoint bundle, duplicate replay is accepted only if the durable checkpoint/receipt/verification bundle exactly matches the original operation.

## Restart reconstruction

`load_graph()` reconstructs persisted checkpoints and delegates graph validity to the normal `DependencyGraph`; missing dependencies, cycles and inconsistent IDs fail closed.

`load_recovery_state()` returns the graph together with only verification results that have been reconstructed with their persisted receipt and revalidated against the exact persisted checkpoint. The current reference implementation requires complete verified state for every persisted checkpoint rather than silently dropping corruption.

## Determinism

Given equal supported structured inputs, policy, current evidence and time input, core produces equal digests, graph ordering and recovery plans. Wall-clock time is never silently read by verification; callers pass `now` when staleness evaluation is required.

Persistence serialization uses the same supported canonical JSON shape. Database row ordering is never used as trust semantics; graph reconstruction and recovery ordering are derived deterministically from checkpoint identities/dependencies.

See [`docs/PERSISTENCE.md`](docs/PERSISTENCE.md), [`SPEC.md`](SPEC.md), and [`THREAT_MODEL.md`](THREAT_MODEL.md).