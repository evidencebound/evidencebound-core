"""Reproducible engineering benchmark; results are scenario-specific."""

from __future__ import annotations

import time

from evidencebound import (
    EvidenceBound,
    EvidenceRecord,
    InvalidationReason,
    PolicyBinding,
    ProvenanceRecord,
)

N = 100
policy = PolicyBinding("benchmark", "1")
eb = EvidenceBound(policy=policy)
e = [EvidenceRecord("e", {"v": 1}, ProvenanceRecord("synthetic", "urn:bench"))]
previous = None
for i in range(N):
    cid = f"n{i:03}"
    deps = [] if previous is None else [previous]
    eb.checkpoint(
        agent="bench",
        evidence=e,
        output={"node": i},
        depends_on=deps,
        checkpoint_id=cid,
    )
    previous = cid

failed = "n075"
t0 = time.perf_counter()
full_restart = tuple(f"n{i:03}" for i in range(N))
full_elapsed = time.perf_counter() - t0

t1 = time.perf_counter()
plan = eb.invalidate(checkpoint_id=failed, reason=InvalidationReason.WORKER_FAILED)
selective_elapsed = time.perf_counter() - t1
print(
    {
        "scenario": "100-node linear synthetic workflow; invalidate n075",
        "full_restart_nodes": len(full_restart),
        "selective_recompute_nodes": len(plan.recompute),
        "reused_nodes": len(plan.reusable),
        "recomputations_avoided": len(full_restart) - len(plan.recompute),
        "planning_elapsed_seconds": selective_elapsed,
        "baseline_list_elapsed_seconds": full_elapsed,
    }
)
