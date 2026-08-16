# Troubleshooting

**Why is action BLOCK with apparently valid output?** EvidenceBound evaluates evidence/provenance/policy, not output plausibility. Required provenance or current evidence may be missing.

**Why did changed evidence produce REVIEW_REQUIRED instead of REFUTED?** A checksum difference proves difference, not contradiction. Set explicit refutation only from a verifier/source contract that can establish it.

**Why is my old receipt still integrity VERIFIED after evidence changed?** That is intentional. Historical integrity says the old protected record remains intact; current applicability is a separate decision.

**Why is a downstream node in recompute?** Recovery follows actual dependency edges. Use `ancestors`, `descendants` and `blast_radius` to inspect the graph.

**Can I store receipts beside checkpoints?** You can, but an attacker able to rewrite both can forge a consistent pair. Anchor/protect receipts according to your threat model.
