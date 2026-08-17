# Durable Persistence

Status: **Unreleased on `main` after v0.3.0**. The published `v0.3.0` tag does not contain this persistence API.

EvidenceBound persistence has two layers:

1. `PersistenceStore` — a provider-neutral protocol owned by core.
2. `evidencebound.providers.sqlite.SQLiteStore` — a stdlib SQLite reference implementation.

SQLite support adds no third-party runtime dependency.

## Trust rule

Persisted state is not trusted merely because it was previously written.

`SQLiteStore.load_verification()` reconstructs the persisted checkpoint, receipt and verification state and runs `verify_verification_receipt()` before returning the verification result. Missing, malformed, version-incompatible or tampered state raises a persistence error instead of becoming reusable state.

`load_checkpoint()` is intentionally weaker: it reconstructs a checkpoint record but does **not** assert that the checkpoint is trusted, current or reusable.

## Atomic bundle

`commit_bundle()` writes the following records in one SQLite transaction:

- checkpoint;
- proof receipt;
- verification state;
- optional replay/idempotency record.

The verification receipt must already bind to the exact checkpoint supplied to `commit_bundle()`. When an operation ID is supplied, it must match the checkpoint's `operation_id` and the replay payload is bound through the existing `operation` digest domain.

A failure before commit rolls the entire bundle back. A failure after commit can leave a complete durable bundle; reopening the database re-validates the stored binding before returning verification state.

The reference adapter uses explicit `BEGIN IMMEDIATE`, foreign-key enforcement and `synchronous=FULL`. File-backed databases use SQLite WAL mode. These choices are reference durability settings, not a claim that SQLite is immutable or resilient to arbitrary filesystem/host compromise.

## Restart and recovery

```python
from evidencebound import plan_recovery
from evidencebound.providers.sqlite import SQLiteStore

with SQLiteStore("agent-state.sqlite3") as store:
    store.commit_bundle(checkpoint, verification)

# New process / later restart
with SQLiteStore("agent-state.sqlite3") as store:
    graph, verification_by_id = store.load_recovery_state()

plan = plan_recovery(
    graph,
    invalidations,
    verification=verification_by_id,
    consequential=consequential_checkpoint_ids,
)
```

`load_graph()` reconstructs checkpoints in deterministic order and then runs normal `DependencyGraph` validation. Missing dependencies, cycles, inconsistent checkpoint IDs or malformed records fail closed.

`load_recovery_state()` requires a valid, receipt-bound verification record for every persisted checkpoint. It does not silently drop a corrupted verification row and continue as if the rest of the persisted workflow were trustworthy.

## Replay after restart

`SQLiteReplayGuard` provides the same public duplicate/conflict behavior as the in-memory replay guard, but stores the operation digest durably:

```python
from evidencebound.providers.sqlite import SQLiteReplayGuard, SQLiteStore

with SQLiteStore("agent-state.sqlite3") as store:
    guard = SQLiteReplayGuard(store)
    guard.apply("operation-42", {"request": "payload"})
```

After restart:

- same operation ID + same payload → `ALREADY_APPLIED`;
- same operation ID + different payload → `ReplayConflict`.

This is an idempotency primitive. EvidenceBound does **not** claim distributed exactly-once execution.

## Crash semantics

The test suite injects failures around checkpoint, receipt, verification and replay writes.

Expected semantics:

- interruption before transaction commit → no partial bundle is visible after reopen;
- interruption after transaction commit → the complete bundle remains available and must still pass receipt/checkpoint re-verification;
- a replay record without the exact matching durable bundle is treated as an integrity error, not proof that the associated consequential state is safe to reuse.

## Schema/version policy

The SQLite schema currently uses persistence schema version `1`; individual stored record rows use record version `1`.

Unknown versions fail closed with `UnsupportedPersistenceSchema`. The alpha implementation intentionally does not auto-migrate unknown schemas because silently reinterpreting trust-bearing historical state would weaken the verification boundary.

Future migrations must be explicit, versioned and covered by reconstruction/integrity tests.

## Corruption and external modification

The SQLite adapter is not an authenticated database. A process or attacker with database write access can change bytes. EvidenceBound therefore re-checks deterministic receipt/result binding on load.

This detects many mutations when the retained receipt is not rewritten consistently. For stronger protection against an attacker able to replace checkpoint and receipt state together, retain/anchor receipts independently and/or use the signed-receipt API with verification trust roots protected outside the mutable database as appropriate to the application threat model.

## Non-goals

The reference adapter does not provide:

- distributed consensus;
- multi-node replication;
- immutable storage;
- secure backups;
- filesystem or host compromise resistance;
- automatic schema migration;
- distributed exactly-once side effects;
- application-specific database schemas.

See `THREAT_MODEL.md`, `SPEC.md`, and `docs/SIGNED_RECEIPTS.md`.