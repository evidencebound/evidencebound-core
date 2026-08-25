# LinkedIn Onboarding Public Surface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make evidencebound.org ready to be the canonical public website/privacy origin for the EvidenceBound LinkedIn Developer App without a new paid Vercel project.

**Architecture:** Extend the existing static `site/` deployment with privacy and OAuth-callback information pages. Guard the public contract through small pytest checks and rely on the existing Vercel Git deployment for production rollout.

**Tech Stack:** Static HTML/CSS, pytest, existing GitHub Actions CI, existing Vercel project `evidencebound`.

**Spec:** `docs/superpowers/specs/2026-08-25-linkedin-onboarding-surface-design.md`

## Global Constraints

- Canonical deployment root: `site/`.
- Canonical domain: `https://evidencebound.org`.
- No secrets, OAuth codes, tokens, cookies, or private LinkedIn messages in source or rendered output.
- Preserve existing CSP/security headers.
- Contact: `ruslan@evidencebound.org`.

---

### Task 1: Public-Surface Contract Tests

**Files:**
- Create: `tests/test_linkedin_onboarding_site.py`

**Interfaces:**
- Consumes: files under `site/`.
- Produces: static acceptance checks for privacy/callback/footer.

- [ ] Write tests asserting `site/privacy/index.html` and `site/linkedin/oauth/callback/index.html` exist, use EvidenceBound canonical identity/contact, contain no secret-like values, callback HTML contains no script/query reflection, and root footer links to both surfaces.
- [ ] Push test-only commit and verify CI fails because pages/links are absent.

### Task 2: Privacy and Callback Pages

**Files:**
- Create: `site/privacy/index.html`
- Create: `site/linkedin/oauth/callback/index.html`
- Modify: `site/index.html`

**Interfaces:**
- Produces: `/privacy/` and `/linkedin/oauth/callback/` public URLs.

- [ ] Add the bounded privacy policy defined by the spec.
- [ ] Add a non-reflecting OAuth callback information page that never reads query parameters.
- [ ] Add footer links from the canonical home page.
- [ ] Verify CI turns green.

### Task 3: Production Acceptance

**Files:** none.

- [ ] Merge only after branch CI passes.
- [ ] Verify main CI after merge.
- [ ] Verify Vercel production deployment is READY and sourced from the merge commit.
- [ ] Publicly read back `https://evidencebound.org/privacy/` and `https://evidencebound.org/linkedin/oauth/callback/`.