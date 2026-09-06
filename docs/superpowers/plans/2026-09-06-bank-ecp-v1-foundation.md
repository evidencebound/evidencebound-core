# BANK-ECP v1 Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a private, reproducible EU Banking/FinTech regulatory benchmark foundation with an authoritative source registry, claim-level evidence passports, deterministic hard gates, reviewed seed cases, reproducible metrics and preserved run receipts.

**Architecture:** Keep all regulatory policy and benchmark internals under `benchmarks/bank_ecp_v1/`; do not alter the public `src/evidencebound` API. Use stdlib-only Python, JSON fixtures and deterministic canonical SHA-256 records. Live LLM execution is a separate adapter boundary and is not required for foundation PASS.

**Tech Stack:** Python 3.10+, dataclasses/enums, stdlib `json`/`hashlib`, pytest, existing EvidenceBound CI.

**Spec:** `docs/superpowers/specs/2026-09-06-bank-ecp-v1-foundation-design.md`

## Global Constraints

- EU Banking / FinTech only; no insurance expansion.
- No unconditional runtime dependency additions.
- No SignalReview runtime dependency.
- No paid model calls without owner approval.
- Official primary sources are ground truth when available.
- `BANK_ECP_POLICY_v1` hard gates cannot be overridden by model confidence or weighted scores.
- Holdout labels cannot be used for policy tuning.
- No public release, external outreach or production mutation.

---

### Task 1: Source registry validator and authoritative seed

**Files:**
- Create: `benchmarks/bank_ecp_v1/source_registry.py`
- Create: `benchmarks/bank_ecp_v1/source_registry.json`
- Test: `tests/test_bank_ecp_source_registry.py`

**Interfaces:**
- Produces: `load_source_registry(path: Path) -> dict[str, SourceRecord]`, `registry_digest(records: Mapping[str, SourceRecord]) -> str`.

- [ ] Write tests requiring unique source IDs, HTTPS canonical URLs, EU jurisdiction, ISO dates, authoritative status, exact deterministic registry fingerprint and rejection of duplicate/malformed records.
- [ ] Run `pytest tests/test_bank_ecp_source_registry.py -q` and retain the expected RED result before implementation.
- [ ] Implement frozen `SourceRecord`, canonical JSON normalization and SHA-256 fingerprint verification with no network dependency.
- [ ] Add reviewed metadata for DORA, MiCA, EU AI Act, Regulation (EU) 2023/1113, EBA Travel Rule Guidelines and ESMA reverse-solicitation guidance.
- [ ] Run the source-registry tests to GREEN.

### Task 2: RegulatoryEvidencePassport v1

**Files:**
- Create: `benchmarks/bank_ecp_v1/schema.py`
- Test: `tests/test_bank_ecp_passport.py`

**Interfaces:**
- Produces: `RegulatoryEvidencePassport`, `CitationRef`, enum state types, and `validate_passport(passport) -> tuple[str, ...]`.

- [ ] Write tests for a complete supported passport and fail-closed rejection of missing claim ID, malformed jurisdiction state, contradictory evidence flags, missing material exception details and missing citation locators.
- [ ] Run passport tests and retain RED.
- [ ] Implement immutable dataclasses/enums and deterministic validation.
- [ ] Run passport tests to GREEN.

### Task 3: BANK_ECP_POLICY_v1 hard gates

**Files:**
- Create: `benchmarks/bank_ecp_v1/policy.py`
- Test: `tests/test_bank_ecp_policy.py`

**Interfaces:**
- Produces: `Verdict`, `PolicyDecision`, `evaluate_passport(passport: RegulatoryEvidencePassport) -> PolicyDecision`.

- [ ] Write one failing test per hard gate: unsupported citation, wrong jurisdiction, stale/superseded authority, omitted material exception, unresolved contradiction, no authoritative evidence, missing human authority; add clean PASS and uncertainty-only CAUTION tests.
- [ ] Add an adversarial test proving `model_confidence=1000` cannot override any hard gate.
- [ ] Run policy tests and retain RED.
- [ ] Implement deterministic precedence: material HOLD gates first, no-authority ABSTAIN next, uncertainty CAUTION, otherwise PASS.
- [ ] Run policy tests to GREEN.

### Task 4: Benchmark case contract and reviewed seed

**Files:**
- Create: `benchmarks/bank_ecp_v1/dataset.py`
- Create: `benchmarks/bank_ecp_v1/cases_development.json`
- Create: `benchmarks/bank_ecp_v1/cases_holdout_seed.json`
- Test: `tests/test_bank_ecp_dataset.py`

**Interfaces:**
- Produces: `BenchmarkCase`, `load_cases(path)`, `validate_case_set(cases, source_ids)`.

- [ ] Write tests requiring unique immutable IDs, valid source references, split consistency, expected verdict, controlled mutation provenance and traceable reviewer rationale.
- [ ] Enforce that development and holdout IDs do not overlap and that no source/reference is invented.
- [ ] Run dataset tests and retain RED.
- [ ] Implement parser/validator.
- [ ] Add a reviewed seed spanning supported, unsupported extrapolation, citation mismatch, wrong jurisdiction, stale/future applicability, omitted exception, conflicting authority, missing evidence, high-confidence unsupported output and false-HOLD controls.
- [ ] Run dataset tests to GREEN.

### Task 5: Metrics and deterministic evaluator

**Files:**
- Create: `benchmarks/bank_ecp_v1/metrics.py`
- Create: `benchmarks/bank_ecp_v1/evaluate.py`
- Test: `tests/test_bank_ecp_metrics.py`
- Test: `tests/test_bank_ecp_evaluate.py`

**Interfaces:**
- Produces: `MetricCounts`, `compute_metrics(...)`, `evaluate_cases(cases) -> RunArtifact`.

- [ ] Write tests for all required metric numerators/denominators and `null` undefined ratios.
- [ ] Write an independent recomputation test from raw case decisions rather than trusting serialized metrics.
- [ ] Run evaluator tests and retain RED.
- [ ] Implement integer-count metrics and deterministic canonical run artifact with SHA-256 receipt.
- [ ] Add CLI mode `python benchmarks/bank_ecp_v1/evaluate.py --split development --output <path>`.
- [ ] Run evaluator tests to GREEN.

### Task 6: Falsification suite and seed development evaluation

**Files:**
- Create: `tests/test_bank_ecp_adversarial.py`
- Create: `benchmarks/bank_ecp_v1/README.md`

**Interfaces:**
- Consumes: source registry, schema, policy, dataset and evaluator.

- [ ] Add adversarial cases for near-match citations, partial claim support, future applicability, hidden exception, unresolved conflict, missing definition dependency and high-confidence unsupported output.
- [ ] Prove at least one clean supported case is not falsely held for each source family represented in the seed.
- [ ] Run focused tests then complete `pytest`.
- [ ] Run development deterministic evaluation twice and verify identical artifact digest.
- [ ] Document that these results are policy/harness sanity evidence, not same-model LLM improvement.

### Task 7: Freeze guard and live experiment boundary

**Files:**
- Create: `benchmarks/bank_ecp_v1/freeze.py`
- Create: `tests/test_bank_ecp_freeze.py`
- Create: `benchmarks/bank_ecp_v1/live_protocol.md`

**Interfaces:**
- Produces: `FreezeManifest`, `build_freeze_manifest(...)`, validation that policy/source/dataset hashes are fixed before holdout execution.

- [ ] Write tests proving manifest changes when policy/source/development/holdout bytes change and that a missing commit SHA cannot be frozen.
- [ ] Run RED, implement, then run GREEN.
- [ ] Document same-model/same-corpus baseline/control protocol, model/prompt/config provenance fields and raw-output retention rules.
- [ ] Do not execute paid/live provider calls in this task.

### Task 8: Verification and internal handoff

**Files:**
- No production file required unless verification discovers a tested defect.

- [ ] Run all pytest tests.
- [ ] Run `python -m compileall -q src examples benchmarks compat tools`.
- [ ] Run `ruff check .` if available in CI/local execution.
- [ ] Verify existing core files are unchanged via branch diff.
- [ ] Run repository secret/security checks already configured in CI; do not print secret values.
- [ ] Preserve exact branch SHA, test evidence, benchmark seed counts, source registry digest and known limitations.
- [ ] Do not freeze the empirical benchmark or prepare sales claims unless a credible same-model held-out result exists.
