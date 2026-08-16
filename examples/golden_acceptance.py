from dataclasses import replace

from evidencebound import (
    ActionDecision,
    ApplicabilityStatus,
    EvidenceBound,
    EvidenceRecord,
    IntegrityStatus,
    InvalidationReason,
    PolicyBinding,
    ProvenanceRecord,
)

policy = PolicyBinding("safety", "1")
eb = EvidenceBound(policy=policy)
p = ProvenanceRecord("tool", "urn:example:source")
e = EvidenceRecord("e1", {"value": 1}, p)
a = eb.checkpoint(agent="A", evidence=[e], output={"step": "A"}, checkpoint_id="A")
b = eb.checkpoint(
    agent="B",
    evidence=[e],
    output={"step": "B"},
    depends_on=["A"],
    checkpoint_id="B",
)
c = eb.checkpoint(
    agent="C",
    evidence=[e],
    output={"step": "C"},
    depends_on=["B"],
    checkpoint_id="C",
)
verified_a = eb.verify(a)
verified_b = eb.verify(b)
verified_c = eb.verify(c)
assert verified_a.action is ActionDecision.ALLOW
assert verified_b.action is ActionDecision.ALLOW
assert verified_c.action is ActionDecision.ALLOW

tampered = replace(c, output={"step": "tampered"})
assert eb.verify(tampered, prior_receipt=verified_c.receipt).action is ActionDecision.BLOCK

changed = EvidenceRecord("e1", {"value": 2}, p)
review = eb.verify(c, current_evidence={"e1": changed}, prior_receipt=verified_c.receipt)
assert review.integrity is IntegrityStatus.VERIFIED
assert review.applicability is ApplicabilityStatus.REVIEW_REQUIRED

plan = eb.invalidate(
    checkpoint_id="B",
    reason=InvalidationReason.EVIDENCE_CHANGED,
    consequential={"C"},
)
assert plan.recompute == ("B", "C")
assert plan.reusable == ("A",)
assert plan.requires_verification == ()
assert plan.blocked == ("C",)
print("GOLDEN_ACCEPTANCE_PASS")
