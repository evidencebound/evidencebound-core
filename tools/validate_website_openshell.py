from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "site" / "index.html"
RAB1 = ROOT / "site" / "rab1" / "index.html"
NVIDIA = ROOT / "site" / "assets" / "nvidia-mark.svg"
ASSESSMENT = ROOT / "site" / "assessment" / "index.html"
OEM = ROOT / "site" / "partners" / "oem" / "index.html"
LOGO = ROOT / "site" / "assets" / "evidencebound-mark.jpg"

home = HOME.read_text(encoding="utf-8")
assert RAB1.is_file(), "missing site/rab1/index.html public proof page"
assert NVIDIA.is_file(), "missing site/assets/nvidia-mark.svg"
assert ASSESSMENT.is_file(), "missing site/assessment/index.html"
assert OEM.is_file(), "missing site/partners/oem/index.html"
assert LOGO.is_file(), "missing site/assets/evidencebound-mark.jpg"

rab1 = RAB1.read_text(encoding="utf-8")
nvidia = NVIDIA.read_text(encoding="utf-8")

home_required = [
    "Consequential Agent Control Assessment",
    "Authorization is not a one-time event.",
    "NVIDIA OpenShell",
    "href=\"/assessment/\"",
    "href=\"/partners/oem/\"",
    "href=\"/rab1/\"",
    "bounded tested property",
]
for marker in home_required:
    assert marker in home, f"homepage missing required RAB-1 marker: {marker}"

rab1_required = [
    "EvidenceBound Runtime Authority Benchmark on NVIDIA OpenShell",
    "FULL_PASS",
    "12/12",
    "8/8",
    "rab1-v1-full-pass-20260930",
    "36759924096",
    "73 retained files",
    "0 evidence hash failures",
    "EvidenceBound demonstrated outcome-aware recovery authority and trusted "
    "operation-lineage enforcement at the OpenShell pre-effect HTTP boundary "
    "under the tested benchmark conditions.",
    "not NVIDIA validation or endorsement",
    "independent runtime enforcement substrate",
]
for marker in rab1_required:
    assert marker in rab1, f"RAB-1 page missing required marker: {marker}"

for forbidden in [
    "private key",
    "signing secret",
    "customer confidential",
    "reviewer_id",
    "GROUND_TRUTH_PRIVATE",
    "blind-case-manifest-private",
]:
    assert forbidden not in home
    assert forbidden not in rab1

assert "<svg" in nvidia and "viewBox" in nvidia
print("website-openshell-public-proof-ok")
