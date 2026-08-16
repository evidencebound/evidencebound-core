# Security Policy

## Supported versions

Until a first stable release, only the latest published alpha line is supported for security fixes.

## Reporting a vulnerability

Use GitHub private vulnerability reporting when enabled. Do not place credentials, private provider payloads, exploit secrets or production user data in a public issue.

A useful report includes affected version/commit, minimal reproduction, expected/actual trust outcome, and whether the issue can cause an incorrect `ALLOW`, undetected protected-state mutation, graph under-invalidation or replay bypass.

## Security invariants

Security regressions include: tampered protected payload remaining trusted, missing required evidence receiving `ALLOW`, hash change being automatically labeled `REFUTED`, non-descendants entering blast radius, or consequential action escaping the post-invalidation re-verification gate.
