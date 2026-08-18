# EvidenceBound ScenarioGraph — Independent External Validity Holdout

## Purpose

This evidence layer is deliberately separate from the retained two-case NHTSA VICIS SPARK baseline. It asks a different question:

> Can the ScenarioGraph evidence/trust boundary ingest a second official crash-data system with different coding and missingness rules, preserve source gaps instead of inventing completion, and reproduce the same normalized result deterministically?

It is **not** used to inflate the controlled NHTSA benchmark percentages and it is not presented as GenAI extraction accuracy.

## Independent source

**Dataset:** PSNI Northern Ireland Police Recorded Injury Road Traffic Collision Statistics 2024  
**Publisher:** Police Service of Northern Ireland via Open Data NI  
**Licence:** UK Open Government Licence (OGL)  
**Data model:** separate collision, vehicle and casualty resources linked through collision reference and, where present, vehicle identifiers  
**Data guide:** the publisher's 2024 Data Guide is used as the field-code and recording-policy authority.

The live CI job queries the public Open Data NI CKAN API. Raw source rows are not retained in this repository. Instead, the benchmark retains source resource IDs, row counts, full-recordset SHA-256 digests, aggregate metrics and a small data-minimised case summary.

## Live source observed by CI

| Resource | Live rows |
|---|---:|
| Collision records | 4,753 |
| Vehicle records | 8,822 |
| Casualty records | 7,494 |

Within the casualty table, **745** records are pedestrian or pedal-cyclist casualties. All **745/745** resolve to a collision record. Only **217/745** have a directly matching associated-vehicle row under the source identifiers used by the three resources.

That 217/745 value is retained as an observed source-integration property. It is **not** treated as a model failure and is not hidden by filtering records out.

## Deterministic holdout selection

The benchmark deterministically selects the first **64** vulnerable-road-user casualties after stable ordering by collision reference, vehicle ID and casualty ID.

Observed in that 64-case holdout:

- **51/64** lack a matching associated-vehicle row;
- **47/64** contain at least one field that the PSNI Data Guide says is conditionally not recorded for slight-injury collisions;
- missing associated-vehicle facts are retained as `unknown_missing_associated_vehicle_row`;
- conditionally unrecorded fields are retained as `not_recorded_for_slight_collision`;
- neither state is silently completed from model priors or neighboring records.

## Measured external-holdout results

| Metric | Result |
|---|---:|
| Collision-reference join | 100.0% |
| Associated-vehicle direct join | 29.1% — descriptive source property |
| Missing-vehicle explicit uncertainty | 100.0% |
| Provenance coverage for normalized material fields | 100.0% |
| Explicit uncertainty coverage | 100.0% |
| Direct harmonized-event mapping coverage | 43.7% — descriptive mapping coverage |
| Event mapping **or explicit uncertainty** | 100.0% |
| Deterministic reproduction | 100.0% |
| Unsupported assertion rate | 0.0% |
| Sensitive fields retained | 0.0% |

The 43.7% direct event-mapping figure is intentionally not rewritten as an accuracy percentage. A substantial part of the independent source is governed by publisher recording rules that leave some pedestrian/context fields unrecorded for slight-injury collisions. ScenarioGraph preserves that as uncertainty rather than turning absence into a positive scenario claim.

## Data minimisation boundary

The normalized holdout excludes exact source OSGR coordinates and the driver/casualty sex and age-group fields. The CI job additionally checks that those source field names do not appear in retained case summaries.

This demonstrates an engineering data-minimisation boundary for the public holdout. It is not a blanket GDPR-compliance claim.

## Retained evidence

Retained compact baseline:

`benchmarks/ai_boost_challenge4/EXTERNAL_HOLDOUT_NI_BASELINE.json`

Live external receipt SHA-256:

`274c4f68aa09aba4fdf51ac08435aa3ddfd8c558b27b621ab72c077e3c0ed153`

Source-recordset SHA-256 values retained in the baseline:

- collisions: `0011ab5b338d33675daa46ec32aba9cb3139815a60a6d1e0dfb08cd05e61464e`
- vehicles: `4aa9c33090e36a28487ff56117c57cdd933adb1caff3c1b6de0426a1317e0814`
- casualties: `94ff1f327d90545c9f0d1a5ccfb0d32131d137c32f05d559d7f7cff80676977e`

The dedicated GitHub Actions workflow re-fetches the public source and compares the live source hashes, counts, selected scope, metrics and receipt SHA with the retained baseline. Any source or mapping drift therefore fails the evidence gate until it is explicitly reviewed.

## What this proves

This independent holdout materially strengthens the SPARK evidence in four ways:

1. **Cross-source portability:** the evidence/trust contract is exercised on a second official crash-data system rather than another hand-shaped NHTSA fixture.
2. **Real missingness behavior:** missing joins and publisher-defined conditional fields are observed in live public data and remain explicit uncertainty.
3. **No denominator laundering:** incomplete records are not dropped merely to preserve perfect controlled-fixture scores.
4. **Reproducible external evidence:** the source recordsets and normalized receipt are content-addressed and regression-gated in CI.

## What this does not prove

This holdout does **not** establish:

- live LLM/VLM extraction accuracy;
- semantic correctness of every harmonized automotive taxonomy label;
- simulator-level behavioral validity;
- vehicle-dynamics fidelity;
- production automotive safety;
- homologation or certification;
- performance on Siemens/RobustifAI Challenge Owner data;
- generalization to CISS, GIDAS, CARE or STRADA.

The next evidence layer is a representative schema-constrained LLM/VLM extraction evaluation on independently held public cases, scored separately from the deterministic trust-gate metrics and accompanied by an explicit error taxonomy and uncertainty calibration.
