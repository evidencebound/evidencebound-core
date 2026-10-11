"""Check public Core tracked files for private paths and high-confidence credential patterns."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_PATHS = frozenset(
    {
        "AUTONOMOUS_HANDOFF.md",
        "FUNDING_TARGET_MATRIX.md",
        "WORKLOG.md",
        "docs/superpowers/specs/2026-08-31-webmcp-authority-compiler-design.md",
        "docs/superpowers/plans/2026-08-31-webmcp-authority-compiler.md",
        "docs/superpowers/specs/2026-09-10-evidencebound-control-center-design.md",
        "docs/superpowers/plans/2026-09-10-evidencebound-control-center.md",
    }
)
FORBIDDEN_PREFIXES = ("benchmarks/bank_ecp_v1/",)
FORBIDDEN_NAME_PARTS = ("bank-ecp-v1-foundation",)
CREDENTIAL_SIGNATURES = {
    "PEM private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b"),
    "AWS access key": re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
    "Google API key": re.compile(r"\bAIza[A-Za-z0-9_-]{30,}\b"),
}


def tracked_paths() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    )
    return [item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def validate(paths: list[str]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        if (
            path in FORBIDDEN_PATHS
            or any(path.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)
            or any(marker in path for marker in FORBIDDEN_NAME_PARTS)
        ):
            errors.append(f"private-only path in public tree: {path}")
            continue
        target = ROOT / path
        if not target.is_file() or target.stat().st_size > 1_000_000:
            continue
        try:
            content = target.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            continue
        for kind, pattern in CREDENTIAL_SIGNATURES.items():
            if pattern.search(content):
                errors.append(f"possible {kind} in {path}; value suppressed")
    return errors


def main() -> int:
    errors = validate(tracked_paths())
    for error in errors:
        print(error)
    if errors:
        return 1
    print("Public IP and credential boundary: PASS (pattern-limited)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
