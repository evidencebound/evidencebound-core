# Governance

EvidenceBound Core is currently a maintainer-led open-source project.

## Maintainer

Ruslan Vrublevskyi is the current project maintainer and release owner. This document describes the present operating model; it does not claim a foundation, steering committee, external adopters, or governance body that does not exist.

## Decision model

Changes are evaluated against the project's public trust semantics and OSS boundary. The maintainer may accept, request changes to, or decline proposals based on:

- deterministic and fail-closed behavior;
- provenance, integrity, policy and recovery correctness;
- framework/provider neutrality of the core;
- compatibility and migration cost for external adopters;
- security and privacy impact;
- testability and reproducible evidence;
- maintenance and dependency cost;
- consistency with documented non-goals.

Material trust-semantic changes should include executable regression coverage and documentation updates in the same change. LLM output or reviewer opinion cannot override deterministic verification gates.

## Public API changes

EvidenceBound is pre-1.0. Breaking changes are possible, but they should be intentional and documented. Public API changes should identify:

1. the contract being changed;
2. the security/trust consequence;
3. compatibility impact;
4. migration guidance when applicable;
5. tests proving the new behavior.

## Security-sensitive changes

Security reports follow `SECURITY.md`. Changes affecting canonicalization, receipt verification, evidence identity, policy binding, graph invalidation, replay/idempotency, or action gates require adversarial regression coverage before release.

## Releases

A release is valid only when the tagged commit has passed the repository's required CI/clean-room/security gates and the tag/release relationship has been independently verified. A package version present in source does not by itself mean that a GitHub or PyPI release exists.

## Contributions

Contributions are welcome under `CONTRIBUTING.md` and the Apache-2.0 license. Contributors should keep framework-specific integrations thin and optional; core behavior must remain usable without adopting a specific cloud, model, agent framework, or application domain.

Governance may evolve if sustained external maintainership or adoption develops. Any such change will be documented publicly rather than inferred from activity or funding.
