"""
Gaon Guard AI — Submission Checklist Verification
Checks all hackathon deliverables and prints PASS/FAIL per item.
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PASS = "\033[92m[PASS]\033[0m"
FAIL = "\033[91m[FAIL]\033[0m"

results = []


def check(name, condition):
    status = PASS if condition else FAIL
    results.append((name, condition))
    print(f"  {status} {name}")
    return condition


def main():
    print("\n" + "=" * 60)
    print("  GAON GUARD AI — SUBMISSION CHECKLIST")
    print("=" * 60)

    # 1. README.md
    print("\n--- Documentation ---")
    readme_path = ROOT / "README.md"
    readme_exists = readme_path.exists()
    check("README.md exists", readme_exists)
    if readme_exists:
        content = readme_path.read_text(encoding="utf-8")
        sections = ["## Overview", "## Architecture", "## Data Schemas",
                     "## Tools and APIs Used", "## Antigravity Role",
                     "## Setup Steps", "## Assumptions and Limitations",
                     "## Privacy Note", "## Baseline Comparison"]
        for s in sections:
            check(f"README has '{s}'", s in content)

    # 2. Mock data files
    print("\n--- Mock Data (9 datasets) ---")
    data_dir = ROOT / "mock_data"
    datasets = ["villages.json", "weather.json", "teams.json",
                "health_reports.json", "missing_persons.json",
                "camp_registrations.json", "beneficiary_registry.json",
                "market_prices.json", "road_status.json"]
    for ds in datasets:
        check(f"mock_data/{ds} exists", (data_dir / ds).exists())

    # 3. Agent configs (11 agents)
    print("\n--- Agent Configs (11 agents) ---")
    config_dir = ROOT / "antigravity" / "agent_configs"
    agents = ["a1_intake", "a2_evidence", "a3_severity", "a4_dispatch",
              "b1_scanner", "b2_matcher", "b3_cluster",
              "c1_registry", "c2_audit", "c3_geoverify", "x_coordinator"]
    for a in agents:
        check(f"agent_configs/{a}.json", (config_dir / f"{a}.json").exists())

    # 4. Antigravity planning docs
    print("\n--- Antigravity Planning ---")
    check("workplan.json exists", (ROOT / "antigravity" / "workplan.json").exists())
    check("task_plan.json exists", (ROOT / "antigravity" / "task_plan.json").exists())
    check("firestore_schema.json exists", (ROOT / "antigravity" / "firestore_schema.json").exists())

    # 5. Test scripts
    print("\n--- Test Scripts ---")
    tests = ["test_a1_a3.py", "test_a4_x.py", "test_b1_b3.py", "test_c1_c3.py"]
    for t in tests:
        check(f"antigravity/{t}", (ROOT / "antigravity" / t).exists())

    # 6. Backend
    print("\n--- Backend ---")
    check("backend/main.py exists", (ROOT / "backend" / "main.py").exists())
    check("backend/edge_cases.py exists", (ROOT / "backend" / "edge_cases.py").exists())
    check("backend/audit_pipeline.py exists", (ROOT / "backend" / "audit_pipeline.py").exists())
    check("backend/export_traces.py exists", (ROOT / "backend" / "export_traces.py").exists())
    check("backend/requirements.txt exists", (ROOT / "backend" / "requirements.txt").exists())

    # 7. Submission traces
    print("\n--- Submission Traces ---")
    traces_path = ROOT / "antigravity" / "submission_traces.json"
    traces_exist = traces_path.exists()
    check("submission_traces.json exists", traces_exist)
    if traces_exist:
        with open(traces_path, "r", encoding="utf-8") as f:
            traces = json.load(f)
        count = traces.get("total_traces", 0)
        check(f"submission_traces has >= 10 entries (found {count})", count >= 10)

    # 8. Flutter app
    print("\n--- Flutter App ---")
    check("mobile/pubspec.yaml exists", (ROOT / "mobile" / "pubspec.yaml").exists())
    check("mobile/lib/main.dart exists", (ROOT / "mobile" / "lib" / "main.dart").exists())
    screens = [f"screen{i}" for i in range(1, 11)]
    screen_dir = ROOT / "mobile" / "lib" / "screens"
    for s in screens:
        found = any(f.name.startswith(s) for f in screen_dir.iterdir()) if screen_dir.exists() else False
        check(f"Flutter {s} exists", found)
    check("mobile/lib/theme.dart exists", (ROOT / "mobile" / "lib" / "theme.dart").exists())

    # 9. Demo script
    print("\n--- Demo Documentation ---")
    check("docs/demo_script.md exists", (ROOT / "docs" / "demo_script.md").exists())

    # 10. API check (only if server is running)
    print("\n--- API Endpoints (requires running server) ---")
    try:
        import requests
        r = requests.get("http://localhost:8000/", timeout=3)
        check("FastAPI responds on :8000", r.status_code == 200)

        endpoints = [
            "/api/villages", "/api/weather/Larkana", "/api/teams",
            "/api/health/Larkana", "/api/missing", "/api/camps",
            "/api/beneficiaries/VIL_002", "/api/demo/edge_cases",
            "/api/demo/traces",
        ]
        for ep in endpoints:
            r = requests.get(f"http://localhost:8000{ep}", timeout=3)
            check(f"GET {ep} -> 200", r.status_code == 200)

        for i in range(1, 7):
            r = requests.post(f"http://localhost:8000/api/demo/edge_case/{i}", timeout=3)
            check(f"POST /api/demo/edge_case/{i} -> 200", r.status_code == 200)
    except Exception:
        print(f"  {FAIL} Server not running — skipping API checks")
        print("       Start server: cd backend && uvicorn main:app --port 8000")

    # Summary
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print("\n" + "=" * 60)
    print(f"  RESULT: {passed}/{total} checks passed")
    if passed == total:
        print("  STATUS: READY FOR SUBMISSION")
    else:
        failed = [name for name, ok in results if not ok]
        print(f"  FAILED: {', '.join(failed[:5])}" + (" ..." if len(failed) > 5 else ""))
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
