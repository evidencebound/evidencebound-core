# EvidenceBound Control Center Authority

This document governs project-control operations. It does not grant product runtime authority and does
not supersede narrower release, deployment, production, competition, or human-approval rules.

## Allowed by default

Within the scoped task and normal repository permissions, an agent may inspect repository truth, read
public evidence, run tests, edit documentation, and make reversible feature-branch changes.

## Denied by default

Without separate applicable authority, the following remain denied:

- publication or release actions;
- production deployment;
- package or registry publication;
- external messages;
- spending or procurement;
- destructive or irreversible mutation.

The absence of required authority is `DENY`, not implicit consent. The absence of required evidence is
not interpreted as success.

## Precedence

Existing narrower project rules always outrank this generic Control Center permission layer. A field in
`control/CONTROL.yaml`, a model suggestion, chat history, or a knowledge delta cannot mint, widen, or
restore authority.

## Knowledge authority

Chat history, model memory, and generated prose are non-authoritative. Existing project artifacts remain
the canonical owners named by the selected route. A verified knowledge delta may support an update to
an authoritative source, but the delta itself does not silently replace that source.
