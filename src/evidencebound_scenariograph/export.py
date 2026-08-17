"""ASAM OpenSCENARIO XML 1.4 structural export seam.

The SPARK prototype deliberately does not claim XSD conformance until schema
validation is wired into acceptance. The artifact is an inspectable integration seam.
"""
from __future__ import annotations

from dataclasses import dataclass
from xml.etree.ElementTree import Element, SubElement, tostring

from .model import FieldDecision, ScenarioGraph


@dataclass(frozen=True)
class OpenScenarioArtifact:
    xml: str
    standard: str = "ASAM OpenSCENARIO XML 1.4"
    conformance: str = "STRUCTURAL_SEAM_NOT_XSD_VALIDATED"


def export_openscenario_14(graph: ScenarioGraph, *, case_id: str) -> OpenScenarioArtifact:
    """Export a deterministic OpenSCENARIO-shaped XML artifact."""

    assessments = graph.assessments()
    blocked = any(item.decision is FieldDecision.BLOCKED for item in assessments.values())
    review = any(
        item.decision is FieldDecision.REVIEW_REQUIRED for item in assessments.values()
    )
    verification = "BLOCKED" if blocked else "REVIEW_REQUIRED" if review else "VERIFIED"

    root = Element("OpenSCENARIO")
    SubElement(
        root,
        "FileHeader",
        {
            "revMajor": "1",
            "revMinor": "4",
            "date": "1970-01-01T00:00:00",
            "description": f"EvidenceBound ScenarioGraph structural seam for {case_id}",
            "author": "EvidenceBound ScenarioGraph",
        },
    )
    declarations = SubElement(root, "ParameterDeclarations")
    values = {
        "eb_case_id": case_id,
        "eb_functional_label": str(graph.fields["functional_label"].value),
        "eb_verification": verification,
        "eb_export_conformance": "STRUCTURAL_SEAM_NOT_XSD_VALIDATED",
    }
    for name, value in sorted(values.items()):
        SubElement(
            declarations,
            "ParameterDeclaration",
            {"name": name, "parameterType": "string", "value": value},
        )

    SubElement(root, "CatalogLocations")
    SubElement(root, "RoadNetwork")
    SubElement(root, "Entities")
    SubElement(root, "Storyboard")
    xml = tostring(root, encoding="unicode", short_empty_elements=True)
    return OpenScenarioArtifact(xml=xml)
