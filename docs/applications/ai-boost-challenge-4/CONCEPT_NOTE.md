# AI-BOOST Challenge 4 — SPARK Concept Note

**Challenge:** Generative AI for Automatic Test Case Generation from Crash Databases & Standards — Siemens Industry Software NV / RobustifAI  
**Project title:** EvidenceBound ScenarioGraph — Evidence-grounded crash-to-validation scenario generation  
**Applicant:** Ruslan Vrublevskyi  
**Legal status:** Individual  
**Application language:** English  
**Submission deadline:** 8 September 2026, 17:00 Brussels time  
**Submission platform:** F6S / AI Challenge Competition #2

> EvidenceBound Core is pre-existing background technology. Challenge 4 crash adapters, ScenarioGraph foreground pipeline, benchmark integration and automotive export work are challenge foreground. Measured SPARK results below are explicitly limited to 2 sanitized public NHTSA VICIS cases + 15 controlled mutations, including 8 explicit kinematic-gate expectation cases, and are not automotive production-accuracy, simulator-validation or homologation claims.

## Admin

1. **Full Name / Team Name / Organization Name:** Ruslan Vrublevskyi / EvidenceBound ScenarioGraph
2. **Email:** ruslan@evidencebound.org
3. **Phone:** TODO — enter current applicant phone in F6S
4. **Country of Residence / Registration:** Ukraine
5. **Legal Status:** Individual
6. **Consortium structure:** Single individual applicant at SPARK submission; collaboration with the Challenge Owner and AI-BOOST technical experts is planned during Advance.

## EXCELLENCE

### 1. Project Title

**EvidenceBound ScenarioGraph — Evidence-grounded crash-to-validation scenario generation**

### 2. Specific problem

Challenge 4: Generative AI for automatic test-case generation from crash databases and standards.

### 3. Problem Fit & Contribution — max 1,500 characters

EvidenceBound ScenarioGraph addresses the challenge’s core bottleneck: turning fragmented crash evidence and safety standards into structured scenarios without losing provenance or silently inventing missing facts. It extracts Functional Scenarios, enriches them into Logical Scenarios, normalizes them into typed state, and matches them to validation catalogues. Every material generated attribute is bound to source evidence, provenance and uncertainty. Unsupported or conflicting fields become REVIEW_REQUIRED or BLOCKED, not plausible-looking facts. A dependency graph records which downstream scenario and test-case nodes depend on each evidence item; when evidence changes, only the exact affected branch is invalidated and regenerated. This supports scalable scenario engineering while preserving traceability, explainability, reproducibility and human review.

### 4. Quantifiable Outcomes — max 1,500 characters

Measured SPARK baseline: a reproducible CI benchmark over 2 sanitized public NHTSA VICIS cases plus 15 controlled mutations, including 8 explicit kinematic-gate expectation cases. Controlled-suite results are 1000/1000 for evidence coverage, explicit uncertainty for unknown fields, Functional Scenario label accuracy, controlled-catalog Recall@1/MRR, receipt reproduction, exact changed-evidence detection, selective-recovery precision/recall, unrelated-field preservation, clean-case kinematic verification and expected kinematic decisions; unsupported assertion rate is 0/1000. Both generated .xosc artifacts pass the official ASAM OpenSCENARIO XML 1.4.0 XSD in CI. Retained receipt SHA-256: `90d21220e6cd1ca488fdb57e08b6cab0567821f5a6986ae246efbb56026f844a`. These are controlled-fixture results, not automotive production accuracy. Advance targets: broader Challenge Owner datasets, macro-F1 ≥0.80, Recall@5 ≥0.90, calibrated uncertainty, stronger physics/simulator validation and measured runtime/cost.

### 5. Innovation & Novelty — max 1,300 characters

Most GenAI scenario pipelines optimize extraction or generation quality and add citations afterward. ScenarioGraph makes evidence applicability part of execution. Each scenario claim is a typed node bound to source evidence, provenance, uncertainty and policy; downstream scenario/test-case nodes form an explicit dependency graph. If evidence becomes stale, missing or refuted, the system computes the exact blast radius and selectively regenerates only affected descendants. A deterministic gate prevents unsupported, inconsistent or non-reproducible outputs from being promoted merely because an LLM produced plausible text. The novelty is the combination of generative multimodal extraction with evidence-bound state, field-level uncertainty, dependency-aware invalidation, fail-closed verification and reproducible receipts—turning traceability from an audit artifact into a runtime property.

### 6. Technology Readiness — max 1,500 characters

EvidenceBound Core is pre-existing Apache-2.0 background technology with working deterministic verification, provenance-bound state, dependency blast-radius analysis and selective recovery. The Challenge 4 foreground is at TRL 3: the SPARK vertical slice ingests sanitized public NHTSA crash cases, creates evidence-bound Functional/Logical Scenario state, performs validation-catalog matching, detects exact evidence changes, computes preserve/recompute recovery sets, applies a versioned float-free kinematic coherence sanity gate, and exports ASAM OpenSCENARIO XML 1.4 documents validated in CI against the official 1.4.0 XSD. A strict recorded-GenAI candidate boundary proves invented evidence references are deterministically BLOCKED. The retained benchmark covers 2 public cases plus 15 controlled mutations, including 8 kinematic decision expectation cases. During Advance we will integrate Challenge Owner datasets, live schema-constrained LLM/VLM extraction, multimodal enrichment, broader matching benchmarks and stronger physics/simulator checks. Goal: TRL 5 validation in a relevant automotive-safety workflow, not homologation.

### 7. AI Technology & Justification — max 2,000 characters

The solution uses a hybrid generative + deterministic architecture. A provider-agnostic extraction contract accepts schema-constrained LLM/VLM candidates for Functional Scenario identification; the current SPARK acceptance baseline deliberately uses an inspectable deterministic extractor over coded public records so benchmark trust is not confused with probabilistic generation performance. During Advance, LLM/VLM/RAG components will extract and harmonize Functional Scenarios from heterogeneous text and multimodal evidence, then enrich Logical Scenario attributes and parameter ranges. A typed ScenarioGraph canonicalizes actors, context, parameters, relationships, uncertainty and source bindings. Hybrid matching combines semantic retrieval/embeddings with structured constraints to rank validation-catalog candidates and identify coverage gaps. EvidenceBound owns deterministic trust: provenance completeness, dependency invalidation, selective recovery, content-addressed receipts and a versioned integer-only kinematic coherence gate that maps controlled inconsistencies to VERIFIED, REVIEW_REQUIRED or BLOCKED. Outputs use ASAM OpenSCENARIO XML 1.4; the retained artifacts pass the official 1.4.0 XSD in CI. The current kinematic gate is a constant-speed sanity check, not a dynamics simulator. Model providers remain replaceable and prompts/models/configurations are versioned. GenAI handles ambiguity and abstraction; deterministic controls—not model confidence—decide trusted status.

### 8. Trustworthy, Responsible AI & Compliance — max 2,000 characters

Trustworthiness is enforced at runtime, not added as a report after generation. LLM/VLM components may propose scenario facts but cannot grant trusted status. Every material field carries source references, transformation provenance and uncertainty; missing or conflicting evidence remains explicit and triggers REVIEW_REQUIRED or BLOCKED rather than silent completion. Deterministic validators enforce provenance/dependency consistency and a versioned float-free kinematic coherence sanity check before simulation-oriented export. Controlled coherent data can remain VERIFIED; review-zone inconsistency becomes REVIEW_REQUIRED; strong inconsistency or non-positive required measurements becomes BLOCKED. Evidence changes invalidate only dependent state and trigger selective re-evaluation; reproducible receipts bind evidence, policy and outputs. Human review remains mandatory for ambiguous safety-relevant fields. At SPARK this is a TRL-3 engineering/research validation aid, not a deployed vehicle safety component, dynamics simulator, homologation result or compliance authority. Third-party models/APIs/cloud services will be disclosed, and PII/sensitive accident data will not be sent to external services.

### 9. Ethics & Data Governance — max 1,500 characters

The SPARK prototype applies data minimisation by retaining only scenario-relevant geometry, movement, environment, visibility and kinematic fields from public NHTSA cases; demographics, injury/medical, alcohol/drug and other sensitive person data are explicitly excluded in both fixtures and receipts. This is data-minimisation by design, aligned with the GDPR data-minimisation principle; it is not presented as blanket GDPR compliance. During Advance, data will be used only where public, licensed, organizer-provided or otherwise authorized. Dataset source, access/license context, transformations and integrity hashes will be recorded. Personal or sensitive accident data will not be transmitted to external AI services; where such data is required, processing will follow applicable controller instructions, lawful basis, safeguards and an approved local/private path. Missing demographic/contextual values will not be inferred without evidence. Bias and representativeness will be assessed across source datasets, regions and scenario classes. Outputs are engineering validation aids, not legal, certification or homologation decisions.

## IMPACT

### 1. Sustainability & Scalability AI — max 2,000 characters

ScenarioGraph is a modular foreground adapter around the framework-agnostic Apache-2.0 EvidenceBound Core. New accident schemas, countries, standards, model providers and validation catalogues can be added through adapters while preserving one typed evidence/trust contract. Canonical scenario state supports batch processing, caching, replay and selective re-evaluation: when one source changes, unaffected branches are preserved instead of regenerating the entire scenario graph. Models, prompts, policies and datasets are versioned and regression-tested. The evaluation path is container-ready and designed to run first on commodity/cloud infrastructure, with runtime, model calls and cost per 1,000 records measured during Advance. Public non-sensitive fixtures, schemas and evaluation code support reproducibility where licences permit. Provider substitution, human review and documented AI Act/GDPR assessment keep the design adaptable to regulatory and technical change.

### 2. Social & Environmental Impact — max 1,500 characters

The direct benefit is more scalable, traceable use of real crash evidence in automated-driving validation. Engineers can distinguish well-supported scenario elements from uncertain or unsupported inferences and identify validation gaps without treating synthetic plausibility as fact. This supports road-safety objectives while improving engineering productivity and lowering the barrier to evidence-grounded scenario analysis for smaller teams. Environmental claims will be measured rather than assumed: Advance will track model calls, runtime and cost, and selective re-evaluation is designed to avoid unnecessary repeated generation when only part of the evidence changes. The project does not claim that the SPARK prototype directly reduces crashes, emissions or certification effort. Its measurable contribution is better traceability, reproducibility, uncertainty handling and validation-coverage reasoning.

### 3. Fairness, Diversity & Open Science — max 1,500 characters

The benchmark plan will evaluate performance across heterogeneous countries, source types and scenario classes instead of reporting only aggregate accuracy. Missing demographic or contextual information remains unknown rather than being imputed as fact; protected or sensitive attributes are excluded unless technically necessary, ethically justified and permitted by data conditions. Scenario diversity and representativeness will be monitored to reduce overfitting to dominant crash patterns. The current applicant is one individual, so no claim is made about a diverse team composition. EvidenceBound Core remains Apache-2.0. Where dataset licences permit, non-sensitive fixtures, schemas, benchmark code, reproducibility instructions and evaluation receipts will be public. Restricted Challenge Owner data will not be republished.

### 4. Exploitation & Potential for Collaboration — max 2,000 characters

The immediate exploitation path is technical collaboration with Siemens Industry Software NV, RobustifAI and AI-BOOST experts to validate ScenarioGraph in a relevant automotive-safety workflow. After TRL 5, the architecture can support scenario-database curation, safety-case preparation, validation-coverage analysis and traceable GenAI workflows in mobility and other safety-critical domains. The pre-existing Apache-2.0 EvidenceBound Core remains reusable background IP, while Challenge 4-specific crash adapters, scenario mappings, benchmark integration, automotive policies and export tooling are isolated as foreground. This boundary supports the programme’s Challenge Owner rights without turning the general-purpose OSS runtime into newly developed foreground. Public benchmark artifacts and research outputs will be shared where data/IP terms allow.

## QUALITY OF IMPLEMENTATION

### 1. Work Plan (Advance) — max 3,000 characters

SPARK starting point: a green-CI TRL-3 vertical slice over two sanitized public NHTSA VICIS cases, with evidence-bound Functional/Logical Scenario state, deterministic catalog matching, exact evidence-change detection and selective recovery, a strict GenAI candidate trust boundary, a versioned float-free kinematic coherence gate, 15 controlled mutations including 8 kinematic decision expectation cases, a retained content-addressed benchmark receipt, and generated ASAM OpenSCENARIO XML 1.4 artifacts validated against the official 1.4.0 XSD in CI.

**Month 1 — Data & taxonomy:** integrate representative Challenge Owner/open datasets; implement versioned ingestion adapters, source-addressed evidence packs, common Functional Scenario taxonomy mapping and labelled evaluation subsets. Add live schema-constrained LLM/VLM extraction beside the deterministic baseline.

**Month 2 — Multimodal Logical Scenario enrichment:** link text/images/maps/context where available; extract parameter ranges with field-level uncertainty and conflict provenance; benchmark completeness/correctness and uncertainty calibration.

**Month 3 — Matching & coverage:** implement hybrid semantic + structured matching to validation catalogues, measure Recall@K/MRR and coverage-gap usefulness, and validate dependency-aware invalidation/selective recovery at larger scale.

**Month 4 — Simulation readiness:** extend the current kinematic sanity gate with stronger physical/traffic constraints, complete the common Structured Scenario Representation, enrich XSD-valid OpenSCENARIO exports with simulation-relevant entities/actions, and add simulator/visualization integration where practical.

**Month 5 — TRL-5 validation:** run heterogeneous holdout/adversarial suites, optimize runtime/cost, document failure modes, validate with Challenge Owner experts, freeze reproducible container/environment, final algorithm, benchmark report and live demo.

**Continuous:** CI/security, provider/model/prompt/data versioning, GDPR/Responsible-AI review, human-review workflow, documentation and leaderboard feedback.

### 2. Need CINECA?

**No for SPARK / initial architecture.** Re-evaluate during Advance if organizer-scale multimodal training or benchmarking justifies HPC.

### 3. Resources / Infrastructure — max 1,500 characters

No CINECA allocation is requested for SPARK/initial Advance planning. The current prototype runs in standard GitHub CI and requires no GPU. Existing resources include the public Python EvidenceBound Core, deterministic verification/recovery primitives, GitHub Actions CI/security/supply-chain gates, and experience deploying AI systems on AWS and Google Cloud. Advance will use Python, typed schemas, structured LLM/VLM outputs, semantic retrieval/embeddings, deterministic validators and containerized evaluation. Early inference/benchmarking can use approved commercial APIs or commodity cloud CPU/GPU under data-policy constraints; providers will be disclosed and sensitive/PII data will not leave approved processing boundaries. Storage will retain content-addressed public/authorized fixtures plus versioned model/prompt/config metadata. Runtime, model calls/tokens where available, and cost per 1,000 records will be measured.

### 4. Team Credentials & Expertise — max 1,750 words

Ruslan Vrublevskyi is the creator and maintainer of EvidenceBound Core, an Apache-2.0 framework-agnostic Python runtime for evidence/provenance-bound state, deterministic verification, dependency blast-radius analysis and fail-closed selective recovery. The public core includes architecture and threat-model documentation, deterministic canonicalization, persistence/replay and signing seams, interoperability/conformance work, CI across Python 3.10–3.13, security checks and supply-chain/release evidence.

Public reference implementations demonstrate the same trust primitives across different AI/cloud environments. EvidenceBound Recovery Mesh uses Google ADK, Gemini/Vertex AI and Cloud Run to demonstrate controlled trust-break propagation, exact downstream blast radius and selective recomputation. EvidenceBound DataHub Gate binds DataHub MCP metadata to governed actions, restricted execution and tamper-evident Proof Packs with a signing/verification path. EvidenceBound Verified Memory uses CockroachDB and AWS to persist canonical decision snapshots, reconstruct historical integrity and separately determine current applicability.

For AI-BOOST Challenge 4, the public draft branch/PR contains the SPARK ScenarioGraph vertical slice: sanitized official NHTSA VICIS crash cases, source-addressed evidence, typed Functional and Logical Scenario fields, explicit uncertainty, deterministic validation-catalog matching, exact evidence-change detection and selective recovery. A strict recorded-GenAI boundary demonstrates that invented evidence references are blocked by the deterministic trust gate. The retained benchmark covers 2 public cases plus 15 controlled mutations, including 8 explicit kinematic-gate expectation cases. A versioned float-free kinematic coherence sanity gate exercises VERIFIED, REVIEW_REQUIRED and BLOCKED outcomes, and generated ASAM OpenSCENARIO XML 1.4 artifacts pass the official 1.4.0 XSD in dedicated CI. The normal repository CI covers Python 3.10–3.13, pytest, Ruff, Mypy, security and build checks.

Technical experience spans Python, TypeScript, Next.js, FastAPI, PostgreSQL/CockroachDB, AWS, Google Cloud, Docker, GitHub Actions, OIDC/WIF, MCP and agent orchestration. The main capability gap is automotive validation-domain expertise rather than core AI/platform engineering. The Advance plan therefore relies on Siemens Industry Software NV, RobustifAI and AI-BOOST guidance for taxonomy semantics, benchmark data, stronger traffic/physics constraints and industrial validation relevance rather than claiming pre-existing homologation or automotive-safety authority.

### 5. Risk Management & Mitigation — max 1,500 characters

Domain-semantic risk: generated fields may be plausible but wrong; mitigate with source-level evidence binding, labelled evaluation, uncertainty and Challenge Owner review. Sparse/conflicting evidence: preserve UNKNOWN/conflict state and require REVIEW_REQUIRED/BLOCKED rather than silent completion. GenAI drift/vendor dependence: version models/prompts, keep provider abstraction and deterministic regression fixtures. Physical inconsistency: the current versioned kinematic sanity gate blocks/reviews controlled incoherence; extend it during Advance with stronger traffic/physics and simulator checks. Matching generalization: evaluate heterogeneous holdouts and report Recall@K/MRR plus error analysis, not only the small SPARK fixture score. Dataset/licensing/PII risk: use approved/public data, minimize retained fields and prohibit external transmission of sensitive data. Scale/cost risk: batch, cache and selectively re-evaluate affected branches; measure cost/runtime. Automotive-domain gap: use Siemens/RobustifAI guidance rather than claiming existing domain authority. IP risk: keep EvidenceBound Core/reference systems documented as background and isolate Challenge 4 foreground.

## Public evidence

- Project site: https://evidencebound.org
- Core repository: https://github.com/moneyparking/evidencebound-core
- SPARK draft PR: https://github.com/moneyparking/evidencebound-core/pull/26
- Judge-facing evidence index: `docs/applications/ai-boost-challenge-4/SPARK_EVIDENCE.md`
- Retained benchmark: `benchmarks/ai_boost_challenge4/BASELINE.json`
- Reproduction guide: `benchmarks/ai_boost_challenge4/README.md`

## Before F6S submission

- [ ] Confirm applicant phone number.
- [ ] Confirm exact F6S profile name/email.
- [ ] Re-check online F6S wording against Annex 1; online form prevails if different.
- [x] Public crash fixtures retained and source-addressed.
- [x] Measured SPARK baseline retained with deterministic SHA-256 receipt.
- [x] Fifteen controlled mutations included, with eight explicit kinematic-gate expectation cases.
- [x] GenAI invented-evidence reference fail-closed test included.
- [x] Deterministic kinematic coherence gate exercises VERIFIED / REVIEW_REQUIRED / BLOCKED.
- [x] OpenSCENARIO XML 1.4.0 artifacts validated against official ASAM XSD in CI.
- [ ] Review IP/background/foreground statement against participation agreement if selected.
- [ ] Submit once, deliberately, because only the last proposal per applicant is evaluated.