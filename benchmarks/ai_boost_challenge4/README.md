# AI-BOOST Challenge 4 — ScenarioGraph SPARK benchmark

This benchmark is a deliberately small, reproducible vertical slice for the AI-BOOST Challenge 4 application. It demonstrates the proposed trust mechanics on public crash evidence; it is **not** a claim of automotive production accuracy.

## Public evidence sources

The retained fixtures are sanitized scenario-only extracts from official U.S. NHTSA VICIS/CIREN Crash Viewer pages:

- NHTSA VICIS Case 991: <https://crashviewer.nhtsa.dot.gov/crashviewer/CIREN/print?CaseId=991&Study=CIRENVICIS>
- NHTSA VICIS Case 1027: <https://crashviewer.nhtsa.dot.gov/crashviewer/CIREN/print?CaseId=1027&Study=CIRENVICIS>

The fixtures intentionally exclude demographics, injury/medical, alcohol/drug and other sensitive person-level fields. Only scenario geometry, classifications, movement, environment, visibility and kinematic evidence needed for the controlled technical benchmark are retained.

## OpenSCENARIO acceptance

The export targets **ASAM OpenSCENARIO XML 1.4.0**. The dedicated `AI-BOOST Challenge 4 SPARK Benchmark` GitHub Actions workflow downloads the official ASAM 1.4.0 schema archive on every run and validates both generated `.xosc` files with `xmllint` against `OpenSCENARIO.xsd`.

Official specification:

- <https://openscenario.asam.net/ASAM_OpenSCENARIO_XML/v1.4.0/00_preface/01_introduction.html>

The current artifact records `ASAM_OPENSCENARIO_XML_1_4_XSD_VALIDATED_IN_CI`. This is schema conformance for the generated minimal SPARK documents; it is not a simulator-behavior, homologation or certification claim.

## Reproduce

From an installed checkout:

```bash
python benchmarks/ai_boost_challenge4/run.py --assert-targets
python benchmarks/ai_boost_challenge4/export_xosc.py
```

The report uses integer `milli` ratios (`1000 == 100%`) so the retained quality receipt remains inside EvidenceBound's float-free deterministic canonicalization domain.

## What is measured

Scope: **2 public NHTSA cases + 9 controlled adversarial mutations**.

- evidence coverage of asserted material fields;
- unsupported assertion rate;
- explicit uncertainty coverage for unknown fields;
- Functional Scenario label accuracy on the two labelled public fixtures;
- validation-catalog Recall@1 and MRR on the controlled catalog;
- deterministic receipt reproduction;
- exact changed-evidence detection;
- selective-recovery precision and recall;
- preservation of unrelated scenario fields;
- fail-closed behavior after deliberately removing required evidence.

Controlled mutations cover visibility changes/removal, vehicle speed changes, maneuver change, day-to-night, clear-to-rain, dry-to-wet and environment-evidence removal.

## Retained baseline

`BASELINE.json` is compared exactly against a newly generated report in pytest. Current retained benchmark receipt:

`2358c4db90bf2314daeebfcb824df913f9195d33a83cdad8b9f1ea21fba20a5f`

## Claim boundary

Perfect results on two selected public cases and nine controlled mutations prove only that the SPARK vertical slice satisfies its retained fixtures. They do **not** establish generalization to NHTSA CISS, GIDAS, CARE, STRADA or Challenge Owner data, production safety performance, or regulatory/homologation compliance. OpenSCENARIO XSD validation is separately demonstrated in CI against the official ASAM 1.4.0 schema.
