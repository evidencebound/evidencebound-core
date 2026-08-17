import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "benchmarks" / "ai_boost_challenge4" / "run.py"


def test_ai_boost_challenge4_benchmark_acceptance() -> None:
    completed = subprocess.run(
        [sys.executable, str(BENCHMARK), "--assert-targets"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    print(completed.stdout)
    if completed.stderr:
        print(completed.stderr)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert '"evidence_coverage_milli": 1000' in completed.stdout
    assert '"invalidation_recall_milli": 1000' in completed.stdout
    assert '"receipt_reproduction_rate_milli": 1000' in completed.stdout
