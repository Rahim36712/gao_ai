"""
Gaon Guard AI - Live synthetic case runner.

Usage:
    python -u run_live_case.py --complaint "Ali Pur mein flood hai aur bacha laapata hai"

All data is SYNTHETIC DEMO DATA.
"""

import argparse
import json
import os
import re
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from google import genai


OUTPUT_DIR = Path(os.environ.get("GG_TEST_OUTPUT_DIR", r"D:\gaon_guard_test_outputs"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
os.environ["GG_TEST_OUTPUT_DIR"] = str(OUTPUT_DIR)

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(BACKEND_DIR))

from test_a1_a3 import run_a1, run_a2, run_a3  # noqa: E402
from test_a4_x import api_get, run_a4_dispatch, run_coordinator_x  # noqa: E402
from test_b1_b3 import run_b1, run_b2, run_b3  # noqa: E402
from audit_pipeline import run_c1, run_c2, run_c3  # noqa: E402


def _has_any(text, keywords):
    lowered = text.lower()
    return any(keyword in lowered for keyword in keywords)


def _extract_cnic(text):
    match = re.search(r"\b\d{5}-\d{7}-\d\b", text)
    return match.group(0) if match else "42301-7777777-7"


def _make_client():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("[WARN] GEMINI_API_KEY not set; deterministic fallbacks will be used")
        return None
    return genai.Client(api_key=api_key)


def _has_conflict(a2_output):
    return any(
        check.get("verdict") == "CONTRADICTS"
        for check in a2_output.get("evidence_checks", [])
    )


def _fallback_used(*outputs):
    return any(bool(output.get("fallback_used")) for output in outputs if isinstance(output, dict))


def _run_a_pipeline(client, complaint):
    a1 = run_a1(client, complaint)
    a2 = run_a2(client, a1["output"])
    a3 = run_a3(client, a1["output"], a2["output"])
    return {"a1": a1, "a2": a2, "a3": a3}


def _run_a3_after_a2(client, a1, a2):
    return run_a3(client, a1["output"], a2["output"])


def _run_dispatch_if_needed(client, a_outputs):
    a3_output = a_outputs["a3"]["output"]
    if a3_output.get("authorization") != "DISPATCH_AUTHORIZED":
        return None

    a1_output = a_outputs["a1"]["output"]
    location = a1_output.get("location_name") or "Ali Pur"
    village_id = "VIL_001" if location == "Ali Pur" else "VIL_002"
    village_data = api_get(f"/api/villages/{village_id}")
    return run_a4_dispatch(client, a1_output, a3_output, village_data)


def _run_x_if_needed(client, a_outputs):
    a2_output = a_outputs["a2"]["output"]
    if not _has_conflict(a2_output):
        return None

    return run_coordinator_x(
        client,
        a_outputs["a1"]["output"],
        {
            "evidence_checks": a2_output.get("evidence_checks", []),
            "confidence": a2_output.get("confidence"),
            "overall_summary": a2_output.get("overall_summary"),
        },
    )


def _run_b_if_needed(client, complaint, a1_output):
    if not a1_output.get("missing_person_signal"):
        return None

    b1 = run_b1(client, complaint)
    b2 = run_b2(client)
    b3 = run_b3(client)
    return {"b1": b1, "b2": b2, "b3": b3}


def _run_b_after_b1(client, b1, a1_missing_signal):
    if b1 is None:
        return None
    if not (a1_missing_signal or b1["output"].get("signal_detected")):
        return {
            "b1": b1,
            "b2": None,
            "b3": None,
            "skipped_reason": "No missing-person signal detected by A1 or B1",
        }
    b2 = run_b2(client)
    b3 = run_b3(client)
    return {"b1": b1, "b2": b2, "b3": b3}


def _run_c_if_needed(client, complaint, pipeline_id):
    audit_keywords = ["cnic", "ration", "tent", "aid", "distribution", "corruption", "fraud", "gps"]
    if not _has_any(complaint, audit_keywords):
        return None

    suspicious = _has_any(complaint, ["corruption", "fraud"])
    gps_far = "gps" in complaint.lower() or suspicious
    beneficiary = {
        "cnic": _extract_cnic(complaint),
        "head_name": f"Live Case {pipeline_id[:8]}",
        "village_id": "VIL_002",
        "household_size": 6,
        "gps_home": {"lat": 26.7320, "lng": 67.7750},
        "damage_level": "SEVERE" if suspicious else "MODERATE",
    }
    distribution = {
        "village_id": "VIL_002",
        "total_tents": 500 if suspicious else 25,
        "total_ration_packs": 400 if suspicious else 80,
        "total_cash_pkr": 5000000 if suspicious else 250000,
        "registered_households": 120,
        "officer_id": "LIVE_CASE_OFFICER",
        "invoice_prices": {"tent_pkr": 25000 if suspicious else 15000, "ration_pack_pkr": 8000 if suspicious else 4500},
        "gps_distribution": {"lat": 27.1234, "lng": 68.5678} if gps_far else {"lat": 26.7350, "lng": 67.7800},
    }

    c1 = run_c1(client, beneficiary)
    c2 = run_c2(client, distribution)
    c3 = run_c3(client, distribution["gps_distribution"], distribution["village_id"])
    return {"c1": c1, "c2": c2, "c3": c3}


def _summary(trace):
    a1 = trace["a_pipeline"]["a1"]["output"]
    a3 = trace["a_pipeline"]["a3"]["output"]
    dispatch = trace.get("dispatch")
    b_engine = trace.get("b_engine")
    c_engine = trace.get("c_engine")

    tickets = dispatch["output"].get("tickets", []) if dispatch else []
    b_matches = []
    if b_engine and b_engine.get("b2"):
        b_matches = b_engine["b2"]["output"].get("matches", [])
    audit_status = None
    if c_engine:
        audit_status = {
            "c1": c_engine["c1"]["output"].get("decision"),
            "c2": c_engine["c2"]["output"].get("audit_status"),
            "c3": c_engine["c3"]["output"].get("verdict"),
        }

    outputs = [
        trace["a_pipeline"]["a1"]["output"],
        trace["a_pipeline"]["a2"]["output"],
        trace["a_pipeline"]["a3"]["output"],
    ]
    if dispatch:
        outputs.append(dispatch["output"])
    if trace.get("x_coordinator"):
        outputs.append(trace["x_coordinator"]["output"])
    if b_engine:
        outputs.append(b_engine["b1"]["output"])
        if b_engine.get("b2"):
            outputs.append(b_engine["b2"]["output"])
        if b_engine.get("b3"):
            outputs.append(b_engine["b3"]["output"])
    if c_engine:
        outputs.extend([c_engine["c1"]["output"], c_engine["c2"]["output"], c_engine["c3"]["output"]])

    return {
        "pipeline_id": trace["pipeline_id"],
        "crisis_type": a1.get("crisis_type", []),
        "severity": a3.get("severity_score"),
        "dispatch_tickets": len(tickets),
        "missing_person_result": {
            "ran": bool(b_engine and b_engine.get("b2")),
            "scanner_ran": bool(b_engine),
            "matches": len(b_matches),
        },
        "fraud_audit_result": {
            "ran": bool(c_engine),
            "status": audit_status,
        },
        "gemini_used": os.environ.get("GEMINI_API_KEY", "") != "",
        "fallback_used": _fallback_used(*outputs),
    }


def main():
    parser = argparse.ArgumentParser(description="Run one live synthetic Gaon Guard AI case.")
    parser.add_argument("--complaint", required=True, help="Complaint text to process.")
    args = parser.parse_args()

    pipeline_id = uuid.uuid4().hex[:12]
    client = _make_client()
    started = time.time()

    trace = {
        "_doc": "Gaon Guard AI - Live Case Trace",
        "pipeline_id": pipeline_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "complaint": args.complaint,
        "data_type": "SYNTHETIC",
    }

    a1 = run_a1(client, args.complaint)
    a1_missing_signal = bool(a1["output"].get("missing_person_signal"))
    c_should_run = _has_any(
        args.complaint,
        ["cnic", "ration", "tent", "aid", "distribution", "corruption", "fraud", "gps"],
    )

    with ThreadPoolExecutor(max_workers=3) as executor:
        a2_future = executor.submit(run_a2, client, a1["output"])
        b1_future = executor.submit(run_b1, client, args.complaint)
        c_future = executor.submit(_run_c_if_needed, client, args.complaint, pipeline_id) if c_should_run else None

        b1 = b1_future.result()
        b_engine_future = executor.submit(_run_b_after_b1, client, b1, a1_missing_signal)

        a2 = a2_future.result()
        a3 = _run_a3_after_a2(client, a1, a2)
        a_pipeline = {"a1": a1, "a2": a2, "a3": a3}

        x_future = executor.submit(_run_x_if_needed, client, a_pipeline) if _has_conflict(a2["output"]) else None
        dispatch_future = None
        if a3["output"].get("authorization") == "DISPATCH_AUTHORIZED":
            dispatch_future = executor.submit(_run_dispatch_if_needed, client, a_pipeline)

        trace["a_pipeline"] = a_pipeline
        trace["x_coordinator"] = x_future.result() if x_future is not None else None
        trace["dispatch"] = dispatch_future.result() if dispatch_future is not None else None
        trace["b_engine"] = b_engine_future.result()
        trace["c_engine"] = c_future.result() if c_future is not None else None

    trace["runtime_seconds"] = round(time.time() - started, 2)
    trace["summary"] = _summary(trace)

    out_path = OUTPUT_DIR / f"live_case_{pipeline_id}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2, ensure_ascii=False)

    summary = trace["summary"]
    print("\nLIVE CASE SUMMARY")
    print("=" * 48)
    print(f"pipeline_id: {summary['pipeline_id']}")
    print(f"crisis type: {summary['crisis_type']}")
    print(f"severity: {summary['severity']}")
    print(f"dispatch tickets: {summary['dispatch_tickets']}")
    print(f"missing-person result: {summary['missing_person_result']}")
    print(f"fraud/audit result: {summary['fraud_audit_result']}")
    print(f"Gemini used: {summary['gemini_used']}")
    print(f"fallback used: {summary['fallback_used']}")
    print(f"trace saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
