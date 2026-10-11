# Roadmap

## v0.1 — Independent core — implemented

Typed contracts, EBCJ-1 canonicalization, evidence/provenance/policy binding, deterministic verification, tamper-evident receipts, fail-closed outcomes, package and quickstart.

## v0.2 — Trust graph and recovery — implemented

Acyclic dependency graph, exact blast radius, selective recovery, replay/idempotency guard, plain Python adapter, external-framework callback seam and provider-neutral events.

## v0.3 — Adoption/funding baseline — released

Public API curation, threat model/spec/docs, reproducible benchmark, CI, clean-install path, license/provenance audit and funding work packages. GitHub source release `v0.3.0` was published on 2026-08-17. The subsequent `v0.4.0` release was published on GitHub and PyPI on 2026-10-05.

## v0.4.0 — published on GitHub and PyPI, 2026-10-05

- provider-neutral signed receipts, explicit key lifecycle and optional Ed25519 provider;
- provider-neutral persistence contract + crash-consistent SQLite reference backend/restart recovery;
- exact Google ADK 2.7.0 lifecycle compatibility CI with fail-closed early-stop behavior;
- EBCJ-1 language-neutral conformance corpus and deterministic property-based trust/graph invariants;
- trusted-main build checksums, CycloneDX SBOM and GitHub/Sigstore provenance/SBOM attestations.

These capabilities belong to `v0.4.0` and are not retroactively part of the original `v0.3.0` source release.

## Next adoption/security work

- maintainer-authored clean-room external-consumer fixture using only public package APIs;
- independently owned external integration/adoption evidence;
- independently verified consumption of release-artifact provenance;
- external security audit and remediation process;
- formal state-machine/model for invalidation/recovery;
- second independent runtime consuming EBCJ-1 conformance vectors;
- additional framework adapters only where maintenance demand is demonstrated;
- provider/schema migration conformance and fault testing;
- long-term governance and maintainer continuity.

## Non-goals / scope control

Avoid generic RAG, decorative blockchain, fake immutability, unnecessary LLM dependencies, broad dashboards, premature SaaS, and distributed complexity without a demonstrated integration need.
