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

## P0 acceptance gates

1. **Evidence binding — PASS**
   - material generated fields are bound to source evidence or derived only from bound fields;
   - source payloads are content-addressed;
   - an invented GenAI evidence reference is deterministically `BLOCKED`;
   - unsupported material assertions cannot receive VERIFIED status.

2. **Missing-data safety — PASS**
   - removed environment or kinematic evidence is not silently completed;
   - missing attributes remain explicit;
   - missing material kinematics requires `REVIEW_REQUIRED` rather than fabricated certainty.

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
   - both retained exports pass the official ASAM 1.4.0 XSD in dedicated CI.

6. **Catalog matching — PASS for controlled catalog**
   - generated scenarios are matched against a small versioned validation catalog;
   - top-k score and structured reasons are retained;
   - controlled Recall@1 and MRR are measured, not advertised as general automotive accuracy.

7. **Reproducibility — PASS**
   - same normalized inputs + same pinned extractor output + same policy produce byte-stable receipts;
   - model-generated content remains separately versioned;
   - retained benchmark JSON is compared exactly in pytest.

8. **Privacy/data-minimisation boundary — PASS for retained fixtures**
   - retained fixtures exclude demographics, medical/injury, alcohol/drug and other sensitive person-level categories;
   - only scenario-relevant evidence is retained;
   - this is described as data-minimisation by design, not blanket GDPR compliance.

## Measured retained benchmark

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

Retained benchmark receipt:

`90d21220e6cd1ca488fdb57e08b6cab0567821f5a6986ae246efbb56026f844a`

## Verified automation evidence

On head `9a14646645a7a9ee527612d35cb9fbdcc48d549e`:

- full repository CI `32036316364` — **PASS**;
- dedicated SPARK benchmark + judge demo + official ASAM 1.4.0 XSD `32036316372` — **PASS**.

## Submission gate

- [x] at least one public crash fixture runs end-to-end — two retained cases do;
- [x] missing-evidence adversarial acceptance passes fail-closed/review-required behavior;
- [x] evidence-change invalidation/recovery acceptance passes;
- [x] deterministic kinematic coherence acceptance passes;
- [x] README includes one-command reproduction;
- [x] measured baseline receipt is retained;
- [x] OpenSCENARIO XML 1.4.0 artifacts pass the official ASAM XSD in CI;
- [x] background/foreground IP boundary remains explicit;
- [ ] final application answers rechecked against the live F6S form immediately before submission;
- [ ] any Challenge Owner dataset/catalog access incorporated if provided before the final gate.

## Explicit non-claims / Advance gaps

The current prototype remains **TRL 3**. It does not claim:

- automotive production accuracy or homologation;
- simulator-level behavioral validity;
- generalization from two public cases to NHTSA CISS, GIDAS, CARE, STRADA or Challenge Owner data;
- live LLM/VLM extraction quality not yet measured on a representative labelled set;
- that the constant-speed kinematic gate is a vehicle-dynamics model.

Advance work should therefore prioritize Challenge Owner data/catalog integration, representative LLM/VLM extraction evaluation, stronger physical/kinematic constraints and simulator-level behavioral validation rather than inflating the current controlled-suite claims.
