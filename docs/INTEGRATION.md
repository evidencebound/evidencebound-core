# Integration Guide

## Existing Python workflow

Keep business/model code unchanged. At a boundary where an output becomes reusable or consequential:

1. convert supporting evidence into `EvidenceRecord` objects;
2. call `eb.checkpoint(...)` after the worker returns;
3. call `eb.verify(...)` before reuse/action;
4. persist the checkpoint + receipt through your application or a persistence provider if durable verification is required;
5. when evidence/policy/work fails, call `invalidate()` and recompute only the plan’s affected nodes;
6. require successful re-verification before a consequential recovered action.

The `run_guarded` helper demonstrates the thinnest callable adapter.

## Multi-agent systems

Use checkpoint IDs as dependency edges. EvidenceBound does not schedule agents. Your orchestrator owns execution; EvidenceBound owns deterministic dependency/trust calculations.

## Google ADK callbacks

`AdkCallbackAdapter` is intentionally dependency-free. The maintained compatibility lane currently pins and tests **`google-adk==2.7.0` on Python 3.13** using the real upstream `BaseAgent`, `Runner`, callback validator, event stream and `InMemorySessionService`. No Gemini model, Google Cloud credential or network model call is used by the acceptance scenario.

This is an exact tested compatibility statement, not a claim that every ADK release is supported. A future ADK upgrade must change the pinned compatibility lane explicitly and pass its end-to-end lifecycle acceptance before documentation can claim that version was tested.

Google ADK 2.7.0 requires the `after_agent_callback` parameter to be named exactly `callback_context`. Register `adapter.after_agent` directly, then supply an `evidence_factory` plus an `output_factory`; a practical pattern is to configure the ADK agent's `output_key` and have `output_factory` read that value from `callback_context.state`. The adapter returns `None` so it does not replace the agent response, and it stores the structured EvidenceBound result under `evidencebound.verification` in callback state.

### ADK lifecycle requirement: consume the run before trusting the result

EvidenceBound verification in an `after_agent_callback` is a lifecycle side effect. An integrating runner must let the ADK agent run reach callback completion before treating the agent result as verified. Application code must not regard an earlier/final-looking response event as EvidenceBound-approved merely because the response has already been observed.

For a consequential action, use the dependency-free application gate:

```python
from evidencebound.adapters.google_adk import adk_consequential_action_allowed

if not adk_consequential_action_allowed(session.state):
    # fail closed: do not perform the consequential side effect
    ...
```

The helper returns `True` only when callback state contains an explicit serialized EvidenceBound `action == "ALLOW"`. Missing, malformed, `REVIEW_REQUIRED`, or `BLOCK` state returns `False`.

The real ADK compatibility acceptance exercises both lifecycle paths:

1. **complete consumption** — the synthetic real ADK agent event stream is exhausted, the upstream after-agent callback runs, ADK emits/persists the callback state delta, and the application gate becomes allowed only after that state exists;
2. **early stop** — the consumer reads the first real ADK agent event and closes the async generator before callback completion; EvidenceBound verification remains absent and the consequential gate remains blocked.

This distinction is intentional. EvidenceBound does not infer approval from an ADK event, model result, or apparent agent completion. Upstream lifecycle breakage should be fixed in the thin adapter/compatibility seam, not by weakening deterministic EvidenceBound verification.

`google-adk` is installed only inside the compatibility CI lane. It is not an EvidenceBound runtime dependency or a Core import.

## Typing

The distribution ships a PEP 561 `py.typed` marker. Public annotations are therefore discoverable by type checkers when the built package is installed. Pre-1.0 API compatibility is not guaranteed; pin the EvidenceBound version for integrations that depend on exact public types.

## Persistence

Core exposes a provider-neutral `PersistenceStore`. Current `main` also includes the stdlib `evidencebound.providers.sqlite.SQLiteStore` reference implementation with atomic checkpoint/receipt/verification/replay bundles, deterministic graph reconstruction, durable replay semantics, schema-version fail-closed behavior, and receipt/result re-verification on reopen.

A stored row is not automatically trusted state. See [`PERSISTENCE.md`](PERSISTENCE.md) for crash/restart semantics and [`SIGNED_RECEIPTS.md`](SIGNED_RECEIPTS.md) when issuer authentication or stronger independent receipt anchoring is required.
