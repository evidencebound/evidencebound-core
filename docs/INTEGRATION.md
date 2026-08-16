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

Framework callback signatures can evolve, so pin and test the ADK version in the integrating application. EvidenceBound's stable boundary is the structured checkpoint/verification contract, not an upstream framework callback object.

## Persistence

Current core objects are JSON-serializable through `to_dict()` methods, but the alpha does not ship a storage backend. Persist receipts separately/immutably enough for your threat model; storing checkpoint and receipt in one attacker-controlled row does not create meaningful tamper resistance.
