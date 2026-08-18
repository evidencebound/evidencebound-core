"""Live Gemini generateContent holdout for AI-BOOST Challenge 4.

This path intentionally mirrors llm_holdout_gemini.py but uses the stable
Generate Content API surface instead of the newer Interactions API. It keeps
the same deterministic PSNI case selection, prompt, JSON schema, scorer and
claim boundary so endpoint access is the only material variable.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

from google import genai  # type: ignore[import-not-found]
from google.genai import types  # type: ignore[import-not-found]

HERE = Path(__file__).resolve().parent
BASELINE_PATH = HERE / "llm_holdout_gemini.py"
SPEC = importlib.util.spec_from_file_location("ai_boost_llm_holdout_interactions", BASELINE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load baseline Gemini holdout module")
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)

MODEL_DEFAULT = BASE.MODEL_DEFAULT
DEFAULT_CASES = BASE.DEFAULT_CASES


def run_benchmark(*, model: str, case_count: int) -> dict[str, Any]:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    client = genai.Client(api_key=api_key)
    packets = BASE._selected_packets(case_count)
    schema = BASE._response_schema()
    scores: list[dict[str, Any]] = []
    total_input_tokens = 0
    total_output_tokens = 0
    total_thought_tokens = 0

    for packet in packets:
        response = client.models.generate_content(
            model=model,
            contents=BASE._prompt(packet),
            config=types.GenerateContentConfig(
                candidate_count=1,
                temperature=0,
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )
        text = response.text
        if not isinstance(text, str) or not text.strip():
            raise RuntimeError("Gemini generateContent returned no model text")
        candidate = json.loads(text)
        if not isinstance(candidate, dict):
            raise RuntimeError("Gemini structured output is not an object")

        expected = packet["expected"]
        if not isinstance(expected, BASE.NIStats20Record):
            raise RuntimeError("internal expected comparator type mismatch")
        scores.append(BASE.score_candidate(expected, candidate))

        usage = response.usage_metadata
        if usage is not None:
            total_input_tokens += int(getattr(usage, "prompt_token_count", 0) or 0)
            total_output_tokens += int(getattr(usage, "candidates_token_count", 0) or 0)
            total_thought_tokens += int(getattr(usage, "thoughts_token_count", 0) or 0)

    body = {
        "schema": "evidencebound-ai-boost-challenge4-live-llm-holdout/0.2",
        "provider": "google-gemini-api",
        "api_surface": "generateContent",
        "model": model,
        "sdk": f"google-genai/{importlib.metadata.version('google-genai')}",
        "prompt_version": BASE.PROMPT_VERSION,
        "source": "PSNI Northern Ireland Police Recorded Injury RTC 2024",
        "cases": case_count,
        "evaluated_fields": list(BASE.EVALUATED_FIELDS),
        "metrics": BASE._aggregate(scores),
        "usage": {
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_thought_tokens": total_thought_tokens,
        },
        "case_scores": scores,
        "claim_boundary": (
            "Live schema-constrained model extraction benchmark on an independent public coded-"
            "evidence holdout. Semantic mismatches are identified with a held-out deterministic "
            "comparator for evaluation only; the production trust gate cannot infer semantic "
            "truth merely from valid provenance. Results do not establish simulator validity, "
            "automotive production safety, homologation or Challenge Owner data performance."
        ),
    }
    return {"body": body, "sha256": BASE._sha256(body)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=MODEL_DEFAULT)
    parser.add_argument("--cases", type=int, default=DEFAULT_CASES)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.cases < 1 or args.cases > 64:
        raise SystemExit("--cases must be between 1 and 64")

    receipt = run_benchmark(model=args.model, case_count=args.cases)
    rendered = json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False)
    if args.output is not None:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
