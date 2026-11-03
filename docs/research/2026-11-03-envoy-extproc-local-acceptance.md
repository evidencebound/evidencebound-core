# EvidenceBound — Local Envoy ext_proc Action Integrity Acceptance

**Date:** 2026-11-03  
**Classification:** Synthetic/local protocol evaluation. No Google-managed service acceptance or customer system deployment.

## Fixed source and evidence

- Reused **EvidenceBound Core** \`main\` commit \`068a66f019d2185cf5f6875bcc5d3f36023ff59b\`; not equivalent to the published v0.4.0 tag.
- Envoy protobuf/gRPC packages used locally: \`grpcio==1.76.0\`, \`xds-protos==1.76.0\`; Python 3.13.1 / Windows.
- The lab uses an actual loopback \`envoy.service.ext_proc.v3.ExternalProcessor.Process\` gRPC stream and a fixed-operation, **headers-only** contract. EvidenceBound Core handles evidence/provenance/policy and verification-receipt binding; a separate **synthetic fixture** handles approval and one-time capability consumption.
- Archive: \`EvidenceBound-Gateway-Lab-2026-11-03.zip\`, SHA-256 \`8073a818fe1ccfa417544e7db6d492c9926077295bf1bc74d920ff3c9ec0ab97\`. Retained privately in isolated research storage; **not a downloadable public reproduction bundle**.
- Original archived benchmark receipt SHA-256: \`475a7a235c1802a2531ee1a7fdba328016af468785cb29e541d02d0e3ba775f9\`.
- Archive was copied to a non-temporary isolated directory and byte-for-byte SHA verified, extracted separately, and rerun in a new process. The replay confirmed the source file digests. A limited scan of standard secret markers returned no matches; this is not a comprehensive security audit.

## Independent local replay by EvidenceBound, not third-party verification

The extracted archive passed **19/19** automated negative and boundary tests in **0.95 s**, including: missing/revoked/mismatched approval, stale/changed/missing evidence, policy drift, duplicate side effects, unknown prior outcome, direct bypass, invalid selector, unavailable extension, invalid processing phase, missing operation ID, observability-only mode, deterministic receipt, 24-way concurrency and gRPC deadline.

A fresh run of **400 sequential localhost gRPC checks** measured wall-clock **p50 1.6913 ms** and **p95 2.4155 ms**. Batch-averaged process CPU time was **2.8125 ms/check**. At an **assumed** $0.10/vCPU-hour, CPU-only arithmetic gives about **$0.000000078/check**, excluding Google service charges, network, storage, logging, minimum billing, operator effort, and integration costs. No Google API/model calls and no customer approval or financial loss measurements occurred in this replay.

The eight intentionally unguarded **synthetic** control scenarios produced effect counts \`[1,1,1,1,1,2,1,1]\`; the protected fixture returned \`[1,0,0,0,0,1,0,0]\`. These are in-process sink counts, **not universal side-effect prevention, completed recovery, or customer ROI**. BLOCK does not imply a workflow completed successfully.

## What remains unproven

1. \`ProducerExtension\` / \`ExtensionBinding\` API eligibility, real Google Agent Gateway compatibility and deployed behavior: **NOT VERIFIED**.
2. The real gateway's identity/authenticated provenance and compatibility with the simulated \`metadata_context\` selector.
3. Full-body MCP tool-argument binding; the local fixture is intentionally headers-only with a predefined operation.
4. Real human authority; the test controller simulates approvals and has no authenticated human issuer.
5. Independent signed and externally anchored receipts; protected cross-process state, unknown-outcome reconciliation, multi-host concurrency and restart-safe once-only effects.
6. Customer supervision effort, repeated token spend, recovery compute cost and deployment ROI.

## Correct interpretation

This is a narrow protocol **proof of concept**, not a Google Agent Gateway product, Google-certified extension, production-ready agent authority gate, partner validation, or Google cost benchmark. Any customer-specific pilot requires explicit approval, a real downstream effect boundary and separate acceptance testing.

Official Google documentation still describes extension bindings as coming soon / early preview (verified 2026-11-03): [Extensible policies on Agent Gateway](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/gateways/extension-bindings-overview).

## Reproducibility boundary and stop condition

Reproduction requires the retained private archive. The above public digest allows integrity comparison but cannot substitute for access to the code and fixture; no third-party reproducibility is claimed. Do not extend this adapter for production until there is an authorized customer-owned staging sink, preview access where relevant and an externally accepted paid scope. The existing [$1,000 Action-Control Check](https://evidencebound.org/assessment/) remains the current commercial entry offer.
