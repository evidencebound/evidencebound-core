# LinkedIn Onboarding Public Surface — Design

Date: 2026-08-25
Status: Approved in chat

## Goal

Make `https://evidencebound.org` ready to serve as the canonical public website and privacy-policy origin for the EvidenceBound LinkedIn Developer App without introducing a separate paid Vercel project.

## Scope

- Add a public privacy policy at `/privacy/` covering the EvidenceBound website and the owner-authorized LinkedIn integration.
- Add a public OAuth callback information surface at `/linkedin/oauth/callback/` that is safe before the Developer App exists and can later be replaced or complemented by a server-side callback if persistent automated OAuth is enabled.
- Add Privacy and LinkedIn integration links to the canonical site footer.
- Keep the site static and free of secrets. No access token, client secret, authorization code, browser cookie, or private LinkedIn message may be written into source or rendered into HTML.
- Preserve the existing CSP and security headers.

## Privacy commitments

The policy must accurately state that:

- EvidenceBound is early-stage open-source AI safety infrastructure maintained by Ruslan Vrublevskyi.
- The public site does not intentionally collect LinkedIn credentials or private messages.
- If the LinkedIn integration is authorized, it may process the authenticated member identifier, EvidenceBound organization identifier/role authorization, approved post content/media metadata, publication resource identifiers, and operational receipts needed to perform authorized publishing and verification.
- OAuth access/refresh tokens are secrets and must remain in approved secret stores; they are never intentionally committed to public source.
- GitHub/GitHub Actions, Vercel, and LinkedIn may process operational data according to their own terms when used as infrastructure providers.
- The integration is intended only for the maintainer's authorized EvidenceBound/member surfaces, not third-party account management.
- Users may request deletion/revocation through `ruslan@evidencebound.org` and can revoke LinkedIn app access in LinkedIn account settings.

## OAuth callback boundary

The public callback page is an onboarding endpoint, not a token store. Before a server-side exchange implementation is explicitly deployed with secrets, it must not echo `code`, `state`, `error`, or other query parameters into the page or logs under application control. Initial live acceptance may use LinkedIn Developer Portal token generation / owner OAuth instead of a persistent callback service.

## Acceptance

1. `/privacy/` is committed under the canonical `site/` deployment root.
2. `/linkedin/oauth/callback/` exists and exposes no query-string data.
3. Root footer links to Privacy and the LinkedIn integration information surface.
4. Automated tests assert canonical title/contact, no secret-shaped values, and callback non-reflection.
5. CI passes and the production Vercel deployment is READY.
6. Public readback confirms `https://evidencebound.org/privacy/` is live.