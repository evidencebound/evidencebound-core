# EvidenceBound ScenarioGraph — SPARK Evidence Index

**AI-BOOST Challenge 4:** Generative AI for automatic test case generation from crash databases and standards  
**Stage:** TRL-3 controlled vertical slice  
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
deterministic trust gate
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
pytest
```

Retained baseline:

`benchmarks/ai_boost_challenge4/BASELINE.json`

The pytest acceptance compares the generated benchmark report with the retained JSON object. Benchmark drift therefore requires an explicit baseline update.

## Measured SPARK baseline

Scope: **2 sanitized public NHTSA VICIS cases + 9 controlled adversarial mutations**.

| Metric | Controlled-fixture result |
|---|---:|
| Evidence coverage for asserted material fields | 100% |
| Unsupported assertion rate | 0% |
| Unknown fields with explicit uncertainty | 100% |
| Functional Scenario label accuracy | 100% |
| Controlled catalog Recall@1 | 100% |
| Controlled catalog MRR | 1.0 |
| Deterministic receipt reproduction | 100% |
| Mutation changed-evidence detection | 100% |
| Mutation selective-recovery precision | 100% |
| Mutation selective-recovery recall | 100% |
| Unrelated-field preservation | 100% |
| Missing-evidence no-completion behavior | 100% |
| Missing-evidence REVIEW_REQUIRED behavior | 100% |

**Retained benchmark receipt SHA-256:**

`2358c4db90bf2314daeebfcb824df913f9195d33a83cdad8b9f1ea21fba20a5f`

Baseline per-case pipeline receipts:

- NHTSA-VICIS-991: `a93271cfe140a42157d104f738017459bc21aaff23d9fa532a5c526b9dfda189`
- NHTSA-VICIS-1027: `e79e8d57c5b34b7c17a15c0edefe3ddefb044c2218ea52ce09d2baec93314874`

## Nine controlled mutations

The mutation suite covers:

1. visual obstruction change;
2. visibility evidence removal;
3. vehicle speed increase on case 991;
4. vehicle maneuver change;
5. day → night;
6. clear → rain;
7. dry → wet road surface;
8. vehicle speed increase on case 1027;
9. environment evidence removal.

Each mutation is evaluated by comparing source evidence hashes, detecting the exact changed evidence block, computing the expected dependency blast radius and comparing it with the observed `recompute_fields` set. Unrelated fields are checked for preservation.

Example: changing `visibility` in case 991 produces the exact recompute set:

```text
catalog_match_top1
obstruction_context
```

`functional_label` and `vehicle_speed_kph` remain in the preserve set.

## GenAI trust boundary

A recorded schema-constrained GenAI candidate can enter the same pipeline, but the model cannot grant itself trusted status. A controlled test gives a generated field an invented evidence ID; that field becomes `BLOCKED`, and its dependent `catalog_match_top1` is also `BLOCKED`.

This is the intended production-oriented boundary:

```text
LLM / VLM candidate generation
        ↓
ScenarioGraph candidate state
        ↓
DETERMINISTIC EVIDENCE GATE  ← trust decision here
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

This demonstrates data-minimisation by design. It is not presented as a blanket GDPR-compliance claim.

## ASAM OpenSCENARIO XML 1.4.0 acceptance

The dedicated GitHub Actions workflow:

1. generates `.xosc` artifacts for both baseline cases;
2. downloads the official ASAM OpenSCENARIO XML 1.4.0 schema archive;
3. extracts `OpenSCENARIO.xsd`;
4. validates each generated `.xosc` with `xmllint --schema`;
5. fails CI on schema violation.

Both retained SPARK exports pass the official XSD gate. Artifact marker:

`ASAM_OPENSCENARIO_XML_1_4_XSD_VALIDATED_IN_CI`

This establishes XML schema acceptance for the generated minimal documents. It does not imply simulator-behavior validation, automotive production safety, homologation or certification.

## Claim boundary

The perfect controlled-fixture percentages are deliberately scoped. They show that the current TRL-3 SPARK vertical slice behaves correctly on **2 selected public cases + 9 controlled mutations**. They do not establish generalization to NHTSA CISS, GIDAS, CARE, STRADA or Challenge Owner data. Broader extraction/enrichment quality, calibration and catalog matching remain Advance-phase evaluation targets.
