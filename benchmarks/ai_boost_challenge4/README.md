# AI-BOOST Challenge 4 — ScenarioGraph SPARK benchmark

This benchmark is a deliberately small, reproducible vertical slice for the AI-BOOST Challenge 4 application. It demonstrates the proposed trust mechanics on public crash evidence; it is **not** a claim of automotive production accuracy.

## Public evidence sources

The retained fixtures are sanitized scenario-only extracts from official U.S. NHTSA VICIS/CIREN Crash Viewer pages:

- NHTSA VICIS Case 991: <https://crashviewer.nhtsa.dot.gov/crashviewer/CIREN/print?CaseId=991&Study=CIRENVICIS>
- NHTSA VICIS Case 1027: <https://crashviewer.nhtsa.dot.gov/crashviewer/CIREN/print?CaseId=1027&Study=CIRENVICIS>

The fixtures intentionally exclude demographics, injury/medical, alcohol/drug and other sensitive person-level fields. Only scenario geometry, classifications, movement, environment, visibility and kinematic evidence needed for the controlled technical benchmark are retained.

## OpenSCENARIO target

The export seam targets the current **ASAM OpenSCENARIO XML 1.4** structural vocabulary:

- specification: <https://publications.pages.asam.net/standards/ASAM_OpenSCENARIO/ASAM_OpenSCENARIO_XML/v1.4.0/index.html>

The current artifact is explicitly marked `STRUCTURAL_SEAM_NOT_XSD_VALIDATED`. Full XSD validation is a later acceptance gate and must not be inferred from this SPARK benchmark.

## Reproduce

From an installed checkout:

```bash
python benchmarks/ai_boost_challenge4/run.py --assert-targets
```

The report uses integer `milli` ratios (`1000 == 100%`) so the retained quality receipt remains inside EvidenceBound's float-free deterministic canonicalization domain.

## What is measured

- evidence coverage of asserted material fields;
- unsupported assertion rate;
- explicit uncertainty coverage for unknown fields;
- Functional Scenario label accuracy on the two labelled public fixtures;
- validation-catalog Recall@1 and MRR on the controlled catalog;
- deterministic receipt reproduction;
- exact invalidation precision/recall for a controlled evidence change;
- fail-closed behavior after deliberately removing environment evidence.

## Claim boundary

A perfect result on two selected public cases and controlled mutations proves only that the SPARK vertical slice satisfies its retained fixtures. It does **not** establish generalization to NHTSA CISS, GIDAS, CARE, STRADA or Challenge Owner data, production safety performance, regulatory/homologation compliance, or complete ASAM OpenSCENARIO conformance.
