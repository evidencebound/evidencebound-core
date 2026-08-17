# Funding Readiness

Canonical repository: https://github.com/moneyparking/evidencebound-core  
Institutional site: https://evidencebound.org  
Maintainer/contact: Ruslan Vrublevskyi — ruslan@evidencebound.org

## Public-good value

EvidenceBound targets a reusable gap between agent memory/tracing and consequential action: deterministic evidence/provenance/policy binding, explicit applicability, exact dependency invalidation, and fail-closed selective recovery without requiring one model, cloud or agent framework.

## Existing engineering evidence

The project has a public, independently verified GitHub source release: `v0.3.0`, tagged at exact accepted commit `2477164acfbdca6a843bf7b2eac5fa21ce9901b2`. That release source passed Python 3.10–3.13 CI, golden acceptance, clean-room installation, package/type checks, the scenario-specific recovery benchmark, pip-audit and Bandit before publication.

Post-release Unreleased `main` has additional executable evidence that is **not** retroactively attributed to `v0.3.0`:

- provider-neutral signed-receipt contracts plus optional Ed25519 reference provider; issue #7 accepted on exact-main CI;
- provider-neutral persistence contract plus crash-consistent stdlib SQLite/restart/replay reference implementation; issue #8 accepted on exact-main CI;
- real credential-free `google-adk==2.7.0` lifecycle compatibility CI, including fail-closed early stream termination; issue #9 accepted on exact-main CI;
- versioned EBCJ-1 language-neutral conformance vectors and deterministic property-based trust/graph invariants; issue #17 accepted on exact-main CI;
- CI-generated sdist/wheel SHA-256 manifest and CycloneDX SBOM plus trusted-main GitHub/Sigstore SLSA provenance and SBOM attestations; issue #19 accepted at `main` `f6f46d4f21d6fcb2dc53cfeb0ebe70a742a34d9c`, exact-main run `31995557238` SUCCESS.

Only executable/public artifacts, exact commits/runs, published source releases and independently inspectable integration evidence should be cited as technical evidence. Reference hackathon/application repositories demonstrate prior exploration but are not evidence of independent external adoption.

## Missing maturity

- independently verified external adopter/integration outside maintainer-owned projects;
- explicit future release-artifact workflow tying release tag, artifact digests and attestations together;
- formal state-machine specification/model checking beyond generated property tests;
- a second independent runtime implementation consuming the EBCJ-1 conformance corpus;
- additional maintained framework integrations only where external demand justifies maintenance;
- external security review;
- independent benchmark/security review;
- stronger long-term governance/maintainer continuity evidence.

## Completed formerly-fundable gaps

The following should no longer be presented as wholly unimplemented work:

- signed receipt/key-provider protocol architecture;
- crash-consistent SQLite reference persistence and restart recovery;
- real Google ADK lifecycle compatibility lane;
- EBCJ-1 conformance corpus and property-based invariant suite;
- development-main SBOM/checksum/build-provenance attestation pipeline.

Future funding proposals may still fund audits, additional providers/adapters, formalization, migration tooling, independent implementations and release-system hardening around these foundations.

## Current fundable work packages

### Small — External integration and conformance adoption
**Problem:** the core is executable and documented, but independent utility is not yet demonstrated by a project outside the maintainer’s own portfolio.  
**Deliverables:** clean-room external-consumer fixture, integration conformance harness, one or more independently owned pilot integrations where available, issue-driven adapter feedback.  
**Acceptance:** public reproducible consumer install from built/released artifact, public integration notes, externally attributable evidence only when actually obtained.  
**Risk:** a maintainer-authored fixture is not external adoption; keep that distinction explicit.

### Medium — Security and release hardening
**Problem:** trusted-main attestations exist, but the published v0.3.0 source release predates artifact attestation and no external audit has occurred.  
**Deliverables:** future release workflow with exact tag/artifact/attestation linkage, external security review, remediation tracking, persistence/provider conformance, migration tests and release verification guide.  
**Acceptance:** a future release has independently verifiable artifact digests/attestations and audit findings are resolved or documented.  
**Risk:** do not retrofit later attestations to historical release claims.

### Large — Multi-runtime verifiable agent-state infrastructure
**Problem:** Python-only implementation limits ecosystem-level interoperability evidence.  
**Deliverables:** language-neutral specification hardening, independent second runtime, cross-runtime receipt/checkpoint fixtures, formal invalidation/recovery model, external audits and sustained governance.  
**Acceptance:** conformance matrix across independently implemented runtimes plus public integration evidence.  
**Risk:** avoid standardization ahead of real integration feedback.

## Application timing

Public source release, signed-receipt architecture, crash-consistent persistence, real ADK compatibility, conformance/property testing and trusted-main supply-chain attestations are now concrete engineering evidence. The largest remaining credibility gap for stronger OSS funding applications is **independent external integration/adoption**, followed by external security review and future release-artifact provenance. Funding target status and eligibility must still be rechecked from official program sources at application time.
