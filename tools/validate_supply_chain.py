"""Validate EvidenceBound build checksums, wheel metadata and CycloneDX SBOM shape."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from email.parser import BytesParser
from email.policy import default
from pathlib import Path

_SHA256_LINE = re.compile(r"^([0-9a-f]{64})  ([^/\\]+)$")
_EXPECTED_NAME = "evidencebound-core"
_EXPECTED_VERSION = "0.3.0"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_manifest(dist: Path, artifacts: list[Path]) -> dict[str, str]:
    manifest = dist / "SHA256SUMS"
    assert manifest.is_file(), f"missing checksum manifest: {manifest}"
    entries: dict[str, str] = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        match = _SHA256_LINE.fullmatch(line)
        assert match is not None, f"invalid SHA256SUMS line: {line!r}"
        digest, filename = match.groups()
        assert filename not in entries, f"duplicate checksum subject: {filename}"
        entries[filename] = digest

    expected_names = {path.name for path in artifacts}
    assert set(entries) == expected_names, (
        f"checksum subjects {sorted(entries)} != artifacts {sorted(expected_names)}"
    )
    for artifact in artifacts:
        actual = sha256(artifact)
        expected = entries[artifact.name]
        assert actual == expected, f"checksum mismatch for {artifact.name}"
        print(f"ARTIFACT_SHA256 {artifact.name} {actual}")
    return entries


def validate_wheel_metadata(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        metadata_paths = [
            name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
        ]
        assert len(metadata_paths) == 1, f"expected one wheel METADATA file: {metadata_paths}"
        message = BytesParser(policy=default).parsebytes(archive.read(metadata_paths[0]))

    assert message["Name"] == _EXPECTED_NAME, message["Name"]
    assert message["Version"] == _EXPECTED_VERSION, message["Version"]
    requirements = message.get_all("Requires-Dist", [])
    unconditional = [requirement for requirement in requirements if "extra ==" not in requirement]
    assert not unconditional, f"unexpected unconditional Requires-Dist: {unconditional}"
    print(f"WHEEL_METADATA name={message['Name']} version={message['Version']}")
    print("UNCONDITIONAL_REQUIRES_DIST=0")


def validate_sbom(sbom: Path) -> None:
    assert sbom.is_file() and sbom.stat().st_size > 0, f"missing/empty SBOM: {sbom}"
    document = json.loads(sbom.read_text(encoding="utf-8"))
    assert isinstance(document, dict), "CycloneDX SBOM root must be an object"
    assert document.get("bomFormat") == "CycloneDX", document.get("bomFormat")
    spec_version = document.get("specVersion")
    assert isinstance(spec_version, str) and spec_version, "missing CycloneDX specVersion"
    serial_number = document.get("serialNumber")
    if serial_number is not None:
        assert isinstance(serial_number, str) and serial_number, "invalid SBOM serialNumber"
    bom_version = document.get("version")
    assert isinstance(bom_version, int) and bom_version > 0, "invalid CycloneDX version"
    components = document.get("components", [])
    assert isinstance(components, list), "CycloneDX components must be a list when present"
    vulnerabilities = document.get("vulnerabilities", [])
    assert isinstance(vulnerabilities, list), (
        "CycloneDX vulnerabilities must be a list when present"
    )
    print(
        "SBOM_VALID "
        f"format=CycloneDX spec={spec_version} components={len(components)} "
        f"vulnerabilities={len(vulnerabilities)}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dist", type=Path)
    args = parser.parse_args()
    dist: Path = args.dist
    assert dist.is_dir(), f"not a dist directory: {dist}"

    wheels = sorted(dist.glob("*.whl"))
    sdists = sorted(dist.glob("*.tar.gz"))
    assert len(wheels) == 1, f"expected exactly one wheel, found: {wheels}"
    assert len(sdists) == 1, f"expected exactly one sdist, found: {sdists}"
    artifacts = [sdists[0], wheels[0]]
    assert all(path.name.startswith("evidencebound_core-0.3.0") for path in artifacts), artifacts

    validate_manifest(dist, artifacts)
    validate_wheel_metadata(wheels[0])
    validate_sbom(dist / "evidencebound-core.sbom.cdx.json")
    print("SUPPLY_CHAIN_EVIDENCE_VALID")


if __name__ == "__main__":
    main()
