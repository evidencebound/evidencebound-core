import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_DIR = ROOT / "benchmarks" / "ai_boost_challenge4"
BENCHMARK = BENCHMARK_DIR / "run.py"
BASELINE = BENCHMARK_DIR / "BASELINE.json"


def test_ai_boost_challenge4_benchmark_acceptance() -> None:
    completed = subprocess.run(
        [sys.executable, str(BENCHMARK), "--assert-targets"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    generated = json.loads(completed.stdout)
    retained = json.loads(BASELINE.read_text(encoding="utf-8"))
    assert generated == retained
    metrics = generated["body"]["metrics"]
    assert metrics["evidence_coverage_milli"] == 1000
    assert metrics["mutation_change_detection_milli"] == 1000
    assert metrics["mutation_recovery_precision_milli"] == 1000
    assert metrics["mutation_recovery_recall_milli"] == 1000
    assert metrics["mutation_unrelated_preservation_milli"] == 1000
    assert metrics["receipt_reproduction_rate_milli"] == 1000
