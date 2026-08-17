# EvidenceBound Core

[![CI](https://github.com/moneyparking/evidencebound-core/actions/workflows/ci.yml/badge.svg)](https://github.com/moneyparking/evidencebound-core/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/moneyparking/evidencebound-core)](https://github.com/moneyparking/evidencebound-core/releases/tag/v0.3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: Apache-2.0](https://img.shields.io/github/license/moneyparking/evidencebound-core)](LICENSE)

**EvidenceBound is a framework-agnostic, LLM-independent runtime for binding agent outputs to evidence, provenance and policy; verifying protected state; computing dependency blast radius; and planning fail-closed selective recovery.**

Created and maintained by Ruslan Vrublevskyi.

> Status: **GitHub source release `v0.3.0` published 2026-08-17** from exact commit `2477164acfbdca6a843bf7b2eac5fa21ce9901b2`. The tagged source passed the full Python 3.10–3.13, clean-room, typing/build, benchmark and security CI gates before publication. PyPI is **not published**. Pre-1.0 API compatibility is not guaranteed.

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

No unconditional runtime dependency is required beyond Python 3.10+.

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
print(plan.requires_verification)
print(plan.recompute)
```

Run the complete external acceptance scenario:

```bash
python examples/golden_acceptance.py
```

It proves the intended sequence: checkpoint → receipt → tamper detection → historical integrity retained while applicability requires review → exact invalidation → consequential action blocked until successful path-specific re-verification.

## Trust semantics

Evidence state and record integrity are separate dimensions.

- `UNCHANGED`: current evidence identity and digest match the protected snapshot.
- `NEW`: a supplied current evidence ID was absent from the protected snapshot.
- `CHANGED`: the digest differs. **This does not mean REFUTED.**
- `STALE`: validity horizon has elapsed when an explicit current time is supplied.
- `MISSING`: required current evidence is absent or its supplied identity does not match the protected record.
- `REFUTED`: an upstream verifier explicitly marks evidence refuted.

Current evidence mapping keys must match the contained `EvidenceRecord.evidence_id`; an identity mismatch fails closed rather than being accepted because payload bytes happen to match.

Possible outcomes:

- historical integrity `VERIFIED` + current applicability `VERIFIED` → `ALLOW`;
- historical integrity `VERIFIED` + changed/stale/new/policy-drift applicability → `REVIEW_REQUIRED`;
- integrity failure, missing/refuted evidence, identity mismatch, or required provenance loss → `BLOCK`.

## What a receipt proves

The default receipt binds a checkpoint to a deterministic SHA-256 digest under the versioned `EBCJ-1` canonicalization domain. `verify_receipt()` validates receipt metadata and checkpoint binding; `verify_verification_receipt()` additionally binds the supplied historical verification result. Receipts are tamper-evident **when retained or anchored independently of mutable checkpoint state**.

This does not prove upstream truth or author identity and does not resist an attacker able to replace both record and trusted receipt anchor. Signed receipts/key management remain roadmap work.

## Canonicalization

`EBCJ-1` accepts null, booleans, integers, Unicode strings, lists, and string-keyed maps. Maps are sorted, JSON is compact UTF-8, and floats are rejected to avoid cross-runtime ambiguity. This is an EvidenceBound format, **not a claim of RFC 8785 compliance**. See [`SPEC.md`](SPEC.md).

## Recovery

`DependencyGraph` validates IDs/dependencies, rejects cycles, provides deterministic topological ordering, and computes exact descendants.

`plan_recovery()` distinguishes:

- `recompute`: checkpoints in the exact invalidation blast radius;
- `reusable`: unaffected checkpoints with an `ALLOW` verification result cryptographically bound to the exact checkpoint currently in the graph;
- `requires_verification`: unaffected state that cannot yet be trusted for reuse;
- `blocked`: consequential actions that may not proceed.

Re-verification requirements are dependency-path-specific, so an unrelated invalidation does not contaminate an independent branch. `ReplayGuard` provides idempotent duplicate detection; it does **not** claim exactly-once execution.

## Adapters

Core never imports an agent framework. Included integration seams:

- `evidencebound.adapters.run_guarded` — plain Python callable hook.
- `evidencebound.adapters.google_adk.AdkCallbackAdapter` — dependency-free seam matching ADK's single-`callback_context` `after_agent_callback` contract; applications provide evidence/output extractors (for example from ADK state populated via `output_key`). It is intentionally not a hard Google ADK dependency.

See [`docs/INTEGRATION.md`](docs/INTEGRATION.md).

## Verify this checkout

```bash
python -m pip install -e '.[dev]'
pytest
python examples/golden_acceptance.py
python benchmarks/selective_recovery.py
python -m compileall -q src examples benchmarks
ruff check .
mypy src/evidencebound
python -m build
```

CI additionally performs an isolated clean-room installation, runtime-dependency assertion, pip-audit, Bandit scan, wheel reinstall/import, and the benchmark acceptance scenario. See `.github/workflows/ci.yml` and [`RELEASE_READINESS.md`](RELEASE_READINESS.md).

## Security and non-goals

Read [`THREAT_MODEL.md`](THREAT_MODEL.md) before using EvidenceBound for consequential actions. The library helps detect unsupported/missing/stale/refuted evidence when that state is supplied or derivable; it cannot establish truthfulness of a malicious source, protect a compromised runtime, or guarantee legal/regulatory compliance.

## Project documents

- [`ARCHITECTURE.md`](ARCHITECTURE.md)
- [`SPEC.md`](SPEC.md)
- [`THREAT_MODEL.md`](THREAT_MODEL.md)
- [`SECURITY.md`](SECURITY.md)
- [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [`ROADMAP.md`](ROADMAP.md)
- [`RELEASE_READINESS.md`](RELEASE_READINESS.md)
- [`FUNDING_READINESS.md`](FUNDING_READINESS.md)
- [`PREEXISTING_WORK.md`](PREEXISTING_WORK.md)
- [`LICENSE_DECISION.md`](LICENSE_DECISION.md)

## License

Apache-2.0. See [`LICENSE_DECISION.md`](LICENSE_DECISION.md) for the project-specific rationale and provenance boundary.
