# EvidenceBound Public Site Carve-Out Implementation Plan

> Goal: make evidencebound.org the version-controlled canonical EvidenceBound site without touching the frozen SignalReview submission.

1. Add failing static-site contract tests for routes, canonical ownership, assurance boundaries, identity ownership, internal links and Vercel security headers.
2. Add a dependency-free static site under `site/` with canonical EvidenceBound research and assurance routes.
3. Add NIST AI RMF / ISO/IEC 42001 / EU AI Act support mappings using official sources and explicit non-certification boundaries.
4. Add a SignalReview case study that explicitly preserves separate-product and generic-IP ownership boundaries.
5. Add machine-readable maintainer identity whose canonical home and research library are evidencebound.org.
6. Run targeted static-site tests and full repository tests/lint/type checks where available.
7. Commit on a feature branch, open PR, run GitHub CI and merge only after required gates pass.
8. Production: link or deploy the existing Vercel `evidencebound` project from `evidencebound-core/site` if an authenticated supported write path exists. If not, report the exact owner-only linkage action; do not deploy the wrong project.
9. After OpenAI judging unlock: change SignalReview generic EvidenceBound routes into permanent redirects, move/copy historical PDF, make sports verification sports-first, and verify the buyer journey.
