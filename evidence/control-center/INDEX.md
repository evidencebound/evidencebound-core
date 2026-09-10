# EvidenceBound Control Center Evidence Index

This directory stores durable evidence about Control Center sessions and bootstrap decisions. It does
not replace the existing canonical owners named in `control/CONTROL.yaml`.

## Knowledge deltas

Machine-readable session deltas live in `evidence/control-center/knowledge_deltas/` and validate against
`control/knowledge_delta.schema.json`.

A delta records what was observed, corrected, decided, attempted, and verified. Promotion into project
truth requires a corresponding verified update to the authoritative owner.

## Public boundary

Artifacts here are public. They may contain only public-safe repository facts and generic references to
a `private benchmark workspace`. Do not place identifying private repository locations, hidden
evaluation material, credentials, private commercialization evidence, or other protected internals here.

## Verification

Run:

```bash
python tools/validate_control_center.py
python -m pytest -q tests/test_control_center_contract.py
```
