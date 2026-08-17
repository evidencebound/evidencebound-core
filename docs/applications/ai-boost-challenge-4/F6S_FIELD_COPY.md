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

**Characters:** 953 / 1500

Measured SPARK baseline: a reproducible CI benchmark over 2 sanitized public NHTSA VICIS cases plus 2 controlled adversarial mutations produced 100% evidence coverage for asserted material fields, 0% unsupported assertions, 100% explicit uncertainty for unknown fields, 100% Functional Scenario label accuracy, Recall@1=100% and MRR=1.0 on the small controlled validation catalogue, 100% receipt reproduction, and 100% precision/recall for the controlled dependency-invalidation test. Receipt SHA-256: f751a951ba5d1c97a46528e378ec9a9089e8b5581cfea5a81b38578826f18ed0. These are fixture-level results, not automotive production accuracy. Advance targets: ≥95% evidence coverage, <2% unsupported assertions, macro-F1 ≥0.80 for scenario taxonomy, ≥0.80 logical-attribute completeness/correctness, Recall@5 ≥0.90, calibrated uncertainty, reproducible containerized evaluation, and measured runtime/cost per 1,000 records on broader Challenge Owner datasets.

### Innovation & Novelty

**Characters:** 897 / 1300

Most GenAI scenario pipelines optimize extraction or generation quality and add citations afterward. ScenarioGraph makes evidence applicability part of execution. Each scenario claim is a typed node bound to source evidence, provenance, uncertainty and policy; downstream scenario/test-case nodes form an explicit dependency graph. If evidence becomes stale, missing or refuted, the system computes the exact blast radius and selectively regenerates only affected descendants. A deterministic gate prevents unsupported, inconsistent or non-reproducible outputs from being promoted merely because an LLM produced plausible text. The novelty is the combination of generative multimodal extraction with evidence-bound state, field-level uncertainty, dependency-aware invalidation, fail-closed verification and reproducible receipts—turning traceability from an audit artifact into a runtime property.

### Technology Readiness

**Characters:** 967 / 1500

EvidenceBound Core is pre-existing Apache-2.0 background technology with working deterministic verification, provenance-bound state, dependency blast-radius analysis and selective recovery. Public reference implementations demonstrate these primitives in multi-agent recovery, governed data actions and verified memory. The Challenge 4 foreground is now at TRL 3: the SPARK vertical slice ingests sanitized public NHTSA crash cases, creates evidence-bound Functional/Logical Scenario state, performs validation-catalog matching, exposes an ASAM OpenSCENARIO XML 1.4 structural export seam, handles missing evidence fail-closed, and retains a reproducible benchmark receipt. During Advance we will integrate Challenge Owner datasets, schema-constrained LLM/VLM extraction, multimodal enrichment, broader matching benchmarks, uncertainty/physics constraints and XSD validation. Goal: TRL 5 prototype validated in a relevant automotive-safety workflow, not homologation.

### AI Technology & Justification

**Characters:** 1458 / 2000

The solution uses a hybrid generative + deterministic architecture. A provider-agnostic extraction contract accepts schema-constrained LLM/VLM candidates for Functional Scenario identification; the current SPARK acceptance baseline deliberately uses an inspectable deterministic extractor over coded public records so benchmark trust is not confused with probabilistic generation performance. During Advance, LLM/VLM/RAG components will extract and harmonize Functional Scenarios from heterogeneous text and multimodal evidence, then enrich Logical Scenario attributes and parameter ranges. A typed ScenarioGraph canonicalizes actors, context, parameters, relationships, uncertainty and source bindings. Hybrid scenario matching combines semantic retrieval/embeddings with structured constraints to rank validation-catalog candidates and identify coverage gaps. EvidenceBound Core owns the deterministic trust layer: provenance completeness, schema checks, applicability, dependency-graph invalidation, selective recovery and content-addressed receipts. Basic physical/kinematic constraints will gate simulation-oriented exports. Outputs use a common structured representation with an ASAM OpenSCENARIO XML 1.4 export path. Model providers remain replaceable; prompts/models/configurations are versioned. GenAI handles ambiguity and abstraction, while deterministic controls—not model confidence—decide whether output is VERIFIED, REVIEW_REQUIRED or BLOCKED.

### Trustworthy, Responsible AI & Compliance

**Characters:** 1276 / 2000

Trustworthiness is enforced at runtime, not added as a report after generation. LLM/VLM components may propose scenario facts but cannot grant trusted status. Every material field carries source references, transformation provenance, uncertainty, and versioned model/prompt/policy metadata. Missing or conflicting evidence remains explicit and triggers REVIEW_REQUIRED or BLOCKED rather than silent completion. Deterministic validators enforce schema, provenance completeness, dependency consistency and basic physical/kinematic constraints before simulation-oriented export. If evidence changes, the graph invalidates only dependent state and selectively re-evaluates that branch; reproducible receipts bind normalized evidence, policy and outputs. Human review remains mandatory for ambiguous safety-relevant fields. At SPARK this is an engineering/research validation aid, not a deployed vehicle safety component or compliance authority. Before any higher-risk deployment, the intended role and EU AI Act classification will be reassessed with the Challenge Owner. The design supports transparency, traceability, robustness and human oversight. Third-party models/APIs/cloud services will be disclosed, and PII/sensitive accident data will not be sent to external services.

### Ethics & Data Governance

**Characters:** 1029 / 1500

The SPARK prototype applies data minimization by retaining only scenario-relevant geometry, movement, environment, visibility and kinematic fields from public NHTSA cases; demographics, injury/medical, alcohol/drug and other sensitive person data are excluded. During Advance, data will be used only where public, licensed, organizer-provided or otherwise authorized. Dataset source, access/license context, transformations and integrity hashes will be recorded. Personal or sensitive accident data will not be transmitted to external AI services; where such data is required, processing will follow the applicable controller instructions, lawful basis, GDPR safeguards and an approved local/private path. Missing demographic/contextual values will not be inferred without evidence. Bias and representativeness will be assessed across source datasets, regions and scenario classes. External models/APIs/cloud services will be disclosed. Outputs are engineering validation aids, not legal, certification or homologation decisions.

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

**Characters:** 1816 / 3000

SPARK starting point: a green-CI TRL-3 vertical slice over two sanitized public NHTSA VICIS cases, with evidence-bound Functional/Logical Scenario state, deterministic catalog matching, exact dependency invalidation/recovery, an OpenSCENARIO XML 1.4 structural export seam, two adversarial missing/change-evidence tests and a retained benchmark receipt.

Month 1 — Data & taxonomy: integrate representative Challenge Owner/open datasets; implement versioned ingestion adapters, source-addressed evidence packs, common Functional Scenario taxonomy mapping and labelled evaluation subsets. Add schema-constrained LLM extraction beside the deterministic baseline.

Month 2 — Multimodal Logical Scenario enrichment: link text/images/maps/context where available; extract parameter ranges with field-level uncertainty and conflict provenance; benchmark completeness/correctness and uncertainty calibration.

Month 3 — Matching & coverage: implement hybrid semantic + structured matching to validation catalogues, measure Recall@K/MRR and coverage-gap usefulness, and validate dependency-aware invalidation/selective recovery at larger scale.

Month 4 — Simulation readiness: add stronger physical/kinematic consistency gates, complete common Structured Scenario Representation, validate ASAM OpenSCENARIO export against the applicable schema, and add visualization/simulation integration where practical.

Month 5 — TRL-5 validation: run heterogeneous holdout/adversarial suites, optimize runtime/cost, document failure modes, validate with Challenge Owner experts, freeze reproducible container/environment, final algorithm, benchmark report and live demo.

Continuous: CI/security, provider/model/prompt/data versioning, GDPR/Responsible-AI review, human-review workflow, documentation and monthly leaderboard feedback.

### Do you need access to CINECA Infrastructure?

No.

### Resources / Infrastructure

**Characters:** 1075 / 1500

No CINECA allocation is requested for SPARK/initial Advance planning. The current prototype runs in standard GitHub CI and requires no GPU. Existing resources include the public Python EvidenceBound Core, deterministic verification/recovery primitives, GitHub Actions CI/security/supply-chain gates, and experience deploying AI systems on AWS and Google Cloud. Advance will use Python, typed schemas, structured LLM/VLM outputs, semantic retrieval/embeddings, deterministic validators and containerized evaluation. Early inference/benchmarking can use approved commercial APIs or commodity cloud CPU/GPU under data-policy constraints; providers will be disclosed and sensitive/PII data will not leave approved processing boundaries. Storage will retain content-addressed public/authorized fixtures plus versioned model/prompt/config metadata. Runtime, model calls/tokens where available, and cost per 1,000 records will be measured. CINECA can be reconsidered with AI-BOOST if Challenge Owner-scale multimodal training or benchmarking later demonstrates a justified HPC need.

### Team Credentials & Expertise

**Words:** 299 / 1750

Ruslan Vrublevskyi is the creator and maintainer of EvidenceBound Core, an Apache-2.0 framework-agnostic Python runtime for evidence/provenance-bound state, deterministic verification, dependency blast-radius analysis and fail-closed selective recovery. The public core includes architecture and threat-model documentation, deterministic canonicalization, persistence/replay and signing seams, interoperability/conformance work, CI across Python 3.10–3.13, security checks and supply-chain/release evidence.

Public reference implementations demonstrate the same trust primitives across different AI/cloud environments. EvidenceBound Recovery Mesh uses Google ADK, Gemini/Vertex AI and Cloud Run to demonstrate controlled trust-break propagation, exact downstream blast radius and selective recomputation. EvidenceBound DataHub Gate binds DataHub MCP metadata to governed actions, restricted execution and tamper-evident Proof Packs with a signing/verification path. EvidenceBound Verified Memory uses CockroachDB and AWS to persist canonical decision snapshots, reconstruct historical integrity and separately determine current applicability.

For AI-BOOST Challenge 4, a new foreground workstream is already implemented in a public draft branch/PR. The SPARK ScenarioGraph vertical slice uses sanitized official NHTSA VICIS crash cases, source-addressed evidence, typed Functional and Logical Scenario fields, explicit uncertainty, deterministic validation-catalog matching, exact dependency invalidation/selective recovery and an ASAM OpenSCENARIO XML 1.4 structural export seam. A dedicated GitHub Actions benchmark reproduces the retained baseline receipt; the normal repository CI is green across Python 3.10–3.13, including pytest, Ruff, Mypy, security and build checks.

Technical experience spans Python, TypeScript, Next.js, FastAPI, PostgreSQL/CockroachDB, AWS, Google Cloud, Docker, GitHub Actions, OIDC/WIF, MCP and agent orchestration. The project approach emphasizes narrow claims, reproducible acceptance, fail-closed execution and explicit separation between model-generated candidates and deterministic trust decisions.

The main capability gap is automotive validation-domain expertise, not core AI/platform engineering. The Advance plan therefore explicitly relies on Siemens Industry Software NV, RobustifAI and AI-BOOST technical guidance for taxonomy semantics, benchmark data, traffic/kinematic constraints and industrial validation relevance rather than claiming pre-existing homologation or automotive-safety authority.

Public evidence:
https://evidencebound.org
https://github.com/moneyparking/evidencebound-core
https://github.com/moneyparking/evidencebound-core/pull/26

### Risk Management & Mitigation

**Characters:** 1155 / 1500

Domain-semantic risk: generated fields may be plausible but wrong; mitigate with source-level evidence binding, labelled evaluation, uncertainty and Challenge Owner review. Sparse/conflicting evidence: preserve UNKNOWN/conflict state and require REVIEW_REQUIRED/BLOCKED rather than silent completion. GenAI drift/vendor dependence: version models/prompts, keep provider abstraction and deterministic regression fixtures. Physical inconsistency: add kinematic/traffic-physics checks and block invalid simulation outputs. Matching generalization: evaluate on heterogeneous holdouts and report Recall@K/MRR plus error analysis, not only the small SPARK fixture score. Dataset/licensing/PII risk: use approved/public data, minimize retained fields and prohibit external transmission of sensitive data. Scale/cost risk: batch, cache and selectively re-evaluate affected branches; measure cost/runtime. Automotive-domain gap: use Siemens/RobustifAI feedback and standards/dataset guidance rather than claiming existing domain authority. IP risk: keep pre-existing EvidenceBound Core/reference systems documented as background and isolate Challenge 4 foreground.

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
- Retained benchmark baseline: https://github.com/moneyparking/evidencebound-core/blob/ai-boost-challenge-4/benchmarks/ai_boost_challenge4/BASELINE.json
- Reproduction instructions: https://github.com/moneyparking/evidencebound-core/blob/ai-boost-challenge-4/benchmarks/ai_boost_challenge4/README.md

## SUBMISSION SAFETY NOTES

- The measured 100% values are explicitly scoped to **2 sanitized public NHTSA VICIS cases + 2 controlled adversarial mutations**. Never restate them as general automotive accuracy.
- Current Functional Scenario benchmark extraction is a deterministic coded-record baseline. The architecture contains a provider seam for schema-constrained LLM/VLM extraction; actual GenAI benchmark performance is not yet claimed.
- Current ASAM OpenSCENARIO XML 1.4 output is a structural export seam and is explicitly **not yet XSD validated**.
- EvidenceBound Core and pre-existing reference implementations are Background IP. Challenge 4 domain adapters, benchmark integration and scenario pipeline are proposed Foreground.
- Submit one deliberate proposal only. If multiple proposals are submitted, the competition rules state only the last timestamped proposal is evaluated.
