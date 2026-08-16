# Contributing

EvidenceBound prioritizes narrow deterministic contracts over framework-specific features.

## Local checks

```bash
python -m pip install -e '.[dev]'
pytest
ruff check .
mypy src/evidencebound
python -m build
python examples/golden_acceptance.py
```

Changes to canonicalization, receipt payloads, verification outcomes, graph ordering or public types require regression tests and an explicit compatibility note.

Do not submit secrets, production payloads, proprietary SignalReview logic, copied hackathon media, or framework dependencies into core. Framework integrations should remain optional adapters.

Potential contribution areas are tracked in `ROADMAP.md` and issue templates.
