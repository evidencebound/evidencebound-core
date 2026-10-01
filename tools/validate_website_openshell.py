from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "website" / "index.html"
RAB1 = ROOT / "website" / "rab1.html"
NVIDIA = ROOT / "website" / "assets" / "nvidia-mark.svg"

home = HOME.read_text(encoding="utf-8")
assert RAB1.is_file(), "missing website/rab1.html public proof page"
assert NVIDIA.is_file(), "missing website/assets/nvidia-mark.svg"

rab1 = RAB1.read_text(encoding="utf-8")
nvidia = NVIDIA.read_text(encoding="utf-8")

home_required = [
    "RAB-1",
    "NVIDIA OpenShell",
    "12/12 hard gates",
    "8/8 frozen scenarios",
    "href=\"/rab1\"",
    "Tested on / enforced through",
    "not NVIDIA validation or endorsement",
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
