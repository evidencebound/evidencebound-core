# AI-BOOST Challenge 4 — ScenarioGraph SPARK benchmark

This benchmark is a deliberately small, reproducible vertical slice for the AI-BOOST Challenge 4 application. It demonstrates the proposed trust mechanics on public crash evidence; it is **not** a claim of automotive production accuracy.

## Public evidence sources

The retained fixtures are sanitized scenario-only extracts from official U.S. NHTSA VICIS/CIREN Crash Viewer pages:

- NHTSA VICIS Case 991: <https://crashviewer.nhtsa.dot.gov/crashviewer/CIREN/print?CaseId=991&Study=CIRENVICIS>
- NHTSA VICIS Case 1027: <https://crashviewer.nhtsa.dot.gov/crashviewer/CIREN/print?CaseId=1027&Study=CIRENVICIS>

The fixtures intentionally exclude demographics, injury/medical, alcohol/drug and other sensitive person-level fields. Only scenario geometry, classifications, movement, environment, visibility and kinematic evidence needed for the controlled technical benchmark are retained.

## Deterministic kinematic coherence gate

The SPARK pipeline now includes a versioned float-free kinematic sanity gate:

`spark-kinematic-coherence/0.1`

It compares reported reveal time with the constant-speed traversal time implied by reported detection distance and pre-event speed. The calculation is integer-only:

```text
expected_reveal_time_millis ≈ detection_distance_m × 3600 / vehicle_speed_kph
```

The prototype policy is explicit and versioned:

- deviation ≤ 250 milli → eligible for `VERIFIED`;
- deviation > 250 milli → `REVIEW_REQUIRED`;
- deviation > 500 milli or non-positive required measurements → `BLOCKED`.

These thresholds are SPARK engineering policy for controlled sanity testing, not automotive physical limits or homologation criteria. Missing kinematic evidence remains explicit and requires review.

The clean cases are accepted by the gate. Controlled coherent, review-zone, impossible/incoherent and missing-kinematics mutations exercise all three decisions: `VERIFIED`, `REVIEW_REQUIRED`, and `BLOCKED`.

## OpenSCENARIO acceptance

The export targets **ASAM OpenSCENARIO XML 1.4.0**. The dedicated `AI-BOOST Challenge 4 SPARK Benchmark` GitHub Actions workflow downloads the official ASAM 1.4.0 schema archive on every run and validates both generated `.xosc` files with `xmllint` against `OpenSCENARIO.xsd`.

Official specification:

- <https://openscenario.asam.net/ASAM_OpenSCENARIO_XML/v1.4.0/00_preface/01_introduction.html>

The current artifact records `ASAM_OPENSCENARIO_XML_1_4_XSD_VALIDATED_IN_CI`. This is schema conformance for the generated minimal SPARK documents; it is not simulator-behavior, homologation or certification validation.

## Reproduce

From an installed checkout:

```bash
python benchmarks/ai_boost_challenge4/run.py --assert-targets
python examples/ai_boost_spark_demo.py
python benchmarks/ai_boost_challenge4/export_xosc.py
```

The report uses integer `milli` ratios (`1000 == 100%`) so the retained quality receipt remains inside EvidenceBound's float-free deterministic canonicalization domain.

## What is measured

Scope: **2 public NHTSA cases + 15 controlled mutations**, including **8 explicit kinematic-gate expectation cases**.

- evidence coverage of asserted material fields;
- unsupported assertion rate;
- explicit uncertainty coverage for unknown fields;
- Functional Scenario label accuracy on the two labelled public fixtures;
- validation-catalog Recall@1 and MRR on the controlled catalog;
- deterministic receipt reproduction;
- exact changed-evidence detection;
- selective-recovery precision and recall;
- preservation of unrelated scenario fields;
- fail-closed behavior after deliberately removing required evidence;
- baseline kinematic-gate verification;
- exact expected kinematic decision on controlled mutations;
- adversarial kinematic BLOCKED behavior.

Controlled mutations now cover visibility change/removal, maneuver change, day-to-night, clear-to-rain, dry-to-wet, environment removal, coherent speed+time change, review-zone reveal time, inconsistent speed/time combinations, reveal-time collapse/inflation, zero speed and complete kinematics removal.

## Retained baseline

`BASELINE.json` is compared exactly against a newly generated report in pytest. Current retained benchmark receipt:

`90d21220e6cd1ca488fdb57e08b6cab0567821f5a6986ae246efbb56026f844a`

Clean-case pipeline receipts:

- NHTSA-VICIS-991: `8672e59dc46e692b38050244f9c050cd5183acfda957faca244e01b3484685f6`
- NHTSA-VICIS-1027: `51b1fdde901370df572739520234d6f14cb0f473052b9489cc07caff87a43a35`

## Claim boundary

Perfect controlled-suite results prove only that the SPARK vertical slice satisfies these selected fixtures and mutations. The kinematic gate is a deterministic sanity check under an explicit constant-speed approximation. It is **not** a simulator, vehicle-dynamics model, safety case, homologation result or evidence of generalization to NHTSA CISS, GIDAS, CARE, STRADA or Challenge Owner data. OpenSCENARIO XSD validation is separately demonstrated in CI against the official ASAM 1.4.0 schema.
