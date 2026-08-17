# Release Checklist

Canonical repository: https://github.com/moneyparking/evidencebound-core

Use this checklist for every EvidenceBound Core release. Exact-head evidence is required; a previously green commit does not validate a later release commit.

## Source and semantics

- [ ] Resolve the exact `main` SHA intended for release from `moneyparking/evidencebound-core`.
- [ ] Confirm version in `pyproject.toml` and `src/evidencebound/__init__.py` match.
- [ ] Confirm `CHANGELOG.md` accurately describes implemented behavior.
- [ ] Confirm `SPEC.md`, `THREAT_MODEL.md`, README and public API agree with executable semantics.
- [ ] Confirm no unsupported security/authenticity/immutability/exactly-once claims were introduced.
- [ ] Confirm package metadata, README badges, citation/security/funding docs and other GitHub links use the canonical repository slug.

## Executable gates

- [ ] Python 3.10–3.13 matrix green.
- [ ] pytest green at exact head.
- [ ] golden external acceptance green.
- [ ] exact selective-recovery benchmark assertions green.
- [ ] Ruff green.
- [ ] strict mypy green.
- [ ] sdist and wheel build green without known package-metadata deprecation warnings.
- [ ] wheel reinstall/import green.
- [ ] clean-room fresh checkout/venv/runtime-only install green.
- [ ] plain Python example green inside clean-room environment.
- [ ] clean-room golden acceptance green.
- [ ] no unconditional runtime dependencies declared.
- [ ] pip-audit green.
- [ ] Bandit core-source scan green.

## Publication/security audit

- [ ] Secret/private-key/provider-payload scan reviewed.
- [ ] No SignalReview commercial logic or unrelated proprietary code entered the repo.
- [ ] License and pre-existing-work boundary reviewed.
- [ ] GitHub Actions remain pinned by exact SHA.
- [ ] Dependency/license changes reviewed.

## Tag and release

- [ ] Create annotated/lightweight tag `vX.Y.Z` at the exact accepted `main` SHA.
- [ ] Fetch the tag and prove it resolves to that SHA.
- [ ] Create GitHub Release from that tag.
- [ ] Fetch the release and verify public visibility, tag, title and notes.
- [ ] Only then move the changelog entry from `Unreleased` to a release date if that change is part of the release process; if it creates a new commit, repeat exact-head/tag consistency checks.

## Optional package registry publication

- [ ] Verify package namespace/account ownership before PyPI upload.
- [ ] Build artifacts from the exact release source.
- [ ] Verify artifact metadata and hashes.
- [ ] Upload using a scoped trusted-publishing/token path.
- [ ] Install from PyPI in a fresh environment and run the golden acceptance.

PyPI publication is not required to truthfully describe a GitHub source release, and a GitHub source release must not be described as PyPI-published unless registry acceptance is independently verified.
