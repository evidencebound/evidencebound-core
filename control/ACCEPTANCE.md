# EvidenceBound Control Center Acceptance

A substantive Control Center task ends in exactly one state: `PASS`, `BLOCKED`, or `FAIL`.
`PASS` is permitted only when every scoped condition has current executed evidence. A queued,
skipped, historical, local-only, or remembered result is not PASS for a claim that requires more.

## Scenario A — Route-safe progressive disclosure

Given a substantive task,
when an agent starts work,
then it reads `control/CONTROL.yaml`, this acceptance contract, and exactly one primary route's
`read_first` sources before broadening context.

If another route is required, the dependency and reason are recorded in the session knowledge delta.

## Scenario B — No unverified completion

Given a task with defined completion evidence,
when implementation or analysis exists but required verification has not completed successfully,
then the task is not marked `PASS`.

Queued, skipped, cancelled, historical, assumed, or merely local evidence does not satisfy a current
external or exact-head acceptance requirement.

## Scenario C — Public/private isolation

Given that this repository is public,
when Control Center artifacts are validated,
then they contain only local public paths and generic references to a `private benchmark workspace`.

Identifying external private repository URLs or private benchmark internals cause validation to fail.

## Scenario D — Authority-gated external effects

Given a consequential external effect,
when no separate project rule or explicit human authority permits that effect,
then the operation remains `DENY` and no Control Center field may mint or widen authority.

Existing narrower project, release, production, and runtime authorization rules outrank this generic
control-plane contract.

## Scenario E — Verified knowledge promotion

Given a new fact, correction, decision, or failed approach from a substantive session,
when it is proposed for durable project truth,
then a machine-readable knowledge delta records its verification evidence before any authoritative
source is updated.

A knowledge delta is evidence about a session; it does not automatically make its claims authoritative.

## Outcome contract

- `PASS`: every scoped acceptance condition has current executed evidence.
- `BLOCKED`: a named external or authority boundary prevents further safe execution; record evidence
  and the minimum next action.
- `FAIL`: verification or acceptance failed without an unresolved external blocker; record the failed
  condition and evidence.

## Self-check

```bash
python tools/validate_control_center.py
python -m pytest -q tests/test_control_center_contract.py
```
