# EvidenceBound Core

**EvidenceBound is a framework-agnostic, LLM-independent runtime for binding agent outputs to evidence, provenance and policy; verifying protected state; computing dependency blast radius; and planning fail-closed selective recovery.**

Created and maintained by Ruslan Vrublevskyi.

> Status: `0.3.0` alpha candidate. The API is intentionally small, but pre-1.0 compatibility is not guaranteed. Release claims require the repository CI/release gate to pass at the exact tagged commit.

## Why EvidenceBound?

Agent memory answers “what did the system remember?” EvidenceBound adds “what evidence supported it, which policy governed it, is the historical record intact, is it still applicable, and what must be recomputed if a dependency changes?”

It is **not** a vector database, RAG framework, tracing backend, LLM framework, truth oracle, or consensus system. A cryptographic digest can bind bytes; it cannot make a malicious upstream source truthful.

```mermaid
flowchart LR
  A[Agent / workflow] --> B[thin adapter]
  B --> C[EvidenceBound Core]
  C --> D[Evidence + provenance binding]
  D --> E[Deterministic verification]
  E --> F[Policy/version binding]
  F --> G[Trust graph + invalidation]
  G --> H[Recovery plan + proof receipt]
  H --> I{Action gate}
  I -->|ALLOW| J[Application action]
  I -->|REVIEW_REQUIRED| K[Review / reverify]
  I -->|BLOCK| L[Fail closed]
```

## Install

From a checkout:

```bash
python -m pip install .
```

No runtime dependency is required beyond Python 3.10+.

## 5-minute quickstart

```python
from evidencebound import (
    EvidenceBound, EvidenceRecord, InvalidationReason,
    PolicyBinding, ProvenanceRecord,
)

policy = PolicyBinding("research-policy", "1")
eb = EvidenceBound(policy=policy)

evidence = [EvidenceRecord(
    evidence_id="paper-1",
    payload={"claim": "observed"},
    provenance=ProvenanceRecord("paper", "doi:10.0000/example"),
)]

research = eb.checkpoint(
    agent="researcher",
    evidence=evidence,
    output={"summary": "supported"},
)

decision = eb.verify(research)
print(decision.action)         # ALLOW for this complete/current snapshot
print(decision.receipt)        # tamper-evident binding receipt

plan = eb.invalidate(
    checkpoint_id=research.checkpoint_id,
    reason=InvalidationReason.EVIDENCE_CHANGED,
)
print(plan.reusable)
print(plan.recompute)
```

Run the complete external acceptance scenario:

```bash
python examples/golden_acceptance.py
```

It proves the intended sequence: checkpoint → receipt → tamper detection → historical integrity retained while applicability requires review → exact invalidation → consequential action blocked until successful re-verification.

## Trust semantics

Evidence state and record integrity are separate dimensions.

- `UNCHANGED`: current evidence digest equals the protected snapshot.
- `CHANGED`: the digest differs. **This does not mean REFUTED.**
- `STALE`: validity horizon has elapsed.
- `MISSING`: required current evidence is absent.
- `REFUTED`: an upstream verifier explicitly marks evidence refuted.

Possible outcomes:

- historical integrity `VERIFIED` + current applicability `VERIFIED` → `ALLOW`;
- historical integrity `VERIFIED` + changed/stale/policy-drift applicability → `REVIEW_REQUIRED`;
- integrity failure, missing/refuted evidence, or required provenance loss → `BLOCK`.

## What a receipt proves

The default receipt binds a checkpoint to a deterministic SHA-256 digest under the versioned `EBCJ-1` canonicalization domain. It is tamper-evident **when the receipt/digest is retained or anchored independently of the mutable checkpoint**. It does not prove upstream truth or author identity and does not resist an attacker able to replace both record and trusted receipt anchor. Signed receipts/key management are roadmap work.

## Canonicalization

`EBCJ-1` accepts null, booleans, integers, Unicode strings, lists, and string-keyed maps. Maps are sorted, JSON is compact UTF-8, and floats are rejected to avoid cross-runtime ambiguity. This is an EvidenceBound format, **not a claim of RFC 8785 compliance**. See [`SPEC.md`](SPEC.md).

## Recovery

`DependencyGraph` validates IDs/dependencies, rejects cycles, provides deterministic topological ordering, and computes exact descendants. `plan_recovery()` separates reusable checkpoints from affected/recompute work. `ReplayGuard` provides idempotent duplicate detection; it does **not** claim exactly-once execution.

## Adapters

Core never imports an agent framework. Included integration seams:

- `evidencebound.adapters.run_guarded` — plain Python callable hook.
- `evidencebound.adapters.google_adk.AdkCallbackAdapter` — dependency-free seam matching ADK's single-`callback_context` `after_agent_callback` contract; applications provide evidence/output extractors (for example from ADK state populated via `output_key`). It is intentionally not a hard Google ADK dependency.

See [`docs/INTEGRATION.md`](docs/INTEGRATION.md).

## Verify this checkout

```bash
python -m pip install -e .
pytest
python examples/golden_acceptance.py
python benchmarks/selective_recovery.py
python -m compileall -q src examples benchmarks
```

For release CI, lint/type/build/security/clean-install gates are also run. See `.github/workflows/ci.yml`.

## Security and non-goals

Read [`THREAT_MODEL.md`](THREAT_MODEL.md) before using EvidenceBound for consequential actions. The library helps detect unsupported/missing/stale/refuted evidence when that state is supplied or derivable; it cannot establish truthfulness of a malicious source, protect a compromised runtime, or guarantee legal/regulatory compliance.

## Project documents

- [`ARCHITECTURE.md`](ARCHITECTURE.md)
- [`SPEC.md`](SPEC.md)
- [`THREAT_MODEL.md`](THREAT_MODEL.md)
- [`SECURITY.md`](SECURITY.md)
- [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [`ROADMAP.md`](ROADMAP.md)
- [`FUNDING_READINESS.md`](FUNDING_READINESS.md)
- [`PREEXISTING_WORK.md`](PREEXISTING_WORK.md)
- [`LICENSE_DECISION.md`](LICENSE_DECISION.md)

## License

Apache-2.0. See [`LICENSE_DECISION.md`](LICENSE_DECISION.md) for the project-specific rationale and provenance boundary.
