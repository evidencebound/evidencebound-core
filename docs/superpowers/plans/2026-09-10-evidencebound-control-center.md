# EvidenceBound Control Center Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a public repo-native Control Center that routes agents to minimal authoritative context, makes project acceptance executable, preserves verified session deltas, and fails closed on privacy or authority violations.

**Architecture:** `control/CONTROL.yaml` is a JSON-compatible YAML routing index, not a duplicate project database. Existing Core artifacts remain canonical owners of mutable facts. A stdlib-only validator plus pytest contract enforce routes, acceptance, safe authority defaults, knowledge-delta structure, and public/private isolation. A dedicated CI lane verifies the control plane without adding runtime dependencies or consequential external effects.

**Tech Stack:** Python 3.10+, stdlib `json`/`pathlib`/`hashlib`, pytest, GitHub Actions, existing EvidenceBound Core CI.

**Spec:** `docs/superpowers/specs/2026-09-10-evidencebound-control-center-design.md`

## Global Constraints

- Public repository: never encode identifying private benchmark repository internals in public Control Center artifacts.
- Preserve tagged `v0.3.0` historical truth; newer `main` is separate Unreleased truth.
- Do not change runtime package APIs, dependencies, WebMCP runtime behavior, release tags, PyPI state, credentials, or production surfaces.
- Chat/model memory is non-authoritative.
- Consequential external actions remain DENY unless separately authorized.
- `PASS` requires executed evidence; queued/skipped/remembered checks are not PASS.

### Task 1: RED — Control Center contract

**Files:** Create `tests/test_control_center_contract.py`; create draft PR after the RED commit.

- [ ] Add tests asserting required `/control`, validator, evidence index, route names, safe default gates, and public privacy contract.
- [ ] Push the test-only commit before implementation.
- [ ] Verify the PR-triggered CI fails for the expected missing-Control-Center reason, not infrastructure noise; preserve run evidence.

### Task 2: GREEN — Minimal public Control Center

**Files:** Create `control/CONTROL.yaml`, `control/ACCEPTANCE.md`, `control/AUTHORITY.md`, `control/knowledge_delta.schema.json`, `tools/validate_control_center.py`, `evidence/control-center/INDEX.md`.

- [ ] Encode five progressive-disclosure routes: core runtime/invariants; release/supply-chain; adoption/security; WebMCP public surface; public benchmark interface.
- [ ] Point mutable facts to existing canonical owners instead of copying them.
- [ ] Encode fail-closed external-effect gates and non-authoritative-memory rule.
- [ ] Implement stdlib-only structural/schema-shape validator with deterministic JSON output and nonzero exit on any violation.
- [ ] Verify focused tests and validator become GREEN.

### Task 3: Knowledge persistence, entrypoint, and CI

**Files:** Create `evidence/control-center/knowledge_deltas/2026-09-10-control-center-bootstrap.json`, `.github/workflows/control-center.yml`; modify `AUTONOMOUS_HANDOFF.md` and minimally `README.md` if needed for discoverability.

- [ ] Persist a bootstrap delta containing only independently verified public repository facts and decisions.
- [ ] Make the handoff explicitly secondary/historical and route substantive agent work through `control/CONTROL.yaml`.
- [ ] Add path-scoped Control Center CI with read-only permissions, pinned existing checkout/setup-python actions, Python 3.13, validator and focused pytest.
- [ ] Ensure the workflow performs no deployment/publication/provider calls and adds no dependency.

### Task 4: Exact-head acceptance and PR evidence

- [ ] Run/observe focused Control Center lane and existing relevant Core CI on the exact PR head.
- [ ] Diagnose and repair only in-scope failures; rerun until GREEN or a real external blocker is proven.
- [ ] Verify final diff contains no identifying private-workspace leakage and no unrelated runtime changes.
- [ ] Update PR body with RED evidence, GREEN evidence, exact head SHA, acceptance result, and truthful blockers.
- [ ] Mark PR ready only after exact-head required CI is successful.

## Definition of Done

`CODE/CONFIG + TESTS + SEPARATE PR + EXACT-HEAD GREEN CI + VERIFIED ACCEPTANCE + EVIDENCE + KNOWLEDGE DELTA + UPDATED CONTROL CENTER`.

Merge/post-merge verification are separate integration steps and require the applicable repository/project authority.