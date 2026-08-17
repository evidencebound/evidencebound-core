# AI-BOOST Challenge 4 — Background / Foreground IP Boundary

This note exists to prevent accidental ambiguity between pre-existing EvidenceBound work and new Challenge 4 work.

## Background IP — pre-existing before Challenge 4

The following are pre-existing EvidenceBound assets and are **not authored as Challenge 4 foreground**:

- `moneyparking/evidencebound-core`, including the Apache-2.0 runtime, canonicalization, evidence/provenance binding, trust/applicability verification, dependency graph, blast-radius analysis, selective recovery, replay/persistence/signing seams, conformance corpus, threat model, governance and release artifacts.
- EvidenceBound Recovery Mesh reference implementation and its trust-break/selective-recovery design evidence.
- EvidenceBound DataHub Gate reference implementation and its evidence-pack / deterministic verification / proof-receipt patterns.
- EvidenceBound Verified Memory reference implementation and its historical-integrity / current-applicability separation.
- EvidenceBound public architecture, research lineage, website, brand and maintainer identity.

These assets remain subject to their existing licenses and ownership terms. Merely using or adapting interfaces from EvidenceBound Core in the Challenge 4 solution does not reclassify the pre-existing Core as newly developed challenge foreground.

## Proposed Challenge 4 foreground

The intended Challenge 4 foreground is limited to new work specifically developed to solve the Siemens / RobustifAI crash-to-validation scenario challenge, including where newly authored:

- crash/safety dataset ingestion adapters;
- Functional Scenario taxonomy extraction pipeline;
- Logical Scenario multimodal enrichment pipeline;
- domain-specific ScenarioGraph schema and mappings;
- validation-catalog matching and coverage-gap logic;
- automotive-specific uncertainty and consistency policies;
- physical/kinematic validation rules authored for the challenge;
- OpenSCENARIO-compatible export adapter;
- challenge-specific benchmark fixtures, metrics, evaluation scripts and integration code;
- challenge-specific UI/demo artifacts and reports.

## Integration rule

Foreground code should depend on EvidenceBound Core through documented public APIs wherever practical rather than copying Core implementation into a challenge-specific package. This keeps the engineering boundary inspectable and reduces future licensing ambiguity.

## Competition term to review before Advance

The published AI-BOOST applicant rules state that the Challenge Owner has foreground exclusivity to use and implement the solution developed within its challenge free of charge for six months after the competition, after which further exploitation/licensing/IP-sharing arrangements require a separate agreement.

Before signing an Advance participation agreement:

1. verify that its definition of Background and Foreground is consistent with this boundary;
2. list EvidenceBound Core and the three pre-existing reference implementations as Background where the agreement provides a schedule for background assets;
3. do not describe the pre-existing EvidenceBound Core itself as a new Challenge 4 deliverable;
4. seek clarification before signing if the agreement would grant exclusivity over general-purpose EvidenceBound Core improvements unrelated to the Challenge 4 domain work.

This document is an engineering/IP scoping record, not legal advice.
