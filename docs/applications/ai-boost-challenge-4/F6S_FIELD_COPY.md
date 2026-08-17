# AI-BOOST Challenge 4 — Final F6S Field Copy

**Application:** AI Challenge Competition #2 — SPARK Phase  
**Challenge:** Challenge 4 — Generative AI for automatic test case generation from crash databases and standards  
**Project:** EvidenceBound ScenarioGraph — Evidence-grounded crash-to-validation scenario generation  
**Applicant:** Ruslan Vrublevskyi  
**Status:** submission-ready working copy; re-check the live F6S form immediately before final submission because the online form prevails if wording/limits differ.

## ADMIN

### 1. Full Name / Team Name / Organization Name
Ruslan Vrublevskyi / EvidenceBound ScenarioGraph

### 2. Email Address
ruslan@evidencebound.org

### 3. Phone Number
**MANUAL REQUIRED:** enter the applicant's current phone number in F6S.

### 4. Country of Residence / Registration
Ukraine

### 5. Legal Status
Individual

### 6. Consortium structure
Not applicable. Single individual applicant. Collaboration with the Challenge Owner and AI-BOOST technical experts is planned during Advance.

## EXCELLENCE

### 1. Project Title
EvidenceBound ScenarioGraph — Evidence-grounded crash-to-validation scenario generation

### 2. Specific problem
Challenge 4 — Generative AI for automatic test case generation from crash databases and standards.

### Problem Fit & Contribution

**Characters:** 867 / 1500

EvidenceBound ScenarioGraph addresses the challenge’s core bottleneck: turning fragmented crash evidence and safety standards into structured scenarios without losing provenance or silently inventing missing facts. It extracts Functional Scenarios, enriches them into Logical Scenarios, normalizes them into typed state, and matches them to validation catalogues. Every material generated attribute is bound to source evidence, provenance and uncertainty. Unsupported or conflicting fields become REVIEW_REQUIRED or BLOCKED, not plausible-looking facts. A dependency graph records which downstream scenario and test-case nodes depend on each evidence item; when evidence changes, only the exact affected branch is invalidated and regenerated. This supports scalable scenario engineering while preserving traceability, explainability, reproducibility and human review.

### Quantifiable Outcomes

**Characters:** 1006 / 1500

Measured SPARK baseline: a reproducible CI benchmark over 2 sanitized public NHTSA VICIS cases plus 15 controlled mutations, including 8 explicit kinematic-gate expectation cases. Controlled-suite results are 1000/1000 for evidence coverage, explicit uncertainty for unknown fields, Functional Scenario label accuracy, controlled-catalog Recall@1/MRR, receipt reproduction, exact changed-evidence detection, selective-recovery precision/recall, unrelated-field preservation, clean-case kinematic verification and expected kinematic decisions; unsupported assertion rate is 0/1000. Both generated .xosc artifacts pass the official ASAM OpenSCENARIO XML 1.4.0 XSD in CI. Retained receipt SHA-256: 90d21220e6cd1ca488fdb57e08b6cab0567821f5a6986ae246efbb56026f844a. These are controlled-fixture results, not automotive production accuracy. Advance targets: broader Challenge Owner datasets, macro-F1 ≥0.80, Recall@5 ≥0.90, calibrated uncertainty, stronger physics/simulator validation and measured runtime/cost.

### Innovation & Novelty

**Characters:** 897 / 1300

Most GenAI scenario pipelines optimize extraction or generation quality and add citations afterward. ScenarioGraph makes evidence applicability part of execution. Each scenario claim is a typed node bound to source evidence, provenance, uncertainty and policy; downstream scenario/test-case nodes form an explicit dependency graph. If evidence becomes stale, missing or refuted, the system computes the exact blast radius and selectively regenerates only affected descendants. A deterministic gate prevents unsupported, inconsistent or non-reproducible outputs from being promoted merely because an LLM produced plausible text. The novelty is the combination of generative multimodal extraction with evidence-bound state, field-level uncertainty, dependency-aware invalidation, fail-closed verification and reproducible receipts—turning traceability from an audit artifact into a runtime property.

### Technology Readiness

**Characters:** 1140 / 1500

EvidenceBound Core is pre-existing Apache-2.0 background technology with working deterministic verification, provenance-bound state, dependency blast-radius analysis and selective recovery. The Challenge 4 foreground is at TRL 3: the SPARK vertical slice ingests sanitized public NHTSA crash cases, creates evidence-bound Functional/Logical Scenario state, performs validation-catalog matching, detects exact evidence changes, computes preserve/recompute recovery sets, applies a versioned float-free kinematic coherence sanity gate, and exports ASAM OpenSCENARIO XML 1.4 documents validated in CI against the official 1.4.0 XSD. A strict recorded-GenAI candidate boundary proves invented evidence references are deterministically BLOCKED. The retained benchmark covers 2 public cases plus 15 controlled mutations, including 8 kinematic decision expectation cases. During Advance we will integrate Challenge Owner datasets, live schema-constrained LLM/VLM extraction, multimodal enrichment, broader matching benchmarks and stronger physics/simulator checks. Goal: TRL 5 validation in a relevant automotive-safety workflow, not homologation.

### AI Technology & Justification

**Characters:** 1497 / 2000

The solution uses a hybrid generative + deterministic architecture. A provider-agnostic extraction contract accepts schema-constrained LLM/VLM candidates for Functional Scenario identification; the current SPARK acceptance baseline deliberately uses an inspectable deterministic extractor over coded public records so benchmark trust is not confused with probabilistic generation performance. During Advance, LLM/VLM/RAG components will extract and harmonize Functional Scenarios from heterogeneous text and multimodal evidence, then enrich Logical Scenario attributes and parameter ranges. A typed ScenarioGraph canonicalizes actors, context, parameters, relationships, uncertainty and source bindings. Hybrid matching combines semantic retrieval/embeddings with structured constraints to rank validation-catalog candidates and identify coverage gaps. EvidenceBound owns deterministic trust: provenance completeness, dependency invalidation, selective recovery, content-addressed receipts and a versioned integer-only kinematic coherence gate that maps controlled inconsistencies to VERIFIED, REVIEW_REQUIRED or BLOCKED. Outputs use ASAM OpenSCENARIO XML 1.4; the retained artifacts pass the official 1.4.0 XSD in CI. The current kinematic gate is a constant-speed sanity check, not a dynamics simulator. Model providers remain replaceable and prompts/models/configurations are versioned. GenAI handles ambiguity and abstraction; deterministic controls—not model confidence—decide trusted status.

### Trustworthy, Responsible AI & Compliance

**Characters:** 1213 / 2000

Trustworthiness is enforced at runtime, not added as a report after generation. LLM/VLM components may propose scenario facts but cannot grant trusted status. Every material field carries source references, transformation provenance and uncertainty; missing or conflicting evidence remains explicit and triggers REVIEW_REQUIRED or BLOCKED rather than silent completion. Deterministic validators enforce provenance/dependency consistency and a versioned float-free kinematic coherence sanity check before simulation-oriented export. Controlled coherent data can remain VERIFIED; review-zone inconsistency becomes REVIEW_REQUIRED; strong inconsistency or non-positive required measurements becomes BLOCKED. Evidence changes invalidate only dependent state and trigger selective re-evaluation; reproducible receipts bind evidence, policy and outputs. Human review remains mandatory for ambiguous safety-relevant fields. At SPARK this is a TRL-3 engineering/research validation aid, not a deployed vehicle safety component, dynamics simulator, homologation result or compliance authority. Third-party models/APIs/cloud services will be disclosed, and PII/sensitive accident data will not be sent to external services.

### Ethics & Data Governance

**Characters:** 1142 / 1500

The SPARK prototype applies data minimisation by retaining only scenario-relevant geometry, movement, environment, visibility and kinematic fields from public NHTSA cases; demographics, injury/medical, alcohol/drug and other sensitive person data are explicitly excluded in both fixtures and receipts. This is data-minimisation by design, aligned with the GDPR data-minimisation principle; it is not presented as blanket GDPR compliance. During Advance, data will be used only where public, licensed, organizer-provided or otherwise authorized. Dataset source, access/license context, transformations and integrity hashes will be recorded. Personal or sensitive accident data will not be transmitted to external AI services; where such data is required, processing will follow applicable controller instructions, lawful basis, safeguards and an approved local/private path. Missing demographic/contextual values will not be inferred without evidence. Bias and representativeness will be assessed across source datasets, regions and scenario classes. Outputs are engineering validation aids, not legal, certification or homologation decisions.

## IMPACT

### Sustainability & Scalability AI

**Characters:** 1226 / 2000

ScenarioGraph is a modular foreground adapter around the framework-agnostic Apache-2.0 EvidenceBound Core. New accident schemas, countries, standards, model providers and validation catalogues can be added through adapters while preserving one typed evidence/trust contract. Canonical scenario state supports batch processing, caching, replay and selective re-evaluation: when one source changes, unaffected branches are preserved instead of regenerating the entire scenario graph. Models, prompts, policies and datasets are versioned and regression-tested; retraining or model replacement will occur only when benchmark evidence justifies it. The evaluation path is container-ready and designed to run first on commodity/cloud infrastructure, with runtime, model calls and cost per 1,000 records measured during Advance. Public non-sensitive fixtures, schemas and evaluation code will support reproducibility and community review where licences permit. Data minimization, provider substitution, human review and documented AI Act/GDPR assessment keep the design adaptable to regulatory and technical change. After TRL 5, the same trust layer can be reused for mobility and other safety-critical scenario-generation workflows.

### Social & Environmental Impact

**Characters:** 1056 / 1500

The direct benefit is more scalable, traceable use of real crash evidence in automated-driving validation. Engineers can distinguish well-supported scenario elements from uncertain or unsupported inferences and identify validation gaps without treating synthetic plausibility as fact. This supports road-safety objectives such as SDG 3.6 and safer, more accessible transport under SDG 11.2, while improving engineering productivity and lowering the barrier to evidence-grounded scenario analysis for smaller teams. Environmental claims will be measured rather than assumed: Advance will track model calls, runtime and cost, and selective re-evaluation is designed to avoid unnecessary repeated generation when only part of the evidence changes. The project does not claim that the SPARK prototype directly reduces crashes, emissions or certification effort. Its measurable contribution is better traceability, reproducibility, uncertainty handling and validation-coverage reasoning, with computational-efficiency metrics reported alongside quality metrics.

### Fairness, Diversity & Open Science

**Characters:** 1090 / 1500

The benchmark plan will evaluate performance across heterogeneous countries, source types and scenario classes instead of reporting only aggregate accuracy. Missing demographic or contextual information remains unknown rather than being imputed as fact; protected or sensitive attributes are excluded unless technically necessary, ethically justified and permitted by the data conditions. Scenario diversity and representativeness will be monitored to reduce overfitting to dominant crash patterns. The current applicant is one individual, so no claim is made about a diverse team composition; diversity is addressed through data coverage, stakeholder review and openness to domain contributors during Advance. EvidenceBound Core remains Apache-2.0. Where dataset licences permit, non-sensitive fixtures, schemas, benchmark code, reproducibility instructions and evaluation receipts will be publicly available. Restricted Challenge Owner data will not be republished; transparent methods and synthetic/public regression fixtures will preserve reproducibility without violating access terms.

### Exploitation & Potential for Collaboration

**Characters:** 1213 / 2000

The immediate exploitation path is technical collaboration with Siemens Industry Software NV, RobustifAI and AI-BOOST experts to validate ScenarioGraph in a relevant automotive-safety workflow. After TRL 5, the architecture can support scenario-database curation, safety-case preparation, validation-coverage analysis and traceable GenAI workflows in mobility and other safety-critical domains. Adoption is structured around open interfaces: the pre-existing Apache-2.0 EvidenceBound Core remains reusable background IP, while Challenge 4-specific crash adapters, scenario mappings, benchmark integration, automotive policies and export tooling are isolated as foreground. This boundary supports the programme’s Challenge Owner rights without turning the general-purpose OSS runtime into newly developed foreground. The provider-neutral architecture supports commercial or open model backends and multiple validation catalogues. After the programme’s six-month Challenge Owner exclusivity period for challenge-developed solutions, any further licensing, integration or commercial collaboration can be negotiated separately. Public benchmark artifacts and research outputs will be shared where data/IP terms allow.

## QUALITY OF IMPLEMENTATION

### Work Plan (Advance Phase)

**Characters:** 2076 / 3000

SPARK starting point: a green-CI TRL-3 vertical slice over two sanitized public NHTSA VICIS cases, with evidence-bound Functional/Logical Scenario state, deterministic catalog matching, exact evidence-change detection and selective recovery, a strict GenAI candidate trust boundary, a versioned float-free kinematic coherence gate, 15 controlled mutations including 8 kinematic decision expectation cases, a retained content-addressed benchmark receipt, and generated ASAM OpenSCENARIO XML 1.4 artifacts validated against the official 1.4.0 XSD in CI.

Month 1 — Data & taxonomy: integrate representative Challenge Owner/open datasets; implement versioned ingestion adapters, source-addressed evidence packs, common Functional Scenario taxonomy mapping and labelled evaluation subsets. Add live schema-constrained LLM/VLM extraction beside the deterministic baseline.

Month 2 — Multimodal Logical Scenario enrichment: link text/images/maps/context where available; extract parameter ranges with field-level uncertainty and conflict provenance; benchmark completeness/correctness and uncertainty calibration.

Month 3 — Matching & coverage: implement hybrid semantic + structured matching to validation catalogues, measure Recall@K/MRR and coverage-gap usefulness, and validate dependency-aware invalidation/selective recovery at larger scale.

Month 4 — Simulation readiness: extend the current kinematic sanity gate with stronger physical/traffic constraints, complete the common Structured Scenario Representation, enrich XSD-valid OpenSCENARIO exports with simulation-relevant entities/actions, and add simulator/visualization integration where practical.

Month 5 — TRL-5 validation: run heterogeneous holdout/adversarial suites, optimize runtime/cost, document failure modes, validate with Challenge Owner experts, freeze reproducible container/environment, final algorithm, benchmark report and live demo.

Continuous: CI/security, provider/model/prompt/data versioning, GDPR/Responsible-AI review, human-review workflow, documentation and monthly leaderboard feedback.

### Do you need access to CINECA Infrastructure?

No.

### Resources / Infrastructure

**Characters:** 1075 / 1500

No CINECA allocation is requested for SPARK/initial Advance planning. The current prototype runs in standard GitHub CI and requires no GPU. Existing resources include the public Python EvidenceBound Core, deterministic verification/recovery primitives, GitHub Actions CI/security/supply-chain gates, and experience deploying AI systems on AWS and Google Cloud. Advance will use Python, typed schemas, structured LLM/VLM outputs, semantic retrieval/embeddings, deterministic validators and containerized evaluation. Early inference/benchmarking can use approved commercial APIs or commodity cloud CPU/GPU under data-policy constraints; providers will be disclosed and sensitive/PII data will not leave approved processing boundaries. Storage will retain content-addressed public/authorized fixtures plus versioned model/prompt/config metadata. Runtime, model calls/tokens where available, and cost per 1,000 records will be measured. CINECA can be reconsidered with AI-BOOST if Challenge Owner-scale multimodal training or benchmarking later demonstrates a justified HPC need.

### Team Credentials & Expertise

**Words:** 338 / 1750

Ruslan Vrublevskyi is the creator and maintainer of EvidenceBound Core, an Apache-2.0 framework-agnostic Python runtime for evidence/provenance-bound state, deterministic verification, dependency blast-radius analysis and fail-closed selective recovery. The public core includes architecture and threat-model documentation, deterministic canonicalization, persistence/replay and signing seams, interoperability/conformance work, CI across Python 3.10–3.13, security checks and supply-chain/release evidence.

Public reference implementations demonstrate the same trust primitives across different AI/cloud environments. EvidenceBound Recovery Mesh uses Google ADK, Gemini/Vertex AI and Cloud Run to demonstrate controlled trust-break propagation, exact downstream blast radius and selective recomputation. EvidenceBound DataHub Gate binds DataHub MCP metadata to governed actions, restricted execution and tamper-evident Proof Packs with a signing/verification path. EvidenceBound Verified Memory uses CockroachDB and AWS to persist canonical decision snapshots, reconstruct historical integrity and separately determine current applicability.

For AI-BOOST Challenge 4, a foreground workstream is implemented in a public draft branch/PR. The SPARK ScenarioGraph vertical slice uses sanitized official NHTSA VICIS crash cases, source-addressed evidence, typed Functional and Logical Scenario fields, explicit uncertainty, deterministic validation-catalog matching, exact evidence-change detection and selective recovery. A strict recorded-GenAI boundary demonstrates that invented evidence references are blocked by the deterministic trust gate. The retained benchmark covers 2 public cases plus 15 controlled mutations, including 8 explicit kinematic-gate expectation cases. A versioned float-free kinematic coherence sanity gate exercises VERIFIED, REVIEW_REQUIRED and BLOCKED outcomes, and generated ASAM OpenSCENARIO XML 1.4 artifacts pass the official 1.4.0 XSD in dedicated CI. Full repository CI covers Python 3.10–3.13, pytest, Ruff, Mypy, security and build checks.

Technical experience spans Python, TypeScript, Next.js, FastAPI, PostgreSQL/CockroachDB, AWS, Google Cloud, Docker, GitHub Actions, OIDC/WIF, MCP and agent orchestration. The project approach emphasizes narrow claims, reproducible acceptance, fail-closed execution and explicit separation between model-generated candidates and deterministic trust decisions.

The main capability gap is automotive validation-domain expertise, not core AI/platform engineering. The Advance plan therefore explicitly relies on Siemens Industry Software NV, RobustifAI and AI-BOOST technical guidance for taxonomy semantics, benchmark data, stronger traffic/physics constraints and industrial validation relevance rather than claiming pre-existing homologation or automotive-safety authority.

Public evidence:
https://evidencebound.org
https://github.com/moneyparking/evidencebound-core
https://github.com/moneyparking/evidencebound-core/pull/26

### Risk Management & Mitigation

**Characters:** 1193 / 1500

Domain-semantic risk: generated fields may be plausible but wrong; mitigate with source-level evidence binding, labelled evaluation, uncertainty and Challenge Owner review. Sparse/conflicting evidence: preserve UNKNOWN/conflict state and require REVIEW_REQUIRED/BLOCKED rather than silent completion. GenAI drift/vendor dependence: version models/prompts, keep provider abstraction and deterministic regression fixtures. Physical inconsistency: the current versioned kinematic sanity gate blocks/reviews controlled incoherence; extend it during Advance with stronger traffic/physics and simulator checks. Matching generalization: evaluate heterogeneous holdouts and report Recall@K/MRR plus error analysis, not only the small SPARK fixture score. Dataset/licensing/PII risk: use approved/public data, minimize retained fields and prohibit external transmission of sensitive data. Scale/cost risk: batch, cache and selectively re-evaluate affected branches; measure cost/runtime. Automotive-domain gap: use Siemens/RobustifAI guidance rather than claiming existing domain authority. IP risk: keep EvidenceBound Core/reference systems documented as background and isolate Challenge 4 foreground.

## DECLARATION

These are checkboxes in F6S. Read them in the live form and tick only if true at submission time:

- Organization/applicant is not subject to exclusion grounds under EU Financial Regulation 2018/1046.
- Acknowledge possible audits/controls by the European Commission, ECA, EPPO and OLAF.
- If selected as a prize-winner, agree to sign the official Declaration of Honour.

## OPTIONAL PUBLIC EVIDENCE LINKS

Use these if the live F6S form provides project/demo/repository/supporting-link fields:

- Institutional project site: https://evidencebound.org
- EvidenceBound Core: https://github.com/moneyparking/evidencebound-core
- AI-BOOST SPARK workstream / draft PR: https://github.com/moneyparking/evidencebound-core/pull/26
- Judge-facing SPARK evidence index: https://github.com/moneyparking/evidencebound-core/blob/ai-boost-challenge-4/docs/applications/ai-boost-challenge-4/SPARK_EVIDENCE.md
- Retained benchmark baseline: https://github.com/moneyparking/evidencebound-core/blob/ai-boost-challenge-4/benchmarks/ai_boost_challenge4/BASELINE.json
- Reproduction instructions: https://github.com/moneyparking/evidencebound-core/blob/ai-boost-challenge-4/benchmarks/ai_boost_challenge4/README.md

## SUBMISSION SAFETY NOTES

- The measured perfect controlled-suite values are explicitly scoped to **2 sanitized public NHTSA VICIS cases + 15 controlled mutations**, including **8 explicit kinematic-gate expectation cases**. Never restate them as general automotive accuracy.
- Current Functional Scenario benchmark extraction is a deterministic coded-record baseline. The architecture also contains a strict provider seam for schema-constrained LLM/VLM extraction; actual live GenAI benchmark performance is not yet claimed.
- The current kinematic coherence gate is a versioned integer-only constant-speed sanity check. It is not a vehicle-dynamics simulator, safety case, homologation criterion or simulator-behavior validation.
- Generated ASAM OpenSCENARIO XML 1.4 artifacts pass the official **1.4.0 XSD** in dedicated CI. This is XML schema acceptance, not simulator-behavior validation, production-safety evidence, homologation or certification.
- Data minimisation is implemented and explicitly recorded; do not turn this into a blanket claim that the full system is “GDPR compliant”.
- EvidenceBound Core and pre-existing reference implementations are Background IP. Challenge 4 domain adapters, benchmark integration and scenario pipeline are proposed Foreground.
- Submit one deliberate proposal only. If multiple proposals are submitted, the competition rules state only the last timestamped proposal is evaluated.