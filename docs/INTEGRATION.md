# Integration Guide

## Existing Python workflow

Keep business/model code unchanged. At a boundary where an output becomes reusable or consequential:

1. convert supporting evidence into `EvidenceRecord` objects;
2. call `eb.checkpoint(...)` after the worker returns;
3. call `eb.verify(...)` before reuse/action;
4. persist the checkpoint + receipt in your application if durable verification is required;
5. when evidence/policy/work fails, call `invalidate()` and recompute only the plan’s affected nodes;
6. require successful re-verification before a consequential recovered action.

The `run_guarded` helper demonstrates the thinnest callable adapter.

## Multi-agent systems

Use checkpoint IDs as dependency edges. EvidenceBound does not schedule agents. Your orchestrator owns execution; EvidenceBound owns deterministic dependency/trust calculations.

## Google ADK-style callbacks

`AdkCallbackAdapter` is intentionally dependency-free and matches the current ADK `after_agent_callback(callback_context)` shape. Register `adapter.after_agent` directly, then supply an `evidence_factory` plus an `output_factory`; a practical pattern is to configure the ADK agent's `output_key` and have `output_factory` read that value from `callback_context.state`. The adapter returns `None` so it does not replace the agent response, and it stores the structured EvidenceBound result under `evidencebound.verification` in callback state.

### ADK lifecycle requirement: consume the run before trusting the result

EvidenceBound verification in an `after_agent_callback` is a lifecycle side effect. An integrating runner must let the ADK agent run reach callback completion before treating the agent result as verified. In particular, application code must not regard an earlier/final-looking response event as EvidenceBound-approved merely because the model response has already been observed.

For a consequential action, use this fail-closed rule:

1. run the ADK invocation to callback completion;
2. require `callback_context.state["evidencebound.verification"]` (or the adapter's `last_verification`) to exist;
3. require its action to be `ALLOW` before the application action proceeds;
4. if the callback did not run, verification state is missing, or the event consumer stopped early, treat the action as blocked/unverified rather than inferring success from the model response.

The upstream ADK lifecycle can evolve. Pin and test the ADK version in the integrating application, and include an end-to-end regression that proves the callback executes under the application's actual event-consumption pattern. EvidenceBound's stable boundary is the structured checkpoint/verification contract, not an upstream framework callback object.

## Typing

The distribution ships a PEP 561 `py.typed` marker. Public annotations are therefore discoverable by type checkers when the built package is installed. Pre-1.0 API compatibility is not guaranteed; pin the EvidenceBound version for integrations that depend on exact public types.

## Persistence

Current core objects are JSON-serializable through `to_dict()` methods, but the alpha does not ship a storage backend. Persist receipts separately/immutably enough for your threat model; storing checkpoint and receipt in one attacker-controlled row does not create meaningful tamper resistance.
