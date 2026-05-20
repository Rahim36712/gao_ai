"""
Gaon Guard AI - Master agent test runner.

Runs each engine test as a subprocess so one failure does not stop the rest.
All data remains synthetic demo data.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = Path(os.environ.get("GG_TEST_OUTPUT_DIR", r"D:\gaon_guard_test_outputs"))
REPORT_PATH = OUTPUT_DIR / "final_agent_test_report.json"
STDOUT_PREVIEW_CHARS = 4000

TESTS = [
    {"label": "A-engine", "script": "test_a1_a3.py"},
    {"label": "A4-X", "script": "test_a4_x.py"},
    {"label": "B-engine", "script": "test_b1_b3.py"},
    {"label": "C-engine", "script": "test_c1_c3.py"},
]


def _preview(text):
    text = text or ""
    if len(text) <= STDOUT_PREVIEW_CHARS:
        return text
    return text[:STDOUT_PREVIEW_CHARS] + "\n... [truncated]"


def run_script(test):
    script_name = test["script"]
    script_path = SCRIPT_DIR / script_name
    started = time.time()

    result = {
        "engine": test["label"],
        "script_name": script_name,
        "passed": False,
        "runtime_seconds": 0.0,
        "stdout_preview": "",
        "stderr": "",
        "returncode": None,
    }

    if not script_path.exists():
        result["stderr"] = f"Script not found: {script_path}"
        return result

    env = os.environ.copy()
    env["GG_TEST_OUTPUT_DIR"] = str(OUTPUT_DIR)

    try:
        completed = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(SCRIPT_DIR),
            env=env,
            text=True,
            capture_output=True,
        )
        result["returncode"] = completed.returncode
        result["passed"] = completed.returncode == 0
        result["stdout_preview"] = _preview(completed.stdout)
        result["stderr"] = completed.stderr.strip()
    except Exception as exc:
        result["stderr"] = f"{type(exc).__name__}: {exc}"
    finally:
        result["runtime_seconds"] = round(time.time() - started, 2)

    return result


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Gaon Guard AI - Master Agent Runner")
    print(f"Output report: {REPORT_PATH}")
    print()

    results = []
    total_started = time.time()

    for test in TESTS:
        print(f"Running {test['label']} ({test['script']})...")
        result = run_script(test)
        results.append(result)
        status = "PASS" if result["passed"] else "FAIL"
        print(f"  {test['label']}: {status} ({result['runtime_seconds']:.2f}s)")

    report = {
        "_doc": "Gaon Guard AI - Final Agent Test Report",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_runtime_seconds": round(time.time() - total_started, 2),
        "data_type": "SYNTHETIC",
        "results": results,
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 48)
    print("FINAL SUMMARY")
    print("=" * 48)
    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"{result['engine']}: {status}")
    print("=" * 48)
    print(f"Report saved to: {REPORT_PATH}")

    return 0 if all(result["passed"] for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
