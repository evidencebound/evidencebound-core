# EBCJ-1 Conformance Corpus

This directory is the language-neutral conformance target for EvidenceBound canonicalization version `EBCJ-1`.

`vectors.json` contains fixed source JSON values, the exact expected UTF-8 canonical JSON text, the corresponding byte-level hex representation, and SHA-256 digests for representative EvidenceBound domains. A conforming runtime can consume the JSON values independently and compare its output byte-for-byte with these vectors.

The digest rule is:

```text
SHA-256("evidencebound:<domain>:EBCJ-1\0" || canonical_bytes(value))
```

## Semantics represented

EBCJ-1 supports JSON `null`, booleans, integers, Unicode strings, arrays, and string-keyed objects. Object keys are sorted lexicographically, JSON separators are compact, and output is UTF-8 with non-ASCII characters preserved rather than ASCII-escaped.

EBCJ-1 performs **no Unicode normalization**. The `unicode-composed` and `unicode-decomposed` vectors are intentionally different byte sequences and digests even though they may render similarly.

EBCJ-1 is an EvidenceBound format. It is **not** a claim of RFC 8785/JCS compliance.

## Python-specific invalid cases

`invalid-python.json` documents values that cannot be represented directly as JSON fixtures but must fail the Python implementation, including floats, bytes, nested floats, and mappings with non-string keys. The test suite maps each case ID to an actual Python value and checks for `CanonicalizationError`.

## Stability

Changing any valid EBCJ-1 vector requires either fixing a demonstrable corpus error or changing the canonicalization version. Do not silently reinterpret historical EBCJ-1 records.

The corpus is conformance evidence, not formal verification and not a proof of SHA-256 collision resistance.
