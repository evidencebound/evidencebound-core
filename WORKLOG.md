# Autonomous Worklog

## 2026-08-16

- Phase 0: reviewed current EvidenceBound public repositories and extraction boundaries; target OSS repository existed with only an initial README.
- Phase 1: locked deterministic stdlib-only core, no framework/cloud dependency, historical integrity separated from current applicability.
- v0.1 implementation: contracts, EBCJ-1, receipts, evidence/provenance/policy verification, fail-closed behavior.
- v0.2 implementation: DAG, exact blast radius, selective recovery, replay guard, structured events, plain/adaptor seams, consequential post-recovery gate.
- v0.3 implementation in progress: docs/spec/threat model/license rationale/benchmark/CI/package/release audit.
- First suite: 14 passed.
- Fail-closed hardening exposed a local ordering regression; repaired.
- Current suite after further adversarial/adapter hardening: 25 passed locally after editable install.
- Package wheel build initially failed because sandbox build isolation could not reach PyPI; rerun with installed local setuptools and `--no-build-isolation` succeeded.
- Fresh venv wheel install/import succeeded at local candidate version 0.3.0.
- Reproducible synthetic benchmark: 100-node linear graph invalidating node 75 produced 25 recompute / 75 reusable / 75 avoided recomputations in this scenario.
- Current official funding status checked: NLnet general proposals temporarily paused pending post-summer reopening; NGI0 Commons final call closed; Sovereign Tech Fund application route remains published; relevant Horizon 2026 digital call is closed.
- Google ADK seam corrected against current upstream callback contract: after_agent_callback receives only callback_context; adapter returns None and reads output via an application-provided extractor.
- Local release gates: 25 tests PASS; plain/golden examples PASS; benchmark PASS; compileall PASS; wheel build with no build isolation PASS; fresh venv wheel import PASS. Ruff/mypy remain unrun locally because binaries are absent; CI installs and runs them.
