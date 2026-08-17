# EvidenceBound ScenarioGraph — SPARK Prototype Acceptance

## Purpose

Build a narrow, reproducible Challenge 4 vertical slice before F6S submission. The prototype must prove the proposed trust mechanism on public/synthetic crash evidence; it must not pretend to solve the complete automotive benchmark before Challenge Owner data access.

## Judge journey

```text
public crash record / standards excerpt
        ↓
source-addressed Evidence Pack
        ↓
schema-constrained Functional Scenario extraction
        ↓
evidence-linked ScenarioGraph fields
        ↓
Logical Scenario enrichment + explicit uncertainty
        ↓
deterministic provenance / consistency gate
        ↓
reference-scenario matching
        ↓
VERIFIED | REVIEW_REQUIRED | BLOCKED
        ↓
reproducible scenario receipt
```

## P0 acceptance gates

1. **Evidence binding**
   - every material generated field contains one or more source IDs, or an explicit `unsupported` / `unknown` state;
   - source payloads are content-addressed;
   - no unreferenced material field may receive VERIFIED status.

2. **Missing-data safety**
   - a fixture with intentionally removed weather/road/context evidence must not cause fabricated completion;
   - missing material attributes produce explicit uncertainty and `REVIEW_REQUIRED` or `BLOCKED` according to policy.

3. **Conflicting evidence**
   - conflicting source values are retained rather than silently collapsed;
   - the field records conflict provenance and cannot be VERIFIED until policy resolves the conflict.

4. **Dependency invalidation**
   - change one source evidence item;
   - compute exact affected ScenarioGraph descendants;
   - unaffected nodes remain reusable only after applicability checks;
   - affected nodes are selectively regenerated/revalidated.

5. **Scenario structure**
   - output a typed Functional Scenario and Logical Scenario representation;
   - include actors, road/context, maneuver/event relationships and parameter ranges where evidence permits;
   - support an initial OpenSCENARIO-compatible export seam without claiming full standard coverage.

6. **Catalog matching**
   - match the generated scenario against a small versioned reference catalog;
   - retain top-k scores plus structured reasons/evidence links;
   - expose unmatched/coverage-gap state explicitly.

7. **Reproducibility**
   - same normalized inputs + same model fixture/pinned output + same policy produce byte-stable deterministic validation receipt;
   - runtime/model-generated content is separately versioned so probabilistic generation is never misrepresented as deterministic.

8. **Privacy boundary**
   - public prototype uses non-sensitive/public or synthetic fixture data;
   - no PII is transmitted to model APIs;
   - external model/provider use is declared in generated metadata.

## Initial benchmark metrics

Report measured values only after running the benchmark:

- evidence coverage: material fields with explicit evidence refs / all material generated fields;
- unsupported assertion rate;
- explicit uncertainty coverage for incomplete/conflicting fields;
- Functional Scenario taxonomy precision/recall/F1 on labelled fixture;
- Logical Scenario attribute completeness/correctness;
- scenario matching Recall@K and MRR;
- evidence-change invalidation precision/recall;
- deterministic receipt reproduction rate;
- runtime, model calls/tokens where available, and cost per record / 1,000 records.

## Submission gate

Do not submit the F6S concept note until:

- [ ] at least one public/synthetic crash fixture runs end-to-end;
- [ ] missing-evidence adversarial fixture passes fail-closed acceptance;
- [ ] evidence-change invalidation/recovery fixture passes;
- [ ] README includes one-command reproduction;
- [ ] measured baseline receipt is retained and linked from the application;
- [ ] application answers are rechecked against the live F6S form;
- [ ] background/foreground IP boundary remains explicit.
