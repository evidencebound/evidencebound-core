# WebMCP Production Acceptance

Acceptance date: 2026-08-31
Canonical URL: `https://evidencebound.org/webmcp/`
Merged PR: `#31`
Production merge SHA: `1655514e60e8266331cb431c7726f37725608c99`
Competition implementation head merged as second parent: `14f7a81200daafa717af474c0747ac4e215b195d`

This document records only observed evidence. `PASS` means the named check was observed successfully. `UNRUN` means this Project Chat did not have the required environment. No browser behavior is inferred from unit tests or static HTTP responses.

## Acceptance matrix

| Gate | Status | Evidence |
|---|---|---|
| PR #31 merged with expected implementation head | PASS | GitHub reports `merged_at=2026-08-31T12:48:28Z`, merge SHA `1655514e...`, head `14f7a812...`. |
| `main` points to merge SHA | PASS | `main = 1655514e60e8266331cb431c7726f37725608c99`. |
| Post-merge WebMCP workflow | PASS | GitHub Actions run `33393610245`, job `webmcp`, all syntax/unit/adversarial steps successful. |
| Post-merge full Core CI | PASS | GitHub Actions run `33393610270`, all eight jobs successful including Python 3.10–3.13 tests, clean-room, security, supply-chain, Google ADK compatibility, and trusted supply-chain attestation. |
| Exact-SHA Vercel production deployment | PASS | Deployment `dpl_GFsK47tx8z4P5F1G42rrgSJuin5N` is `READY`, target `production`, metadata SHA `1655514e...`. |
| Canonical judge HTML public readback | PASS | `GET https://evidencebound.org/webmcp/` returned HTTP 200 and title `EvidenceBound WebMCP Authority Compiler`. |
| Canonical `app.mjs` public readback | PASS | HTTP 200, `application/javascript`. |
| Canonical `webmcp-adapter.mjs` public readback | PASS | HTTP 200, `application/javascript`; contains live-state and commit-time rechecks. |
| Canonical `control-core.mjs` public readback | PASS | HTTP 200, `application/javascript`; contains five-state authority evaluator and exact-fingerprint grant semantics. |
| Security response headers | PASS | Observed CSP with `script-src 'self'`, `connect-src 'self'`, `frame-ancestors 'none'`, `base-uri 'self'`, `form-action 'self'`; HSTS; `X-Content-Type-Options: nosniff`; `X-Frame-Options: DENY`; restrictive camera/microphone/geolocation Permissions-Policy. |
| Credential-free static surface | PASS | Canonical HTML/modules load without challenge credentials; implementation has no external network or secret dependency in the tested/static contract. |
| Real WebMCP browser discovery/invocation/removal | UNRUN | This Project environment does not expose a WebMCP-capable browser/runtime for `document.modelContext` execution. Must be run in the supported judge browser. |
| Final unedited judge-path video | UNRUN | Requires the same supported browser and human capture. |

## Production HTTP evidence

Observed canonical HTML response included:

```text
HTTP 200
Content-Security-Policy: default-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'
Strict-Transport-Security: max-age=63072000
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

The canonical HTML visibly identifies the controlled-demo boundary and does not claim a real external release effect.

## Production code identity

The production deployment metadata binds Vercel target `production` to:

```text
githubCommitRef = main
githubCommitSha = 1655514e60e8266331cb431c7726f37725608c99
githubCommitVerification = verified
```

The merge commit has parents:

```text
9a2137fe29d0532120a774398a45fa90a9850153   # pre-competition main baseline
14f7a81200daafa717af474c0747ac4e215b195d   # final WebMCP competition implementation head
```

This preserves the competition-period commit history rather than squashing it.

## Browser acceptance still required

Use [`JUDGE_PATH.md`](JUDGE_PATH.md) in a supported ChatGPT browser or Chrome WebMCP environment. The browser gate may be called `PASS` only after observing all of the following in one working environment:

1. `document.modelContext` is available and the runtime badge becomes `AVAILABLE`.
2. Initial `HUMAN_REQUIRED` exposes only the safe tools.
3. Agent authority request does not create a grant.
4. Human exact-snapshot grant changes state to `AUTHORIZED` and `execute_authorized_release` becomes browser-visible.
5. Agent execution returns the controlled receipt with `externalSideEffect=false`.
6. Human correction or revocation removes the execution tool and changes state to `INVALIDATED`.
7. Optional adversarial explanation references the automated stale-descriptor, correction-during-verification and concurrent-execution tests; do not claim those browser races were manually reproduced unless they were.

## Claim boundary after production acceptance

Allowed now:

- "The WebMCP judge surface is publicly deployed at `evidencebound.org/webmcp/`."
- "The production deployment is bound to merge SHA `1655514e...`."
- "Post-merge Core CI and WebMCP CI pass on that SHA."
- "The public response exposes the expected self-hosted modules and restrictive security headers."

Not yet allowed:

- "The full WebMCP judge workflow passed in a supported browser" until the browser gate is actually observed.
- "Submission is complete" until Devpost confirms the final submission.
- any unsupported claim of first/only/unique invention, customer adoption, external production mutation, security certification, or guaranteed safety.
