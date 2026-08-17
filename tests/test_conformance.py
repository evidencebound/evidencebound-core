import json
import re
from dataclasses import replace
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from evidencebound import (
    ActionDecision,
    CanonicalizationError,
    Checkpoint,
    DependencyGraph,
    EvidenceRecord,
    EvidenceState,
    PolicyBinding,
    ProvenanceRecord,
    canonical_bytes,
    digest,
    verify_checkpoint,
    verify_receipt,
)

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "conformance" / "EBCJ-1" / "vectors.json"
INVALID = ROOT / "conformance" / "EBCJ-1" / "invalid-python.json"
PROPERTY_SETTINGS = settings(max_examples=80, deadline=None, derandomize=True)
TEXT = st.text(alphabet=st.characters(blacklist_categories=("Cs",)), max_size=16)
SCALAR = st.one_of(st.none(), st.booleans(), st.integers(-10**12, 10**12), TEXT)
JSON_VALUE = st.recursive(
    SCALAR,
    lambda children: st.one_of(
        st.lists(children, max_size=5),
        st.dictionaries(TEXT, children, max_size=5),
    ),
    max_leaves=20,
)


def make_checkpoint(
    checkpoint_id: str,
    *,
    output: object,
    depends_on: tuple[str, ...] = (),
    evidence_value: object | None = None,
) -> Checkpoint:
    payload = {"value": checkpoint_id if evidence_value is None else evidence_value}
    evidence = EvidenceRecord(
        f"e-{checkpoint_id}",
        payload,
        ProvenanceRecord("conformance", f"urn:evidencebound:{checkpoint_id}"),
    )
    return Checkpoint(
        checkpoint_id,
        "property-agent",
        (evidence,),
        output,
        PolicyBinding("property-policy", "1"),
        depends_on=depends_on,
    )


def test_fixed_ebcj1_conformance_vectors_match_production_implementation():
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    assert corpus["canonicalization_version"] == "EBCJ-1"
    assert corpus["digest_algorithm"] == "SHA-256"
    ids = [vector["id"] for vector in corpus["vectors"]]
    assert len(ids) == len(set(ids))

    for vector in corpus["vectors"]:
        encoded = canonical_bytes(vector["value"])
        assert encoded.decode("utf-8") == vector["canonical_utf8"]
        assert encoded.hex() == vector["canonical_hex"]
        for domain in corpus["domains"]:
            assert digest(vector["value"], domain=domain) == vector["digests"][domain]

    by_id = {vector["id"]: vector for vector in corpus["vectors"]}
    assert by_id["unicode-composed"]["canonical_hex"] != by_id["unicode-decomposed"][
        "canonical_hex"
    ]


def test_python_invalid_input_corpus_fails_closed():
    invalid = json.loads(INVALID.read_text(encoding="utf-8"))
    values = {
        "float": 1.5,
        "nested-float": {"x": [1.5]},
        "bytes": b"raw",
        "non-string-key": {1: "value"},
    }
    assert {case["id"] for case in invalid["cases"]} == set(values)
    for case in invalid["cases"]:
        assert case["expected_exception"] == "CanonicalizationError"
        with pytest.raises(
            CanonicalizationError,
            match=re.escape(case["reason_contains"]),
        ):
            canonical_bytes(values[case["id"]])


@PROPERTY_SETTINGS
@given(JSON_VALUE)
def test_supported_values_round_trip_to_same_canonical_bytes(value):
    encoded = canonical_bytes(value)
    decoded = json.loads(encoded.decode("utf-8"))
    assert canonical_bytes(decoded) == encoded


@PROPERTY_SETTINGS
@given(st.dictionaries(TEXT, JSON_VALUE, max_size=8))
def test_mapping_insertion_order_does_not_change_canonical_bytes(mapping):
    reversed_mapping = dict(reversed(list(mapping.items())))
    assert canonical_bytes(mapping) == canonical_bytes(reversed_mapping)


@PROPERTY_SETTINGS
@given(
    JSON_VALUE,
    st.sampled_from(
        [
            ("evidence", "checkpoint"),
            ("checkpoint", "verification"),
            ("verification", "operation"),
            ("operation", "evidence"),
        ]
    ),
)
def test_digest_domains_are_separated_for_same_payload(value, domains):
    left, right = domains
    assert left != right
    assert digest(value, domain=left) != digest(value, domain=right)


@PROPERTY_SETTINGS
@given(st.integers(-10**9, 10**9), st.integers(1, 10**6))
def test_changed_evidence_is_review_required_not_refuted(original, delta):
    checkpoint = make_checkpoint("changed", output={"answer": 1}, evidence_value=original)
    current = EvidenceRecord(
        "e-changed",
        {"value": original + delta},
        ProvenanceRecord("conformance", "urn:evidencebound:changed"),
    )
    result = verify_checkpoint(checkpoint, current_evidence={"e-changed": current})

    assert result.evidence[0].state is EvidenceState.CHANGED
    assert all(item.state is not EvidenceState.REFUTED for item in result.evidence)
    assert result.action is ActionDecision.REVIEW_REQUIRED


@PROPERTY_SETTINGS
@given(st.integers(-10**9, 10**9), st.integers(1, 10**6))
def test_protected_checkpoint_mutation_breaks_retained_receipt(value, delta):
    checkpoint = make_checkpoint("receipt", output={"value": value})
    result = verify_checkpoint(checkpoint)
    mutated = replace(checkpoint, output={"value": value + delta})

    assert verify_receipt(result.receipt, checkpoint)
    assert not verify_receipt(result.receipt, mutated)
    rechecked = verify_checkpoint(mutated, prior_receipt=result.receipt)
    assert rechecked.action is ActionDecision.BLOCK


@st.composite
def dag_cases(draw):
    node_count = draw(st.integers(min_value=1, max_value=8))
    pairs = [(child, parent) for child in range(1, node_count) for parent in range(child)]
    flags = draw(st.lists(st.booleans(), min_size=len(pairs), max_size=len(pairs)))
    dependencies = {index: [] for index in range(node_count)}
    for (child, parent), enabled in zip(pairs, flags, strict=True):
        if enabled:
            dependencies[child].append(parent)
    roots = draw(
        st.sets(
            st.integers(min_value=0, max_value=node_count - 1),
            min_size=1,
            max_size=node_count,
        )
    )
    checkpoints = tuple(
        make_checkpoint(
            f"n{index}",
            output={"node": index},
            depends_on=tuple(f"n{parent}" for parent in dependencies[index]),
        )
        for index in range(node_count)
    )
    return checkpoints, dependencies, roots


@PROPERTY_SETTINGS
@given(dag_cases())
def test_generated_dag_blast_radius_is_exact(case):
    checkpoints, dependencies, roots = case
    graph = DependencyGraph(checkpoints)
    children = {index: set() for index in dependencies}
    for child, parents in dependencies.items():
        for parent in parents:
            children[parent].add(child)

    expected = set(roots)
    pending = list(roots)
    while pending:
        current = pending.pop()
        for child in children[current]:
            if child not in expected:
                expected.add(child)
                pending.append(child)

    expected_ids = {f"n{index}" for index in expected}
    root_ids = tuple(f"n{index}" for index in roots)
    expected_order = tuple(
        checkpoint_id
        for checkpoint_id in graph.topological_order()
        if checkpoint_id in expected_ids
    )
    assert graph.blast_radius(root_ids) == expected_order
    assert set(graph.blast_radius(root_ids)) == expected_ids
