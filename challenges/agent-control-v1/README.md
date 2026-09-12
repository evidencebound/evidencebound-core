# EvidenceBound Agent Control Challenge v1

**Status:** OPEN DEVELOPMENT challenge  
**Goal:** obtain independently authored, replayable evidence about how real agent systems behave when authority, evidence, policy, correction, recovery, and audit state change during a run.

This is a synthetic agent-control challenge. It is not a banking transaction test, a hidden holdout, or a claim that any participating system is safe for production.

## Why this challenge exists

EvidenceBound is testing a narrow proposition: model capability does not itself grant authority to act. A useful agent-control architecture should preserve authority and evidence boundaries even when state changes after an action has been proposed.

The internal DEVELOPMENT benchmark has been frozen at `AGENT-CONTROL-STUDY-v1-N12-2026-09-12`. That frozen cohort contains nine internal deterministic reference architectures plus three EvidenceBound-built adapters over public/open frameworks. Those three adapters are **not** independent third-party submissions.

The independent external cohort starts at **N=0** and is tracked separately. This challenge is the intake path for that cohort.

## What to run

Run one materially distinct agent system against all 10 scenarios in `scenarios.json`.

The scenarios cover:

1. authorized current action;
2. no initial authority;
3. unsupported evidence;
4. evidence becoming stale;
5. authority revocation;
6. policy changing to deny;
7. human correction of the requested action;
8. required recovery;
9. an audit challenge;
10. ambiguous authority.

The challenge source identity is:

`source-set@sha256:14dc37a84feb225c6f80a675a778f44785c02a3f7b6ac8bc8a2206b4c26f266b`

## What to submit

Create a pull request adding exactly two files under:

`challenges/agent-control-v1/submissions/<github-handle>/<system-id>/`

- `submission.json`
- `receipts.json`

Use `submission-template.json` and `receipt-template.json` as the field contract. `receipts.json` must contain exactly 10 receipts, one for each scenario ID.

A receipt records what your system actually did. Do **not** self-score private EvidenceBound failure classes. EvidenceBound performs canonical adjudication separately so the public interface does not disclose internal thresholds, policy implementation, or the full failure taxonomy.

## Independence and eligibility

A submission counts as an independent external submission only when all of the following are true:

- the submitter is not an EvidenceBound owner or maintainer;
- the submitted adapter/run was not authored by EvidenceBound;
- the system is executable and materially distinct from an already accepted submission;
- framework, repository/version/commit, and model/provider/version (or `none`) are disclosed;
- all 10 scenario receipts are present and internally consistent;
- the submitter attests that the receipts came from the disclosed system/run;
- no secrets, customer data, personal data, transaction data, or confidential proprietary payloads are included;
- EvidenceBound can validate the submission provenance and replay contract to the extent claimed by the submitter.

EvidenceBound does not pay provider/model costs for challenge submissions. Local/offline and zero-cost systems are welcome.

## Publication choices

Set `permission_to_publish` to one of:

- `full` — submission details and adjudicated results may be published;
- `aggregate_only` — only aggregate result data may be published;
- `redacted` — EvidenceBound may retain the evidence privately and publish only an agreed redacted summary.

A pull request is public, so do not put information in the PR that you do not want publicly visible.

## What accepted submitters receive

For the first accepted independent submissions, EvidenceBound will provide a bounded failure analysis against the frozen challenge contract and identify observed control-plane weaknesses without requiring customer data or private risk models.

Acceptance means the submission passed evidence/provenance checks. It does **not** mean the system passed every scenario and does not imply endorsement.

## Pull request format

Suggested title:

`challenge(agent-control-v1): submit <system-id>`

In the PR description include:

- GitHub handle / organization;
- system name and repository or artifact reference;
- whether the run can be independently reproduced;
- any provider/model cost incurred by the submitter;
- known limitations;
- publication permission.

## Research boundary

This public package deliberately exposes only the DEVELOPMENT scenario contract and raw submission interface. EvidenceBound does not publish here its private policy engine, hard-gate implementation, internal prompts, thresholds, weighting/calibration logic, complete failure taxonomy, or any sealed regulatory benchmark material.
