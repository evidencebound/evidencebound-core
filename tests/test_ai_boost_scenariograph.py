from prototype.evidencebound_scenariograph import (
    EvidenceItem,
    FieldDecision,
    ScenarioField,
    ScenarioGraph,
)


def _sha(character: str) -> str:
    return character * 64


def _graph() -> ScenarioGraph:
    graph = ScenarioGraph(review_threshold_milli=350)
    graph.add_evidence(EvidenceItem("crash", "fixture://crash/001", _sha("a")))
    graph.add_evidence(EvidenceItem("weather", "fixture://weather/001", _sha("b")))
    graph.add_field(
        ScenarioField(
            "road_type",
            "urban_intersection",
            evidence_ids=("crash",),
            uncertainty_milli=40,
        )
    )
    graph.add_field(
        ScenarioField(
            "weather_state",
            "wet",
            evidence_ids=("weather",),
            uncertainty_milli=120,
        )
    )
    graph.add_field(
        ScenarioField(
            "validation_priority",
            "elevated",
            evidence_ids=("crash",),
            uncertainty_milli=180,
            depends_on_fields=("road_type", "weather_state"),
        )
    )
    return graph


def test_material_claim_without_evidence_fails_closed() -> None:
    graph = ScenarioGraph()
    graph.add_field(ScenarioField("speed_limit", 50))

    assessment = graph.assess_field("speed_limit")

    assert assessment.decision is FieldDecision.BLOCKED
    assert "material_claim_has_no_evidence" in assessment.reasons


def test_unknown_value_requires_review_instead_of_hallucinated_completion() -> None:
    graph = ScenarioGraph()
    graph.add_evidence(EvidenceItem("crash", "fixture://crash/001", _sha("a")))
    graph.add_field(
        ScenarioField(
            "lighting",
            None,
            evidence_ids=("crash",),
            uncertainty_milli=1000,
        )
    )

    assessment = graph.assess_field("lighting")

    assert assessment.decision is FieldDecision.REVIEW_REQUIRED
    assert assessment.reasons == ("value_unknown",)


def test_evidence_change_has_exact_transitive_blast_radius() -> None:
    graph = _graph()

    affected = graph.affected_fields({"weather"})

    assert affected == ("validation_priority", "weather_state")
    assert "road_type" not in affected


def test_receipt_is_stable_and_binds_changed_evidence() -> None:
    graph = _graph()

    first = graph.receipt(changed_evidence_ids={"weather"})
    second = graph.receipt(changed_evidence_ids={"weather"})

    assert first == second
    assert len(first["sha256"]) == 64
    assert first["body"]["affected_fields"] == ["validation_priority", "weather_state"]
    assert all(
        field["decision"] == "VERIFIED"
        for field in first["body"]["fields"]
    )
