# Security Policy

Canonical repository: https://github.com/moneyparking/evidencebound-core

## Supported versions

Until a first stable release, only the latest published alpha line is supported for security fixes.

## Reporting a vulnerability

Use the repository Security area at https://github.com/moneyparking/evidencebound-core/security and GitHub private vulnerability reporting when enabled. Do not place credentials, private provider payloads, exploit secrets or production user data in a public issue.

A useful report includes affected version/commit, minimal reproduction, expected/actual trust outcome, and whether the issue can cause an incorrect `ALLOW`, undetected protected-state mutation, graph under-invalidation or replay bypass.

## External review status

No independent external security audit is currently claimed. The reviewer-facing scope and reproducibility packet is maintained in `docs/SECURITY_REVIEW_SCOPE.md`, and public scheduling/status is tracked in issue #23. Security-impact details should use private vulnerability reporting rather than the public tracking issue until coordinated disclosure permits publication.

## Security invariants

Security regressions include: tampered protected payload remaining trusted, missing required evidence receiving `ALLOW`, hash change being automatically labeled `REFUTED`, non-descendants entering blast radius, or consequential action escaping the post-invalidation re-verification gate.
