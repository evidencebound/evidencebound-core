"""ASAM OpenSCENARIO XML 1.4 export for the AI-BOOST SPARK vertical slice.

The export is intentionally minimal: it carries EvidenceBound scenario metadata as
global parameters while satisfying the OpenSCENARIO scenario-document lifecycle
structure. CI validates generated artifacts against the official ASAM 1.4.0 XSD.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass

from .model import FieldDecision, ScenarioGraph


XOSC_CONFORMANCE = "ASAM_OPENSCENARIO_XML_1_4_XSD_VALIDATED_IN_CI"


@dataclass(frozen=True)
class OpenScenarioArtifact:
    xml: str
    standard: str = "ASAM OpenSCENARIO XML 1.4"
    conformance: str = XOSC_CONFORMANCE


def export_openscenario_14(graph: ScenarioGraph, *, case_id: str) -> OpenScenarioArtifact:
    """Export a deterministic minimal OpenSCENARIO XML 1.4 scenario document."""

    assessments = graph.assessments()
    blocked = any(item.decision is FieldDecision.BLOCKED for item in assessments.values())
    review = any(
        item.decision is FieldDecision.REVIEW_REQUIRED for item in assessments.values()
    )
    verification = "BLOCKED" if blocked else "REVIEW_REQUIRED" if review else "VERIFIED"

    root = ET.Element("OpenSCENARIO")
    ET.SubElement(
        root,
        "FileHeader",
        {
            "revMajor": "1",
            "revMinor": "4",
            "date": "1970-01-01T00:00:00",
            "description": f"EvidenceBound ScenarioGraph SPARK export for {case_id}",
            "author": "EvidenceBound ScenarioGraph",
        },
    )
    declarations = ET.SubElement(root, "ParameterDeclarations")
    values = {
        "eb_case_id": case_id,
        "eb_functional_label": str(graph.fields["functional_label"].value),
        "eb_verification": verification,
        "eb_export_conformance": XOSC_CONFORMANCE,
    }
    for name, value in sorted(values.items()):
        ET.SubElement(
            declarations,
            "ParameterDeclaration",
            {"name": name, "parameterType": "string", "value": value},
        )

    ET.SubElement(root, "CatalogLocations")
    ET.SubElement(root, "RoadNetwork")
    ET.SubElement(root, "Entities")
    storyboard = ET.SubElement(root, "Storyboard")
    init = ET.SubElement(storyboard, "Init")
    ET.SubElement(init, "Actions")
    ET.SubElement(storyboard, "StopTrigger")
    xml = ET.tostring(root, encoding="unicode", short_empty_elements=True)
    return OpenScenarioArtifact(xml=xml)
