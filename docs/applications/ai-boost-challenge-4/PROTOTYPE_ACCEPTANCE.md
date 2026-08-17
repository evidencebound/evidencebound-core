# EvidenceBound ScenarioGraph — SPARK Prototype Acceptance

## Purpose

Maintain a narrow, reproducible Challenge 4 vertical slice that proves the proposed trust mechanism on public crash evidence without pretending to solve the complete automotive benchmark before Challenge Owner data access.

## Current judge journey

```text
public crash record / standards evidence
        ↓
source-addressed Evidence Pack
        ↓
schema-constrained Functional Scenario extraction
        ↓
evidence-linked ScenarioGraph fields
        ↓
Logical Scenario enrichment + explicit uncertainty
        ↓
deterministic evidence + kinematic coherence gates
        ↓
VERIFIED | REVIEW_REQUIRED | BLOCKED
        ↓
reference-scenario matching
        ↓
exact dependency blast radius
        ↓
preserve / recompute selective recovery
        ↓
OpenSCENARIO XML 1.4 export + official XSD validation
        ↓
reproducible content-addressed receipts
```

A second independent path now exercises the evidence/uncertainty boundary against live PSNI Northern Ireland 2024 public crash data rather than another hand-shaped NHTSA fixture.

## P0 acceptance gates

1. **Evidence binding — PASS**
   - material generated fields are bound to source evidence or derived only from bound fields;
   - source payloads are content-addressed;
   - an invented GenAI evidence reference is deterministically `BLOCKED`;
   - unsupported material assertions cannot receive VERIFIED status.

2. **Missing-data safety — PASS**
   - removed environment or kinematic evidence is not silently completed;
   - missing attributes remain explicit;
   - missing material kinematics requires `REVIEW_REQUIRED` rather than fabricated certainty;
   - independent PSNI records with no associated-vehicle row are retained with explicit `unknown_missing_associated_vehicle_row` state rather than dropped.

3. **Deterministic consistency gate — PASS**
   - policy `spark-kinematic-coherence/0.1` uses integer-only constant-speed traversal sanity checking;
   - controlled coherent data can remain `VERIFIED`;
   - review-zone inconsistency becomes `REVIEW_REQUIRED`;
   - strong inconsistency and non-positive required measurements become `BLOCKED`;
   - a BLOCKED gate propagates to the export verification marker.

4. **Dependency invalidation — PASS**
   - source evidence changes are detected by content hash;
   - exact transitive affected ScenarioGraph descendants are computed;
   - unrelated nodes remain in the preserve set;
   - affected nodes are selectively recomputed/revalidated.

5. **Scenario structure — PASS for SPARK scope**
   - typed Functional and Logical Scenario fields are produced from retained evidence;
   - actors/context, movement, roadway, environment, visibility and kinematic fields are represented where evidence permits;
   - minimal ASAM OpenSCENARIO XML 1.4.0 documents are generated;
   - retained exports pass the official ASAM 1.4.0 XSD in dedicated CI.

6. **Catalog matching — PASS for controlled catalog**
   - generated scenarios are matched against a small versioned validation catalog;
   - top-k score and structured reasons are retained;
   - controlled Recall@1 and MRR are measured, not advertised as general automotive accuracy.

7. **Reproducibility — PASS**
   - same normalized inputs + same pinned extractor output + same policy produce byte-stable receipts;
   - model-generated content remains separately versioned;
   - retained NHTSA benchmark JSON is compared exactly in pytest;
   - the live PSNI holdout is re-fetched and compared against a separately retained compact external baseline, including source hashes, counts, scope, metrics and receipt SHA.

8. **Privacy/data-minimisation boundary — PASS for current public evidence**
   - retained NHTSA fixtures exclude demographics, medical/injury, alcohol/drug and other sensitive person-level categories;
   - the PSNI normalized holdout excludes exact OSGR coordinates plus driver/casualty sex and age-group source fields;
   - raw PSNI rows are not retained in the repository;
   - this is described as an engineering data-minimisation boundary, not blanket GDPR compliance.

9. **Independent source portability / external holdout — PASS for ingestion and uncertainty scope**
   - official PSNI Northern Ireland 2024 collision, vehicle and casualty resources are fetched live from Open Data NI under OGL;
   - 745 pedestrian/pedal-cyclist casualties are observed and all 745 resolve to collision records;
   - only 217/745 have a direct associated-vehicle row, and that source gap is reported rather than hidden;
   - the deterministic 64-case holdout contains 51 missing associated-vehicle rows and 47 source-policy missingness cases;
   - provenance coverage, explicit uncertainty coverage, event mapping-or-uncertainty and deterministic reproduction are all `1000/1000`;
   - unsupported assertion rate and retained sensitive-field rate are `0/1000`.

## Measured retained controlled benchmark

Scope: **2 public NHTSA VICIS cases + 15 controlled mutations**, including **8 explicit kinematic-gate expectation cases**.

Measured controlled-suite results:

- evidence coverage: `1000/1000`;
- unsupported assertion rate: `0/1000`;
- explicit uncertainty for unknown fields: `1000/1000`;
- Functional Scenario label accuracy: `1000/1000`;
- controlled catalog Recall@1: `1000/1000`;
- controlled catalog MRR: `1000/1000`;
- deterministic receipt reproduction: `1000/1000`;
- exact changed-evidence detection: `1000/1000`;
- selective-recovery precision: `1000/1000`;
- selective-recovery recall: `1000/1000`;
- unrelated-field preservation: `1000/1000`;
- missing-evidence no-completion: `1000/1000`;
- missing-evidence review behavior: `1000/1000`;
- clean-case kinematic verification: `1000/1000`;
- expected kinematic decision across controlled expectation cases: `1000/1000`;
- expected adversarial kinematic BLOCKED behavior: `1000/1000`.

Retained controlled benchmark receipt:

`90d21220e6cd1ca488fdb57e08b6cab0567821f5a6986ae246efbb56026f844a`

## Independent external holdout

Source: **PSNI Northern Ireland Police Recorded Injury RTC 2024**, independently published via Open Data NI.

Live source population observed by the retained evidence run:

- collision records: `4753`;
- vehicle records: `8822`;
- casualty records: `7494`;
- pedestrian/pedal-cyclist casualties: `745`;
- collision-reference joins: `745/745`;
- associated-vehicle direct joins: `217/745`.

Deterministic holdout scope: `64` vulnerable-road-user casualties.

- missing associated-vehicle rows: `51/64`;
- publisher-policy conditional missingness cases: `47/64`;
- collision-reference join: `1000/1000`;
- associated-vehicle direct join: `291/1000` — descriptive source property, not an accuracy target;
- missing-vehicle explicit uncertainty: `1000/1000`;
- provenance coverage: `1000/1000`;
- explicit uncertainty coverage: `1000/1000`;
- direct harmonized-event mapping coverage: `437/1000` — descriptive mapping coverage, not a general accuracy claim;
- event mapping or explicit uncertainty: `1000/1000`;
- deterministic reproduction: `1000/1000`;
- unsupported assertion rate: `0/1000`;
- sensitive fields retained: `0/1000`.

Retained external receipt SHA-256:

`274c4f68aa09aba4fdf51ac08435aa3ddfd8c558b27b621ab72c077e3c0ed153`

Supporting evidence:

- `docs/applications/ai-boost-challenge-4/EXTERNAL_VALIDITY.md`
- `benchmarks/ai_boost_challenge4/EXTERNAL_HOLDOUT_NI_BASELINE.json`
- `.github/workflows/ai-boost-external-holdout.yml`

## Verified automation evidence

Controlled SPARK baseline:

- full repository CI `32036751642` — **PASS**;
- dedicated SPARK benchmark + judge demo + official ASAM 1.4.0 XSD `32036751650` — **PASS**.

Independent external holdout evolution:

- full repository CI on external-adapter head `658cc9afbc2ba43819794c55563e165ba6e18d69`, run `32043796319` — **PASS**;
- live PSNI holdout + retained-baseline comparison, run `32043929224` — **PASS**.

## Submission gate

- [x] at least one public crash fixture runs end-to-end — two retained NHTSA cases do;
- [x] missing-evidence adversarial acceptance passes fail-closed/review-required behavior;
- [x] evidence-change invalidation/recovery acceptance passes;
- [x] deterministic kinematic coherence acceptance passes;
- [x] README includes one-command reproduction;
- [x] measured controlled baseline receipt is retained;
- [x] OpenSCENARIO XML 1.4.0 artifacts pass the official ASAM XSD in CI;
- [x] independent official public-data holdout runs against a second crash-data system;
- [x] real source join gaps and source-policy missingness remain explicit uncertainty rather than being filtered or fabricated;
- [x] independent live source hashes/counts/metrics are regression-gated against a retained external baseline;
- [x] background/foreground IP boundary remains explicit;
- [ ] representative live schema-constrained LLM/VLM extraction quality measured separately from trust-gate performance;
- [ ] final application answers rechecked against the live F6S form immediately before submission;
- [ ] any Challenge Owner dataset/catalog access incorporated if provided before the final gate.

## Explicit non-claims / next evidence gap

The current prototype remains **TRL 3**. It does not claim:

- automotive production accuracy or homologation;
- simulator-level behavioral validity;
- generalization to NHTSA CISS, GIDAS, CARE, STRADA or Challenge Owner data;
- live LLM/VLM extraction quality not yet measured on a representative labelled set;
- that the constant-speed kinematic gate is a vehicle-dynamics model.

The next evidence layer should measure representative schema-constrained LLM/VLM extraction on independently held public cases, with model errors, abstentions/uncertainty and trust-gate outcomes reported separately. Challenge Owner data/catalog integration and simulator-level behavioral validation remain Advance-phase targets.
