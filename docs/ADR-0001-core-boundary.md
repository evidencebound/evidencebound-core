# ADR-0001: Deterministic framework-independent core

**Status:** Accepted, 2026-08-16.

EvidenceBound Core accepts structured evidence/provenance/policy/checkpoint inputs and emits deterministic verification, receipt, graph and recovery outputs. It does not execute LLMs, fetch evidence, schedule agents, persist state, or require a framework/cloud SDK.

Consequences: low runtime dependency/supply-chain surface and easy embedding; adapters must translate framework state into explicit contracts; authenticity and persistence guarantees remain separate responsibilities.
