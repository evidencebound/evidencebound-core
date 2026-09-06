# BANK-ECP v1 Foundation — Design

Date: 2026-09-06
Status: Approved for autonomous private implementation by owner instruction
Scope: EU Banking / FinTech regulatory reasoning only

## Objective

Build a private, reproducible benchmark layer that can test whether an otherwise equivalent LLM/RAG system releases materially unsupported regulatory claims that EvidenceBound would hold or abstain from, without changing EvidenceBound Core's public runtime API.

The proof sequence remains: PROVE -> EXTERNAL VALIDATE -> SELL. A deterministic foundation or controlled mutation result is not itself evidence of LLM improvement.

## Architecture decision

Three approaches were considered:

1. Extend `src/evidencebound` with regulatory-specific contracts and policy. Rejected because the public core deliberately does not own source truth or business policy and regulatory internals are protected IP.
2. Add a private domain benchmark under `benchmarks/bank_ecp_v1/` that reuses core design principles but keeps regulatory schema, hard gates, dataset generation and evaluation methodology outside the public package. **Selected.**
3. Create a separate repository immediately. Rejected for v1 foundation because it adds release and synchronization complexity before empirical proof exists; a sanitized public proof can be carved out later if justified.

No SignalReview runtime dependency is introduced. SignalReview patterns may inform missing-evidence, bounded-verdict and replayable-artifact semantics only.

## Boundaries

- Do not modify existing production systems, site behavior or public package exports.
- Do not add unconditional runtime dependencies.
- Do not publish benchmark-generation internals, policy thresholds, full failure taxonomy or core prompts.
- Do not call paid model APIs automatically.
- Do not tune policy using held-out outcomes.
- Store only bounded source metadata and claim/evaluation fixtures, not bulk copyrighted legal text.
- Official primary sources are ground truth when available; secondary sources are discovery/context only.

## Source registry

`source_registry.json` records authoritative source metadata:

- `source_id`
- `authority`
- `instrument`
- `canonical_url`
- `jurisdiction`
- `article_sections`
- `effective_date`
- `applicability_date`
- `retrieved_date`
- `status`
- `currentness_note`
- `registry_fingerprint_sha256`

The fingerprint is a deterministic SHA-256 over canonical registry fields and is explicitly a registry-record integrity marker, not a cryptographic hash of the remote legal document.

Initial anchors cover DORA, MiCA, the EU AI Act, Regulation (EU) 2023/1113, EBA Travel Rule Guidelines and ESMA reverse-solicitation guidance. Each benchmark case references one or more registry IDs and exact article/section locators.

## RegulatoryEvidencePassport v1

A passport is claim-level, not answer-level. Required fields are derived from regulatory reasoning needs rather than a fixed row count:

- schema/passport/claim identifiers and materiality;
- claim text;
- jurisdiction and jurisdiction match state;
- applicable authority;
- instrument and article/section;
- effective/applicability date state;
- regulated entity type;
- applicability determination;
- obligation statement;
- exception state and material exceptions;
- definition dependencies;
- citations and citation-support state;
- authoritative-evidence presence;
- contradiction state and contradiction references;
- stale/superseded state;
- missing-evidence list;
- uncertainty list;
- required human authority and whether it is present.

Validation is deterministic and fails closed on malformed or internally inconsistent passports.

## Verdict contract

`BANK_ECP_POLICY_v1` emits one of:

- `PASS`: no hard gate and required evidence/authority conditions are satisfied.
- `CAUTION`: support is adequate but non-gating uncertainty remains.
- `HOLD`: a material hard gate prevents release.
- `ABSTAIN`: the material claim has no verifiable authoritative support and no stronger malformed/contradictory gate requires HOLD.

Hard-gate precedence is deterministic and cannot be overridden by model confidence or a weighted score.

### Hard gates

For material claims:

1. citation mismatch or citation that does not support the asserted proposition -> `HOLD`;
2. wrong jurisdiction -> `HOLD`;
3. materially stale/superseded authority -> `HOLD`;
4. omitted material exception -> `HOLD`;
5. unresolved authoritative contradiction -> `HOLD`;
6. no verifiable authoritative evidence -> `ABSTAIN`;
7. required human authority absent -> `HOLD`.

A non-material claim can still produce CAUTION but cannot silently upgrade a material failure elsewhere.

## Benchmark case contract

Each case contains:

- immutable case ID and benchmark version;
- split (`development` or `holdout`);
- category;
- question;
- evidence source IDs available equally to both experiment arms;
- expected passport facts and expected release verdict;
- controlled model-output fixture for deterministic policy tests;
- mutation provenance describing any injected failure;
- reviewer note explaining why the ground truth follows from the cited authority.

Target v1 size remains approximately 150-250 reviewed cases. This implementation pass creates a high-quality seed and validator/expansion pipeline; numerical scale may not substitute for defensible legal ground truth.

The held-out seed is physically separate. Development code may validate holdout schema and identifiers but must not calculate tuning thresholds from holdout labels.

## Fair experiment

Live proof compares:

A. Baseline LLM or LLM+RAG.
B. Same model, same question, same evidence corpus, plus EvidenceBound passport verification, policy and authority control.

Model outputs are retained verbatim with model/version, prompt/config hashes, source-registry hash, benchmark version, run timestamp and commit SHA. A deterministic pass-through baseline over controlled fixtures is permitted only as a harness sanity check and must never be reported as an LLM improvement result.

## Metrics

The evaluator computes integer counts and ratios for:

- Unsupported Claim Escape Rate;
- Citation Support Accuracy;
- Wrong-Jurisdiction Escape Rate;
- Exception Detection Rate;
- Contradiction Detection Rate;
- Correct HOLD Rate;
- False HOLD Rate;
- Evidence Trace Completeness.

Denominators are explicit. Undefined metrics are represented as `null`, never coerced to perfect scores.

## Falsification

Development cases intentionally include plausible near-match citations, wrong jurisdictions, future/not-yet-applicable provisions, stale authority, hidden exceptions, partial support, conflicting authority, missing definitions/evidence and high-confidence unsupported statements. At least one clean supported case per relevant source family is included to measure false HOLD.

Negative findings are retained. Policy changes after inspecting a frozen holdout require a new benchmark/policy version and a new holdout.

## Freeze protocol

Freeze is justified only when:

1. source registry is reviewed and hashed;
2. passport schema and `BANK_ECP_POLICY_v1` are tested;
3. development seed covers required failure classes;
4. deterministic evaluator independently recomputes metrics;
5. policy version and benchmark version are recorded in a commit;
6. no holdout labels were used for tuning.

The first real same-model held-out LLM run occurs only after the above. Its results are immutable evidence for that version; failures may motivate v2, not retroactive v1 tuning.

## Commercial proof boundary

Commercial materials are prepared only after a credible measured same-model result. Until then the internal deliverables are benchmark foundation, source registry, deterministic policy evidence, seed dataset and live-run protocol. External outreach, publication and customer claims remain owner-gated.
