# EvidenceBound Control Center Design

Date: 2026-09-10
Status: Design approved in chat; implementation not started
Scope: EvidenceBound public Core repository

## 1. Purpose

Add a repo-native Control Center that makes project truth durable, progressively discoverable, and executable without turning chat memory into authority.

The operating loop is:

`Control Center -> select context -> executable acceptance -> execution -> verification -> evidence -> knowledge delta -> authoritative update`

The Control Center is a coordination and verification layer. It does not replace existing source code, release evidence, CI, roadmap, threat model, competition evidence, or production readback. It routes agents to the smallest authoritative context required for the current task and defines what evidence is required before project state may advance.

## 2. Public/private boundary

This repository is public. It MUST NOT disclose the name, URL, branch names, hidden datasets, holdout contents, private evaluation internals, provider credentials, commercialization evidence, or other identifying internals of any private benchmark workspace.

The public Core may refer only to a generic `private benchmark workspace` when a cross-project dependency must be acknowledged. That reference is navigational, not authoritative for the private workspace.

No public Control Center file may require access to private benchmark internals in order to validate the public Core repository.

## 3. Design choice

Use a repo-native Control Center under `/control` with machine-readable state plus human-readable acceptance contracts.

Planned public structure:

```text
/control
  CONTROL.yaml
  ACCEPTANCE.md
  AUTHORITY.md
  knowledge_delta.schema.json

/evidence/control-center
  INDEX.md

/tools
  validate_control_center.py

/tests
  test_control_center_contract.py
```

Existing authoritative artifacts remain where they already live. The Control Center references them instead of duplicating mutable facts.

## 4. Source-of-truth model

`control/CONTROL.yaml` is the entrypoint and routing index, not a universal database.

It records:

- project identity;
- current objective and status;
- canonical source owners for mutable facts;
- context routes;
- acceptance references;
- authority boundaries;
- blockers;
- verification requirements;
- freshness rules;
- evidence and knowledge-delta locations.

When two sources conflict, the Control Center MUST define precedence or mark the state unresolved. It MUST NOT silently choose a convenient value.

Chat history, model memory, generated prose, and stale handoff summaries are non-authoritative unless independently verified against a listed source.

## 5. Progressive context selection

Every substantive agent session starts with:

1. repository-level safety/project instructions if present;
2. `control/CONTROL.yaml`;
3. `control/ACCEPTANCE.md` for the selected objective;
4. only the authoritative files listed by the selected context route.

The agent MUST NOT recursively read the entire repository by default.

Initial Core routes should cover at least:

- `core_runtime_and_invariants`;
- `release_and_supply_chain`;
- `adoption_and_security`;
- `webmcp_public_surface`;
- `public_benchmark_interface` where only public-safe benchmark integration facts are needed.

Each route specifies `read_first`, optional secondary context, freshness source, and completion evidence.

## 6. Executable acceptance

`control/ACCEPTANCE.md` defines executable project-level scenarios. At minimum:

### A. Context isolation

Given a substantive task, when an agent selects a route, then only that route's authoritative context is required unless an explicit dependency is discovered and recorded.

### B. No unverified completion

A task may be marked `PASS` only when every required acceptance condition has current evidence. A written claim, local artifact, queued workflow, skipped workflow, or remembered prior result is not PASS.

### C. Public/private isolation

Public validation fails if public Control Center artifacts contain private benchmark repository identifiers or private benchmark internals.

### D. Authority-gated external effects

External publication, deployment, registry publication, external messaging, spending, destructive mutation, or other consequential effects remain subject to existing project approval rules. The Control Center cannot mint authority.

### E. Knowledge promotion

A new fact or correction may enter authoritative project state only after verification evidence is recorded in a valid knowledge delta.

## 7. Authority model

`control/AUTHORITY.md` defines control-plane permissions, not product runtime authorization.

Default rule: repository-local inspection, documentation, tests, and reversible feature-branch work may proceed under normal repository permissions. Consequential external side effects remain DENY unless separately authorized by existing project rules or explicit human approval.

The Control Center MUST preserve existing EvidenceBound fail-closed principles: absence of required authority or evidence is not interpreted as success.

## 8. Knowledge delta

A substantive session emits a machine-valid knowledge delta. Planned required fields:

```yaml
session_id: string
at_utc: timestamp
project: EvidenceBound Core
objective: string
result: PASS | BLOCKED | FAIL
new_facts: []
corrected_assumptions: []
decisions: []
failed_approaches: []
verification: []
authoritative_updates: []
```

Each verification entry includes source or command, status, and optional immutable digest/commit/run identifier.

A knowledge delta is evidence about a session outcome. It does not automatically update authoritative truth. Promotion occurs only after validation and the corresponding authoritative file update.

## 9. Verification and evidence

`tools/validate_control_center.py` will fail closed and verify at least:

- required Control Center files exist;
- project identity is correct;
- referenced public paths exist;
- context routes are structurally valid;
- acceptance scenarios are present;
- authority defaults are safe;
- knowledge-delta schema is valid;
- persisted knowledge deltas validate against the schema;
- forbidden private-workspace identifiers are absent from public Control Center artifacts;
- mutable truth is referenced to canonical owners rather than duplicated where duplication would create drift.

`tests/test_control_center_contract.py` exercises the validator contract and privacy boundary.

A dedicated CI workflow should run on changes to Control Center, validator, tests, relevant agent-entrypoint docs, and authoritative routing documents.

## 10. Integration with existing Core truth

The Control Center must route to existing authoritative artifacts rather than supersede them. Examples include:

- `ROADMAP.md` for roadmap state;
- `RELEASE_READINESS.md` for published release evidence and distribution boundaries;
- current CI workflows for executable repository verification;
- current threat/spec/competition evidence for their respective claims;
- current production readback where a claim depends on deployed behavior.

The Control Center must distinguish tagged-release truth from newer `main` truth and must not retroactively move release claims.

## 11. Failure handling

A substantive task ends in exactly one state:

- `PASS`: every required acceptance condition has current evidence;
- `BLOCKED`: progress is prevented by a specific external or authority boundary that cannot safely be resolved in the current execution;
- `FAIL`: acceptance or verification failed and the failure is not merely an external blocker.

For `BLOCKED` and `FAIL`, the delta records the exact source, failed condition, and next required action. No state advancement occurs merely because implementation work exists.

## 12. Non-goals

This design does not add:

- a SaaS Control Center;
- a database-backed orchestration service;
- a broad dashboard;
- cross-repository runtime coupling;
- private benchmark internals in the public repo;
- automatic authority escalation;
- automatic truth promotion without verification;
- unrelated runtime refactoring.

## 13. Implementation strategy

Implementation follows TDD on an isolated feature branch:

1. add a failing contract proving the Control Center is absent/incomplete;
2. implement the minimum `/control` structure and validator;
3. make focused tests GREEN;
4. add CI contract;
5. capture a bootstrap knowledge delta based on verified repository facts;
6. update public agent entrypoint/handoff docs to start from `control/CONTROL.yaml` where appropriate;
7. run exact-head CI;
8. open a separate PR with RED/GREEN and acceptance evidence.

## 14. Definition of Done

The public Core portion is complete only when:

- Control Center code/config/docs exist on a feature branch;
- focused contract tests pass;
- privacy-boundary tests pass;
- relevant repository CI passes on exact PR head;
- executable acceptance is checked against final branch state;
- bootstrap evidence and knowledge delta exist and validate;
- agent entrypoint routing is updated;
- no private benchmark repository identifier is introduced into public Control Center artifacts;
- PR evidence records exact head SHA and remaining blockers truthfully.

Merge and post-merge verification are separate integration steps and remain subject to repository/project approval boundaries.
