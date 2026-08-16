# Pre-existing Work and Extraction Boundary

EvidenceBound Core was developed after several application/reference implementations under the same maintainer account. This repository intentionally does not aggregate their cloud, hackathon or product code.

## Reference implementations reviewed

- **EvidenceBound Verified Memory** — reusable concepts: deterministic snapshot hashing, historical integrity vs current applicability, provenance-aware durable memory. Application-specific CockroachDB/AWS code is not core.
- **EvidenceBound Recovery Mesh** — reusable concepts: directed dependencies, cycle rejection, downstream invalidation, selective recovery and Google agent integration. Commerce/hackathon/domain orchestration is not core.
- **EvidenceBound DataHub Gate** — reusable concepts: verify-before-use, fail-closed gating, sealed evidence packs and explicit security limits. DataHub/MCP/judge assets are not core.
- **SignalReview** — commercial/reference application context only. No SignalReview business logic is required or intentionally copied into this package.

## Code provenance policy

Core source in this repository is a clean, generic implementation of the project’s own concepts and invariants. Pre-existing MIT and Apache-2.0 repositories were reviewed for behavior/architecture, not mechanically merged. No cloud credentials, provider payloads, hackathon media or application data belong here.
