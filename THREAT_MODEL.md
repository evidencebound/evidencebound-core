# Threat Model

## Security goal

Make evidence-dependent agent state explicit, bind protected records deterministically, optionally authenticate receipt issuers through provider-neutral signatures, preserve fail-closed semantics across supported durable-state transitions, and prevent unsafe reuse from silently crossing dependency invalidation boundaries.

## Helps detect / contain

- mutation of a checkpoint while a retained receipt is available;
- mutation of a signed receipt envelope or protected receipt metadata when a trusted verification key is available;
- wrong/unknown/revoked signing-key identities and unsupported signature algorithms;
- missing required evidence or provenance;
- evidence staleness when a validity horizon and caller-supplied current time are available;
- explicit evidence refutation supplied by a trusted upstream verifier;
- policy ID/version drift;
- dependency contamination through exact descendant invalidation;
- unsafe reuse after invalidation;
- duplicate/conflicting operation replay, including through the SQLite durable replay adapter;
- malformed graph state such as cycles, missing dependencies and duplicate checkpoint IDs;
- incomplete/tampered supported SQLite persistence records when deterministic receipt/result binding no longer verifies;
- pre-commit interruption of a supported SQLite bundle, which is rolled back rather than exposed as partial trusted state.

## Does not automatically solve

- truthfulness, completeness or honesty of an upstream source;
- authenticity of provenance that is not separately authenticated;
- compromise or theft of a trusted signing private key;
- compromise of the application key registry / trust configuration;
- an attacker who can consistently replace mutable checkpoint, receipt and trust-root state together;
- compromised host/runtime/interpreter;
- arbitrary Byzantine consensus;
- model alignment or prompt-injection generally;
- correctness of an application’s policy;
- legal/regulatory compliance;
- distributed exactly-once side effects;
- filesystem, disk-controller or SQLite-library correctness under arbitrary hardware failure;
- immutable storage, replicated durability, secure backup or disaster recovery;
- HSM/KMS operation or organization-specific key custody.

## Main attacker/error cases

| Case | Expected behavior |
|---|---|
| Protected output modified | prior receipt mismatch → BLOCK |
| Signed receipt field modified | detached signature fails → signed receipt not verified |
| Signed receipt valid but checkpoint modified | signature may remain valid, binding fails → `INVALID_BINDING` |
| Wrong existing key ID substituted | signature verification fails |
| Unknown key ID | `UNKNOWN_KEY` → fail closed |
| Revoked verification key | `REVOKED_KEY` → fail closed |
| Retired verification key | historical verification may succeed as `VERIFIED_RETIRED_KEY`; new signing with retired key is rejected |
| Unsupported algorithm | `UNSUPPORTED_ALGORITHM` → fail closed |
| Malformed signature encoding | `INVALID_SIGNATURE` → fail closed |
| Signature provider raises unexpectedly | `PROVIDER_ERROR` → fail closed |
| Unsigned legacy receipt | deterministic binding may verify, but authentication status remains `UNSIGNED` |
| Persisted checkpoint changed without matching receipt/result update | reopen re-verification fails → persistence integrity error |
| Persisted verification state changed | verification digest binding fails → persistence integrity error |
| Receipt/verification row missing | recovery-state load fails closed; state is not reusable |
| Crash before SQLite bundle commit | transaction rolls back; partial bundle is not exposed after reopen |
| Crash after SQLite bundle commit | complete durable bundle may remain; receipt/checkpoint/result binding is rechecked on reopen |
| Replay record survives restart | equal payload → `ALREADY_APPLIED`; different payload → `ReplayConflict` |
| Replay record exists but matching bundle is missing/different | bundle replay fails with persistence integrity error |
| Unknown persistence/record schema version | `UnsupportedPersistenceSchema`; no silent migration |
| Provenance deleted | required provenance incomplete → BLOCK |
| Current evidence missing | MISSING → BLOCK |
| Digest changes | CHANGED → REVIEW_REQUIRED, never implicit REFUTED |
| Explicit refutation | REFUTED → BLOCK |
| Policy version changes | historical integrity may remain VERIFIED; reuse requires review |
| Graph cycle | construction/reconstruction fails |

## Signing trust assumptions

A signed receipt authenticates that a configured key accepted by the application signed the exact signed-envelope bytes. Mapping `key_id` to an organization, service, operator or hardware root is an application/provider responsibility.

Key state is explicit:

- `ACTIVE`: may sign and verify;
- `RETIRED`: may verify historical receipts but MUST NOT create new receipts through `sign_receipt()`;
- `REVOKED`: verification fails closed;
- `UNKNOWN`: verification fails closed.

Applications must distribute and protect verification trust roots independently enough for their threat model. A signature does not turn an untrusted evidence source into a truthful one.

The optional Ed25519 reference provider is an interoperability example, not a production key-management system. Private-key generation, storage, rotation, audit, access control and compromise response remain deployment responsibilities.

## Persistence trust assumptions

The SQLite reference adapter provides a transaction/restart safety model, not immutable or authenticated storage. Persisted `VerificationResult` data is revalidated against its receipt and exact checkpoint on load; existence in a database never upgrades trust by itself.

The adapter's pre-commit crash guarantees rely on SQLite transaction semantics and the configured local storage behaving within SQLite's documented guarantees. It uses foreign keys, explicit `BEGIN IMMEDIATE`, `synchronous=FULL`, and WAL for file-backed databases. These settings do not provide distributed consensus or protection from a fully compromised host.

If the threat model includes an attacker who can rewrite both checkpoint and unsigned receipt rows consistently, the application needs an independent receipt anchor and/or signed receipts with verification roots protected outside that mutable database. A database row marked `ALLOW` is never sufficient evidence on its own.

## Other trust assumptions

Provenance locators are assertions unless independently verified by an adapter/application. System time is a caller input; EvidenceBound does not silently claim secure time.

## Future hardening

Formal persistence-provider conformance fixtures, schema-migration testing beyond version 1, filesystem fault testing, property/fuzz suites, cross-runtime interoperability fixtures, release provenance/SBOM and independent security review remain roadmap work.
