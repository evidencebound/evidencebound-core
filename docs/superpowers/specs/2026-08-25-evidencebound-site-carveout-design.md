# EvidenceBound Public Site Carve-Out Design

Date: 2026-08-25

## Outcome

Make evidencebound.org the canonical public home for generic EvidenceBound research, maintainer identity, AI Safety assurance mappings and reusable trust architecture while preserving SignalReview as a separate sports product.

## Constraints

- Do not modify the submitted SignalReview repository or judge-facing production routes while OpenAI judging remains active.
- Do not claim certification, legal compliance, regulatory approval, universal safety or production customer adoption.
- Preserve historical EvidenceBound-MAS artifacts as archival evidence.
- SignalReview remains an applied reference implementation, not the canonical EvidenceBound identity home.

## Information architecture

- `/` — canonical EvidenceBound Human Control Plane and OSS Core narrative.
- `/assurance/` — NIST AI RMF, ISO/IEC 42001 and EU AI Act technical-evidence support mappings with explicit non-certification boundaries.
- `/research/` — canonical Research Atlas.
- `/research/deterministic-control-plane-for-ai-agents/`
- `/research/audit-evidence-for-high-stakes-ai/`
- `/research/verify-the-algorithm-not-the-outcome/`
- `/case-studies/signalreview/` — separate-product reference implementation.
- `/identity/ruslan-vrublevskyi.json` — machine-readable canonical maintainer identity.
- `/papers/` — historical paper index; PDF remains on frozen SignalReview asset until judge unlock.

## Claim model

EvidenceBound can claim implemented, tested, reproducible properties only where repository evidence supports them. Framework mappings describe potential technical evidence contributions, not compliance status.

## Migration boundary

EvidenceBound destination is created and verified first. SignalReview 301 redirects and removal of generic EvidenceBound pages happen only after the OpenAI repo freeze ends and current judging status is rechecked.
