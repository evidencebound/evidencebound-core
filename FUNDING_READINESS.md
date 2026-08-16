# Funding Readiness

## Public-good value

EvidenceBound targets a reusable gap between agent memory/tracing and consequential action: deterministic evidence/provenance/policy binding, explicit applicability, exact dependency invalidation, and fail-closed selective recovery without requiring one model, cloud or agent framework.

## Existing engineering evidence in this repository

Only executable/public artifacts should be cited as evidence: package source, tests, golden acceptance example, graph/recovery adversarial cases, benchmark script, threat model/spec and CI results at an exact commit. Reference hackathon/application repositories demonstrate prior exploration but are not evidence of independent external adoption.

## Missing maturity

- independent external adopters and interoperability fixtures;
- signed receipt/key-provider architecture;
- persistence backend protocol and crash-consistency model;
- property/fuzz testing and formal state-machine specification;
- cross-runtime canonicalization profile;
- maintained framework adapters with upstream compatibility CI;
- external security review;
- SBOM/release provenance/supply-chain hardening;
- independent performance/security benchmark review;
- long-term governance and maintainer continuity.

## Fundable work packages

### Small — Trust-contract hardening
**Problem:** alpha semantics need stronger interoperability/security evidence.  
**Deliverables:** property/fuzz suite, canonicalization interoperability fixtures, SQLite reference persistence, signed-receipt design/prototype, two maintained framework adapters.  
**Acceptance:** published spec fixtures pass independently; failure/tamper/replay cases are reproducible; clean-room quickstart works.  
**Dependencies:** contributor/reviewer time.  
**Risks:** premature API lock-in; mitigate with explicit experimental/stable namespaces.

### Medium — Interoperability and security
**Problem:** adoption requires audited boundaries across runtimes/frameworks.  
**Deliverables:** key-provider interface, signed receipts, persistence crash/recovery tests, 3–5 framework adapters, OpenTelemetry exporter, SBOM/release provenance, external security review.  
**Acceptance:** independent audit findings resolved or documented; adapter compatibility CI; reproducible releases; external integration walkthroughs.  
**Dependencies:** upstream framework stability and security reviewer availability.  
**Risks:** adapter maintenance burden; keep core protocol thin.

### Large — Multi-runtime verifiable agent-state infrastructure
**Problem:** Python-only alpha is insufficient for ecosystem-level interoperability.  
**Deliverables:** language-neutral spec, conformance suite, at least two independent runtime implementations, formal model of invalidation/recovery, external audits, sustained maintenance/governance.  
**Acceptance:** cross-runtime receipt/checkpoint fixtures, conformance matrix, audited releases and independent adopters.  
**Dependencies:** ecosystem participation and governance capacity.  
**Risks:** standardization before adoption; stage work behind real integration feedback.

## Application timing

The next credible funding milestone is not a marketing application. It is: exact-head public release candidate + clean-install acceptance + signed/persistence design issue + at least one integration outside the maintainer’s own products. Funding target status must be rechecked from official program sources at application time.
