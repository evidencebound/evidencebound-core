# Supply-chain evidence

EvidenceBound separates source/release truth from later CI hardening. The published GitHub source release `v0.3.0` points to commit `2477164acfbdca6a843bf7b2eac5fa21ce9901b2` and **predates this attestation workflow**. Do not describe that already-published release as retroactively attested by later `main` runs.

## Current workflow design

The CI workflow has two supply-chain layers.

### Pull requests and ordinary validation

The `supply-chain` job has only `contents: read`. It:

1. installs pinned `build==1.5.1` and `pip-audit==2.10.1` as CI tooling;
2. builds the sdist and wheel from the exact checkout;
3. writes SHA-256 checksums for only those two artifacts to `dist/SHA256SUMS`;
4. generates `dist/evidencebound-core.sbom.cdx.json` using pip-audit's CycloneDX JSON output;
5. validates artifact hashes, wheel name/version, absence of unconditional `Requires-Dist`, and the basic CycloneDX document shape with the stdlib-only `tools/validate_supply_chain.py`.

This PR-capable job has no OIDC or attestation write permission.

### Trusted `main` pushes

`attest-supply-chain` runs only when `github.event_name == 'push'` and `github.ref == 'refs/heads/main'`. It depends on the read-only validation job, then rebuilds the same exact commit in a separate trusted job and repeats checksum/SBOM validation before any attestation mutation.

Only this job receives:

- `id-token: write`;
- `attestations: write`;
- `artifact-metadata: write`;
- `contents: read`.

It uses the official `actions/attest` v4.2.2 code pinned by immutable commit SHA:

`1e69f48acb82d1966a394da916b4c1698aa569d6`

The job creates two attestations for the wheel and sdist subjects identified by `SHA256SUMS`:

1. default SLSA build provenance;
2. a CycloneDX SBOM attestation using the generated SBOM as predicate.

The workflow prints the exact artifact SHA-256 digests plus the returned provenance/SBOM attestation IDs and URLs. A later run is evidence only for the exact subjects/digests and workflow identity represented by that run.

## What the checksum manifest proves

A SHA-256 checksum lets a consumer test whether local artifact bytes match the named digest. The checksum text by itself does not authenticate who built or published those bytes. Its security value increases when the digest is independently anchored, for example by a verifiable GitHub artifact attestation.

## What build provenance proves

A successfully verified GitHub artifact attestation binds artifact subject name/digest to signed attestation metadata about the GitHub Actions build identity. Verification is about the artifact bytes and recorded build provenance; it does not establish that EvidenceBound's upstream evidence sources are truthful or that the software is free of every defect.

The workflow does **not** claim bit-for-bit reproducible builds across arbitrary machines. The sdist/wheel built in one job may contain build-environment-dependent metadata; each attestation refers to the exact digest subjects generated in its trusted job.

## What the SBOM represents

The SBOM is generated from the Python project runtime dependency graph with `pip-audit==2.10.1` in CycloneDX JSON format. EvidenceBound currently declares no unconditional third-party runtime dependencies; optional/development tooling is not a claim about core runtime requirements.

The validation script checks the SBOM's basic machine-readable structure. It does not claim full CycloneDX JSON-schema validation unless a future workflow adds an explicit schema validator.

An SBOM is inventory evidence, not proof that every dependency or source is non-malicious and not proof that no vulnerability exists. The separate security CI still runs `pip-audit` and Bandit as executable gates.

## Consumer verification

With the wheel/sdist and `SHA256SUMS` in the same directory, checksum verification can be performed with a platform SHA-256 utility, for example:

```bash
sha256sum -c SHA256SUMS
```

For a future attested artifact downloaded from a trusted build, GitHub CLI can verify that a local artifact digest has a matching attestation in this repository:

```bash
gh attestation verify evidencebound_core-0.3.0-py3-none-any.whl \
  --repo moneyparking/evidencebound-core
```

The verifier should also inspect which workflow/repository/ref identity produced the attestation and whether that identity matches the intended trust policy. Verification of an attestation does not replace EvidenceBound's own evidence/provenance/policy verification semantics.

## Release boundary

- `v0.3.0`: published before this workflow; no retroactive attestation claim.
- later `main` builds: may have attestations only when the exact `attest-supply-chain` run is confirmed successful.
- a future release: should be built/published through an explicit release workflow that preserves exact artifact digest and attestation linkage; that is separate from merely having attestations for development `main` builds.
