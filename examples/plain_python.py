from evidencebound import (
    ActionDecision,
    EvidenceBound,
    EvidenceRecord,
    InvalidationReason,
    PolicyBinding,
    ProvenanceRecord,
)

policy = PolicyBinding("research-policy", "1")
eb = EvidenceBound(policy=policy)
evidence = [
    EvidenceRecord(
        "paper-1",
        {"claim": "observed"},
        ProvenanceRecord("paper", "doi:10.0000/example"),
    )
]
research = eb.checkpoint(
    agent="researcher", evidence=evidence, output={"summary": "supported"}
)
review = eb.checkpoint(
    agent="reviewer",
    evidence=evidence,
    output={"approved": True},
    depends_on=[research.checkpoint_id],
)
result = eb.verify(review)
assert result.action is ActionDecision.ALLOW
plan = eb.invalidate(
    checkpoint_id=research.checkpoint_id,
    reason=InvalidationReason.EVIDENCE_CHANGED,
)
print(result.action.value, plan.recompute)
