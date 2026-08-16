# Roadmap

## v0.1 — Independent core — implemented in current alpha candidate

Typed contracts, EBCJ-1 canonicalization, evidence/provenance/policy binding, deterministic verification, tamper-evident receipts, fail-closed outcomes, package and quickstart.

## v0.2 — Trust graph and recovery — implemented in current alpha candidate

Acyclic dependency graph, exact blast radius, selective recovery, replay/idempotency guard, plain Python adapter, external-framework callback seam and provider-neutral events.

## v0.3 — Adoption/funding readiness — current candidate scope

Public API curation, threat model/spec/docs, reproducible benchmark, CI, clean-install path, license/provenance audit and funding work packages.

## Candidate post-v0.3 work

- signed receipts with algorithm agility and external key-provider interface;
- persistence backend protocol + SQLite reference backend;
- RFC/JCS or cross-runtime canonicalization interoperability profile;
- OpenTelemetry optional exporter;
- first-class adapters for Google ADK, LangGraph and other frameworks maintained against upstream compatibility tests;
- property/fuzz test suite and formal state-machine model;
- supply-chain hardening (provenance/SBOM/reproducible release process);
- external security audit;
- graph visualization tooling outside core;
- independent integration case studies.
