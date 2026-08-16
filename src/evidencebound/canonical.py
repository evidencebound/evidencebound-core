"""Versioned deterministic canonicalization used by EvidenceBound receipts."""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

CANONICALIZATION_VERSION = "EBCJ-1"


class CanonicalizationError(ValueError):
    """Raised when a value cannot be represented unambiguously by EBCJ-1."""


def _validate(value: Any, path: str = "$") -> None:
    if value is None or isinstance(value, (bool, int, str)):
        return
    if isinstance(value, float):
        raise CanonicalizationError(f"floats are not supported by EBCJ-1 at {path}")
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise CanonicalizationError(f"mapping key is not a string at {path}")
            _validate(item, f"{path}.{key}")
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            _validate(item, f"{path}[{index}]")
        return
    raise CanonicalizationError(f"unsupported type {type(value).__name__} at {path}")


def canonical_bytes(value: Any) -> bytes:
    """Return deterministic UTF-8 JSON bytes for the intentionally narrow EBCJ-1 domain."""
    _validate(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def digest(value: Any, *, domain: str) -> str:
    """SHA-256 digest with versioned domain separation."""
    prefix = f"evidencebound:{domain}:{CANONICALIZATION_VERSION}\0".encode()
    return hashlib.sha256(prefix + canonical_bytes(value)).hexdigest()
