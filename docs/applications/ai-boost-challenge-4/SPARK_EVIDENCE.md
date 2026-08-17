# EvidenceBound ScenarioGraph — SPARK Evidence Index

**AI-BOOST Challenge 4:** Generative AI for automatic test case generation from crash databases and standards  
**Stage:** TRL-3 controlled vertical slice with production-oriented safety controls  
**Draft PR:** https://github.com/moneyparking/evidencebound-core/pull/26

## Implemented vertical slice

```text
sanitized public crash evidence
        ↓
source-addressed Evidence Items
        ↓
Functional Scenario extraction contract
        ↓
evidence-bound typed scenario fields
        ↓
Logical Scenario enrichment + explicit uncertainty
        ↓
deterministic evidence + kinematic coherence gates
        ↓
VERIFIED / REVIEW_REQUIRED / BLOCKED
        ↓
validation-catalog matching
        ↓
exact changed-evidence detection
        ↓
dependency blast radius
        ↓
preserve / recompute selective recovery
        ↓
ASAM OpenSCENARIO XML 1.4 export
        ↓
official ASAM 1.4.0 XSD validation in CI
        ↓
content-addressed pipeline + benchmark receipts
```

The retained benchmark uses a deterministic coded-record extractor as an inspectable comparator. A strict `RecordedGenerativeExtractor` boundary is also implemented for schema-constrained LLM/VLM candidates: model-generated fields enter the same ScenarioGraph trust path, and invented evidence references are blocked by deterministic verification rather than accepted from model confidence.

## Public crash evidence

The benchmark uses sanitized scenario-only extracts from official U.S. NHTSA VICIS/CIREN Crash Viewer records:

1. **NHTSA-VICIS-991**  
   Source: https://crashviewer.nhtsa.dot.gov/crashviewer/CIREN/print?CaseId=991&Study=CIRENVICIS  
   Controlled label: `pedestrian_dart_out_visual_obstruction`

2. **NHTSA-VICIS-1027**  
   Source: https://crashviewer.nhtsa.dot.gov/crashviewer/CIREN/print?CaseId=1027&Study=CIRENVICIS  
   Controlled label: `pedestrian_crossing_vehicle_not_turning`

Fixtures intentionally exclude demographics, medical/injury, alcohol/drug and other sensitive person-level categories. Only scenario-relevant classification, movement, roadway, environment, visibility, vehicle and kinematic evidence is retained.

## Reproduce

```bash
git clone https://github.com/moneyparking/evidencebound-core.git
cd evidencebound-core
git checkout ai-boost-challenge-4
python -m pip install -e '.[dev]'
python benchmarks/ai_boost_challenge4/run.py --assert-targets
python examples/ai_boost_spark_demo.py
pytest
```

`benchmarks/ai_boost_challenge4/BASELINE.json` is compared exactly against a newly generated report in pytest, so benchmark drift requires an explicit baseline update.

## Measured SPARK baseline

Scope: **2 sanitized public NHTSA VICIS cases + 15 controlled mutations**, including **8 explicit kinematic-gate expectation cases**.

| Metric | Controlled-fixture result |
|---|---:|
| Evidence coverage for asserted material fields | 1000/1000 |
| Unsupported assertion rate | 0/1000 |
| Unknown fields with explicit uncertainty | 1000/1000 |
| Functional Scenario label accuracy | 1000/1000 |
| Controlled catalog Recall@1 | 1000/1000 |
| Controlled catalog MRR | 1000/1000 |
| Deterministic receipt reproduction | 1000/1000 |
| Mutation changed-evidence detection | 1000/1000 |
| Mutation selective-recovery precision | 1000/1000 |
| Mutation selective-recovery recall | 1000/1000 |
| Unrelated-field preservation | 1000/1000 |
| Missing-evidence no-completion behavior | 1000/1000 |
| Missing-evidence REVIEW_REQUIRED behavior | 1000/1000 |
| Baseline kinematic gate VERIFIED | 1000/1000 |
| Controlled kinematic decision expectation | 1000/1000 |
| Adversarial kinematic BLOCKED behavior | 1000/1000 |

**Retained benchmark receipt SHA-256:**

`90d21220e6cd1ca488fdb57e08b6cab0567821f5a6986ae246efbb56026f844a`

Baseline per-case pipeline receipts:

- NHTSA-VICIS-991: `8672e59dc46e692b38050244f9c050cd5183acfda957faca244e01b3484685f6`
- NHTSA-VICIS-1027: `51b1fdde901370df572739520234d6f14cb0f473052b9489cc07caff87a43a35`

## Deterministic kinematic coherence gate

Policy ID: `spark-kinematic-coherence/0.1`.

The gate compares the reported reveal time with the constant-speed traversal time implied by evidence-bound detection distance and pre-event speed, using integer-only arithmetic:

```text
expected_reveal_time_millis ≈ detection_distance_m × 3600 / vehicle_speed_kph
```

Prototype policy:

- deviation ≤ 250 milli: eligible for `VERIFIED`;
- deviation > 250 milli: `REVIEW_REQUIRED`;
- deviation > 500 milli: `BLOCKED`;
- non-positive required measurement: `BLOCKED`;
- missing required kinematic evidence: `REVIEW_REQUIRED`.

Clean retained cases are VERIFIED by this gate. Controlled mutations exercise coherent, review-zone, inconsistent/impossible and missing-kinematics states. A BLOCKED kinematic field propagates into the exported OpenSCENARIO verification marker rather than being hidden behind successful generation.

These thresholds are versioned SPARK engineering policy under a constant-speed approximation. They are **not** vehicle-dynamics limits, simulator validation, homologation criteria or a safety case.

## Fifteen controlled mutations

The suite covers:

1. case 991 visual-obstruction change;
2. case 991 speed increase with inconsistent reveal time → `BLOCKED`;
3. case 991 coherent speed + reveal-time change → `VERIFIED`;
4. case 991 reveal-time review zone → `REVIEW_REQUIRED`;
5. case 991 reveal-time collapse → `BLOCKED`;
6. case 991 maneuver change;
7. case 991 visibility evidence removal;
8. case 1027 day → night;
9. case 1027 clear → rain;
10. case 1027 dry → wet road surface;
11. case 1027 speed increase with inconsistent reveal time → `BLOCKED`;
12. case 1027 reveal-time inflation → `BLOCKED`;
13. case 1027 zero speed → `BLOCKED`;
14. case 1027 kinematics evidence removal → `REVIEW_REQUIRED`;
15. case 1027 environment evidence removal.

Each mutation compares source evidence hashes, detects the exact changed evidence block, computes its dependency blast radius and checks the observed `recompute_fields` and `preserve_fields` sets. For a `kinematics` change the exact recompute set is:

```text
detection_distance_m
kinematic_coherence
reveal_time_millis
vehicle_speed_kph
```

Unrelated Functional Scenario and visibility fields remain preserved.

## GenAI trust boundary

A recorded schema-constrained GenAI candidate can enter the same pipeline, but the model cannot grant itself trusted status. A controlled test gives a generated field an invented evidence ID; that field becomes `BLOCKED`, and its dependent `catalog_match_top1` is also `BLOCKED`.

```text
LLM / VLM candidate generation
        ↓
ScenarioGraph candidate state
        ↓
DETERMINISTIC EVIDENCE + CONSISTENCY GATES  ← trust decision here
        ↓
VERIFIED / REVIEW_REQUIRED / BLOCKED
        ↓
matching / recovery / export
```

## Data minimisation

Each fixture and pipeline receipt explicitly records excluded data categories:

```text
demographics
medical
injuries
alcohol
drugs
other_sensitive_person_data
```

This demonstrates data-minimisation by design and alignment with the data-minimisation principle; it is not presented as a blanket GDPR-compliance claim.

## ASAM OpenSCENARIO XML 1.4.0 acceptance

The dedicated GitHub Actions workflow generates both `.xosc` artifacts, downloads the official ASAM OpenSCENARIO XML 1.4.0 schema archive and validates each artifact with `xmllint --schema`. CI fails on schema violation.

Artifact marker:

`ASAM_OPENSCENARIO_XML_1_4_XSD_VALIDATED_IN_CI`

This establishes XML schema acceptance for the generated minimal documents. It does not imply simulator-behavior validation, automotive production safety, homologation or certification.

## CI evidence

For branch head `9a14646645a7a9ee527612d35cb9fbdcc48d549e`:

- full repository CI run `32036316364`: **PASS**;
- dedicated SPARK benchmark/XSD run `32036316372`: **PASS**;
- retained benchmark, judge-visible demo, generated `.xosc` files and official ASAM 1.4.0 XSD validation all pass on the same head.

## Claim boundary

The perfect controlled-suite milli metrics show only that the current TRL-3 vertical slice satisfies these selected fixtures and mutations. They do not establish generalization to NHTSA CISS, GIDAS, CARE, STRADA or Challenge Owner data. The kinematic gate is deliberately a deterministic sanity check, not a dynamics simulator. Broader LLM/VLM extraction quality, calibration, catalog matching on Challenge Owner data and simulator-level behavioral validation remain Advance-phase targets.
