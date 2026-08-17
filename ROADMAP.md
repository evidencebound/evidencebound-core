# Roadmap

## v0.1 — Independent core — implemented

Typed contracts, EBCJ-1 canonicalization, evidence/provenance/policy binding, deterministic verification, tamper-evident receipts, fail-closed outcomes, package and quickstart.

## v0.2 — Trust graph and recovery — implemented

Acyclic dependency graph, exact blast radius, selective recovery, replay/idempotency guard, plain Python adapter, external-framework callback seam and provider-neutral events.

## v0.3 — Adoption/funding baseline — released

Public API curation, threat model/spec/docs, reproducible benchmark, CI, clean-install path, license/provenance audit and funding work packages. GitHub source release `v0.3.0` is published and verified; PyPI is not published.

## Post-v0.3 hardening — implemented on Unreleased main

- provider-neutral signed receipts, explicit key lifecycle and optional Ed25519 provider;
- provider-neutral persistence contract + crash-consistent SQLite reference backend/restart recovery;
- exact Google ADK 2.7.0 lifecycle compatibility CI with fail-closed early-stop behavior;
- EBCJ-1 language-neutral conformance corpus and deterministic property-based trust/graph invariants;
- trusted-main build checksums, CycloneDX SBOM and GitHub/Sigstore provenance/SBOM attestations.

These capabilities are not retroactively part of the published `v0.3.0` tag.

## Next adoption/security work

- maintainer-authored clean-room external-consumer fixture using only public package APIs;
- independently owned external integration/adoption evidence;
- explicit future release artifact workflow with exact tag/digest/SBOM/attestation linkage;
- external security audit and remediation process;
- formal state-machine/model for invalidation/recovery;
- second independent runtime consuming EBCJ-1 conformance vectors;
- additional framework adapters only where maintenance demand is demonstrated;
- provider/schema migration conformance and fault testing;
- long-term governance and maintainer continuity.

## Non-goals / scope control

Avoid generic RAG, decorative blockchain, fake immutability, unnecessary LLM dependencies, broad dashboards, premature SaaS, and distributed complexity without a demonstrated integration need.
