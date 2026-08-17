# AI-BOOST Challenge 4 — SPARK Concept Note Draft

**Challenge:** Generative AI for Automatic Test Case Generation from Crash Databases & Standards — Siemens Industry Software NV / RobustifAI  
**Project title:** EvidenceBound ScenarioGraph — Evidence-grounded crash-to-validation scenario generation  
**Applicant:** Ruslan Vrublevskyi  
**Legal status:** Individual  
**Application language:** English  
**Submission deadline:** 8 September 2026, 17:00 Brussels time  
**Submission platform:** F6S / AI Challenge Competition #2

> This document is a working application draft. Claims about future KPI values are targets, not measured results. Pre-existing EvidenceBound Core is background technology; Challenge 4 domain adapters, benchmark integration and scenario pipeline are proposed foreground work.

## Admin

1. **Full Name / Team Name / Organization Name:** Ruslan Vrublevskyi / EvidenceBound ScenarioGraph
2. **Email:** ruslan@evidencebound.org
3. **Phone:** TODO — enter current applicant phone in F6S
4. **Country of Residence / Registration:** Ukraine
5. **Legal Status:** Individual
6. **Consortium structure:** Not a consortium at SPARK submission. The applicant will collaborate with the Challenge Owner and technical mentors as required by the programme.

## EXCELLENCE

### 1. Project Title

**EvidenceBound ScenarioGraph — Evidence-grounded crash-to-validation scenario generation**

### 2. Specific problem

Challenge 4: Generative AI for automatic test-case generation from crash databases and standards.

### 3. Problem Fit & Contribution — max 1,500 characters

EvidenceBound ScenarioGraph addresses the challenge’s central bottleneck: converting fragmented accident evidence and safety standards into structured scenario knowledge without losing provenance or silently inventing missing facts. The pipeline extracts Functional Scenarios, enriches them into Logical Scenarios, normalizes them into a common typed representation, and matches them against validation catalogues. Every material generated attribute is bound to explicit source evidence, provenance, confidence/uncertainty and applicability state. Unsupported or conflicting fields are not treated as plausible facts: they are marked REVIEW_REQUIRED or BLOCKED. A dependency graph records which scenario fields and downstream test cases depend on which evidence, so changed or refuted evidence invalidates only the affected branch and triggers selective regeneration. This directly supports engineers and validation experts who need scalable scenario generation while preserving traceability, explainability and human review.

### 4. Quantifiable Outcomes — max 1,500 characters

Spark/Advance targets will be measured on organizer datasets and reproducible public fixtures, with no fabricated baseline claims. Target KPIs: ≥95% of material generated scenario attributes carry machine-readable source references; <2% unsupported-assertion rate on deliberately incomplete fixtures; 100% explicit uncertainty state for missing/conflicting evidence; functional-scenario taxonomy macro-F1 target ≥0.80; logical-attribute completeness/correctness target ≥0.80 on labelled subsets; scenario-to-catalog Recall@5 target ≥0.90 with MRR reported; uncertainty calibration reported with Brier score/ECE; 100% deterministic validation receipts reproducible from the same normalized inputs and policy version; 100% invalidated descendants detected in controlled evidence-change tests; containerized evaluation runnable from a documented command. Runtime and cost per 1,000 records will be tracked and optimized during Advance.

### 5. Innovation & Novelty — max 1,300 characters

Most GenAI scenario pipelines optimize extraction or generation quality, then add citations as presentation metadata. EvidenceBound ScenarioGraph makes evidence applicability part of the execution model. Each scenario claim is a typed node bound to source evidence, provenance, uncertainty and policy; downstream scenario/test-case nodes form an explicit dependency graph. If evidence becomes stale, missing or refuted, the system computes the exact blast radius and selectively re-generates only affected descendants. A deterministic gate prevents unsupported fields, inconsistent state and non-reproducible outputs from being promoted merely because an LLM produced plausible text. The novelty is the combination of generative multimodal extraction with evidence-bound state, field-level uncertainty, dependency-aware invalidation, fail-closed verification and reproducible receipts—turning traceability from an audit afterthought into a runtime property.

### 6. Technology Readiness — max 1,500 characters

EvidenceBound Core is existing Apache-2.0 background technology with working deterministic verification, provenance-bound state, dependency blast-radius analysis and selective recovery. Related public reference implementations demonstrate these primitives across multi-agent recovery, governed data actions and verified memory. The Challenge 4 foreground begins at TRL 3: a domain-specific proof of concept will adapt these mature trust primitives to crash-data scenario extraction, logical enrichment and validation-catalog matching using public datasets and standards. During Advance, we will integrate challenge datasets, benchmark extraction/enrichment/matching, add OpenSCENARIO-compatible structured export, harden uncertainty/physics constraints, containerize the full evaluation path, and validate with Challenge Owner workflows. The goal is TRL 5: an integrated prototype validated in a relevant automotive-safety scenario preparation environment, not a production homologation claim.

### 7. AI Technology & Justification — max 2,000 characters

The foreground pipeline uses a hybrid generative + deterministic architecture. (1) Retrieval/normalization ingests heterogeneous crash records, textual reports, standards and linked multimodal context into source-addressed evidence objects. (2) A schema-constrained LLM/VLM extraction layer generates Functional Scenario candidates and evidence-linked fields; model providers remain replaceable. (3) Retrieval and multimodal enrichment infer Logical Scenario attributes only with explicit evidence references and calibrated uncertainty. (4) A typed ScenarioGraph canonicalizes entities, parameters, relationships and source bindings. (5) A hybrid matcher combines semantic retrieval/embeddings with structured constraints to map accident-derived scenarios to reference validation catalogues and estimate coverage gaps. (6) Deterministic validators enforce schema, provenance completeness, uncertainty requirements, consistency and basic physical/kinematic constraints. (7) EvidenceBound computes dependency blast radius after source changes and selectively re-evaluates affected nodes. (8) Outputs include a common structured representation and, where applicable, OpenSCENARIO-compatible artifacts plus reproducible Proof Receipts. This architecture uses GenAI where ambiguity and abstraction require it, while deterministic controls own trust decisions.

### 8. Trustworthy, Responsible AI & Compliance — max 2,000 characters

Trustworthiness is a first-class system property rather than a post-processing report. The LLM/VLM may propose scenario facts but cannot grant them trusted status. Every material field stores source references, transformation provenance, model/prompt/version metadata, confidence or uncertainty, and validation status. Missing evidence is represented explicitly; the system is designed to BLOCK or require human review rather than hallucinate a complete scenario. Deterministic validators enforce structured-output schemas, evidence completeness, cross-field consistency and basic physical/kinematic constraints before export. Evidence changes trigger dependency-aware invalidation and selective regeneration so stale conclusions are not silently reused. Reproducible receipts bind normalized evidence, generated state, validation policy and output hashes. Human oversight remains explicit for ambiguous or safety-relevant fields. External models/APIs are disclosed, and the architecture supports provider substitution or local models where data policy requires it. Evaluation will separately report generation quality, evidence coverage, uncertainty calibration and failure modes instead of collapsing them into one opaque score.

### 9. Ethics & Data Governance — max 1,500 characters

The prototype will use public, licensed, organizer-provided or properly authorized datasets and will follow data-minimization principles. PII and sensitive accident information will not be sent to external AI services; any dataset requiring such processing will be anonymized or handled in an approved local/private execution path. The pipeline records data source, license/access context and transformation provenance. Sensitive attributes are not inferred unless required by the benchmark and ethically justified. Uncertainty is mandatory when evidence is incomplete or conflicting, and human review is required for ambiguous safety-relevant outputs. External models, APIs and cloud services will be fully disclosed. Evaluation will include provenance coverage, unsupported-assertion tests, uncertainty calibration, reproducibility and consistency across heterogeneous sources. The system is an engineering validation aid, not a legal-compliance, homologation or certification authority.

## IMPACT

### 1. Sustainability & Scalability AI — max 2,000 characters

ScenarioGraph is designed as a modular adapter around the framework-agnostic Apache-2.0 EvidenceBound Core. New countries, accident schemas, standards, model providers and validation catalogues are added through adapters rather than rewriting the trust model. Canonical typed scenario/evidence contracts enable batch processing, caching, selective re-evaluation and provider substitution. Dependency-aware recovery avoids regenerating unaffected scenario branches when evidence changes. The evaluation stack will be containerized, dependency-pinned and runnable without mandatory HPC; scale and cost per 1,000 records will be measured. Open interfaces and reproducible benchmark fixtures reduce lock-in and support reuse by research groups, safety engineers and public-sector stakeholders. Challenge-specific IP is isolated from pre-existing EvidenceBound Core, allowing the solution to evolve after the competition while preserving a stable, reusable OSS assurance layer.

### 2. Social & Environmental Impact — max 1,500 characters

The project targets safer and more evidence-grounded automated-driving validation. By linking generated scenarios to real accident evidence and explicitly exposing uncertainty, it can help engineers prioritize under-covered safety cases without treating synthetic plausibility as fact. Better reuse of accident evidence may reduce manual scenario-engineering effort and improve access to traceable validation workflows for smaller research and engineering teams. Computational impact will be monitored through model-call counts, runtime and cost; selective re-evaluation is intended to avoid unnecessary repeated generation when only part of the evidence changes. The system does not claim direct reduction of crashes or regulatory compliance at Spark stage; impact will be demonstrated through measurable improvements in traceability, reproducibility and validation-coverage analysis.

### 3. Fairness, Diversity & Open Science — max 1,500 characters

The benchmark plan will test consistency across heterogeneous country/region datasets and report performance by source type rather than only aggregate accuracy. Scenario diversity and representativeness will be measured to reduce overfitting to dominant accident patterns. Missing demographic or contextual information will remain unknown rather than be imputed as fact without evidence. Where protected or sensitive attributes are present, their use will be minimized and evaluated for necessity and bias risk. Reproducible fixtures, schemas, evaluation scripts and non-sensitive benchmark artifacts will be published where dataset licences permit. The pre-existing EvidenceBound Core remains Apache-2.0; challenge-specific outputs will respect AI-BOOST and dataset IP terms while maximizing transparent methods and reusable evaluation assets.

### 4. Exploitation & Potential for Collaboration — max 2,000 characters

The immediate exploitation path is technical collaboration with Siemens Industry Software NV and RobustifAI to validate the scenario-evidence and trust pipeline in a relevant engineering workflow. Beyond the challenge, the same architecture can support scenario-database curation, safety-case preparation, validation coverage analysis and traceable GenAI workflows in mobility and other safety-critical domains. The project will keep pre-existing EvidenceBound Core as clearly identified background IP and isolate challenge-specific foreground components, enabling the Challenge Owner’s competition rights without transferring the general OSS trust runtime into the foreground scope. After the competition’s exclusivity period, collaboration, licensing or integration can be negotiated separately under the programme terms. Open interfaces and a documented benchmark path are intended to make research replication and later industrial integration practical.

## QUALITY OF IMPLEMENTATION

### 1. Work Plan (Advance) — max 3,000 characters

Month 0 / Spark: finalize domain schema, public-data fixture, evidence-binding contract, risk register and baseline extraction benchmark. Deliver a runnable crash-record → Functional Scenario → evidence receipt vertical slice.

Month 1: ingest/normalize representative public and Challenge Owner datasets; implement source-addressed Evidence objects, taxonomy mapping and schema-constrained Functional Scenario extraction. Establish labelled evaluation subset and baseline metrics.

Month 2: add Logical Scenario enrichment from linked text/multimodal context; introduce field-level uncertainty, conflicting-evidence handling and provenance completeness gates. Benchmark completeness/correctness and uncertainty calibration.

Month 3: implement structured ScenarioGraph and hybrid validation-catalog matching; measure Recall@K/MRR and coverage-gap usefulness. Add dependency graph and evidence-change invalidation tests.

Month 4: add deterministic safety checks for schema consistency, evidence support and basic kinematic/physical constraints; produce OpenSCENARIO-compatible structured export where applicable. Integrate containerized reproducibility and tamper-evident receipts.

Month 5: optimize scale/cost, validate on new datasets, run adversarial missing/conflicting-evidence suites, prepare Challenge Owner integration demo, final benchmark report and live demonstration.

Continuous: disclose external models/APIs; privacy review; tests/CI; versioned datasets/configuration; human-review UX for REVIEW_REQUIRED cases. CINECA is not required for the initial architecture but can be evaluated if model training/large-scale multimodal processing later justifies it.

### 2. Need CINECA?

**No for SPARK / initial architecture.** Re-evaluate during Advance if organizer-scale multimodal training or benchmarking justifies HPC.

### 3. Resources / Infrastructure — max 1,500 characters

Existing resources: public EvidenceBound Core (Python, Apache-2.0), CI/release/security controls, prior reference implementations for verifiable memory and multi-agent recovery, GitHub-based reproducibility, and cloud experience across AWS and Google Cloud. Challenge work will use Python, typed schemas/Pydantic, structured LLM/VLM outputs, vector/semantic retrieval, deterministic validators, containerized evaluation and public crash/safety datasets before Challenge Owner data access. Compute will start with commodity/cloud CPU/GPU and provider APIs selected under data-policy constraints; no HPC dependency is assumed. Storage will be content-addressed where practical, with dataset/model/prompt/config versions retained for benchmark replay. Public artifacts will exclude restricted datasets and PII while preserving reproducible synthetic/public fixtures.

### 4. Team Credentials & Expertise — max 1,750 words

Ruslan Vrublevskyi — systems architect and maintainer/creator of EvidenceBound Core. Experience includes design and delivery of agentic AI systems, deterministic verification, provenance-bound state, dependency-graph invalidation, selective recovery, tamper-evident evidence, verifiable memory, multi-agent orchestration, API/backend systems, CI/CD and cloud deployment. Public EvidenceBound implementations include: Recovery Mesh (Google ADK / Gemini / Cloud Run, deterministic trust-break blast-radius analysis and selective recomputation), DataHub Gate (MCP metadata binding, restricted execution, SHA-256 Proof Packs and Ed25519 verification), and Verified Memory (CockroachDB + AWS, canonical historical snapshots, integrity verification and current-applicability separation). The core is framework-agnostic Python and has public architecture, threat model, tests, release/supply-chain evidence and interoperability work. For Challenge 4, the principal gap is automotive-domain validation expertise rather than core AI/system engineering; the work plan therefore explicitly uses Challenge Owner/RobustifAI technical guidance and standards/dataset feedback to validate taxonomy, scenario semantics and engineering relevance instead of pretending pre-existing automotive specialization.

### 5. Risk Management & Mitigation — max 1,500 characters

Domain-semantic risk: generated scenario fields may be plausible but wrong. Mitigation: source-level evidence binding, labelled subsets, uncertainty state, deterministic gates and Challenge Owner review. Sparse/conflicting data: do not fill silently; retain UNKNOWN/REVIEW_REQUIRED and calibrate uncertainty. Dataset/licensing/PII risk: use approved/public data, isolate restricted data, prohibit external transmission of PII, disclose providers. Model drift/vendor dependence: version prompts/models, maintain provider abstraction and regression fixtures. Physical inconsistency: add rule/kinematic validators and BLOCK invalid outputs. Matching quality risk: combine semantic retrieval with structured constraints and report Recall@K/MRR plus error analysis. Scale/cost risk: batch, cache, selective re-evaluation and benchmark cost per 1,000 records. IP risk: explicitly separate pre-existing EvidenceBound Core background IP from Challenge 4 foreground adapters, benchmark and domain pipeline.

## Before F6S submission

- [ ] Confirm applicant phone number.
- [ ] Confirm exact F6S profile name/email.
- [ ] Re-check online F6S wording against Annex 1; online form prevails if different.
- [ ] Add link to a runnable SPARK prototype and controlled benchmark receipt.
- [ ] Add exact public dataset(s) used in the prototype.
- [ ] Add measured baseline results only after reproducible run.
- [ ] Review IP/background/foreground statement against participation agreement if selected.
- [ ] Submit once, deliberately, because only the last proposal per applicant is evaluated.
