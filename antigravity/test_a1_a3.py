"""
Gaon Guard AI - Agent Test Script: A1 -> A2 -> A3
Runs the Crisis Intelligence Engine pipeline on the Ali Pur demo complaint.

Usage:
    1. Start the FastAPI server: uvicorn main:app --reload --port 8000
    2. Set GEMINI_API_KEY env var: $env:GEMINI_API_KEY="your-key"
    3. Run: python test_a1_a3.py

All data is SYNTHETIC DEMO DATA.
"""

import json
import os
import sys
import time
import concurrent.futures
from datetime import datetime, timezone
from pathlib import Path

import requests
from google import genai
from google.genai import types

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

API_BASE = os.environ.get("API_BASE", "http://localhost:8000")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL_NAME = "gemini-2.0-flash"

CONFIGS_DIR = Path(__file__).resolve().parent / "agent_configs"
OUTPUT_DIR = Path(os.environ.get("GG_TEST_OUTPUT_DIR", r"D:\gaon_guard_test_outputs"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Demo complaint (Roman Urdu)
DEMO_COMPLAINT = (
    "Ali Pur mein 2 din se pani khara hai, bachay diarrhea se "
    "beemar hain aur bacha nazar nahi aa raha"
)

# Known mappings for the demo (A2 needs these to look up the right APIs)
VILLAGE_LOOKUP = {
    "Ali Pur": {"village_id": "VIL_001", "district": "Larkana", "nearest_bhu": "BHU_Larkana_03"},
    "Basti Malook": {"village_id": "VIL_002", "district": "Dadu", "nearest_bhu": "BHU_Dadu_01"},
}


def load_agent_config(filename: str) -> dict:
    """Load an agent config JSON file."""
    with open(CONFIGS_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


from gemini_utils import GeminiCallError, call_gemini
from pretty_print import print_a1, print_a2, print_a3, print_summary, print_header, print_agent_header


def api_get(path: str) -> dict:
    """GET from the FastAPI backend."""
    r = requests.get(f"{API_BASE}{path}", timeout=10)
    r.raise_for_status()
    return r.json()


def api_post(path: str, data: dict) -> dict:
    """POST to the FastAPI backend."""
    r = requests.post(f"{API_BASE}{path}", json=data, timeout=10)
    r.raise_for_status()
    return r.json()


def post_trace(agent_id: str, crisis_event_id: str, input_summary: str,
               observations: str, reasoning: str, decision: str,
               action_taken: str, tool_calls: list, output_summary: str,
               error_recovery: str = None) -> dict:
    """Post an agent trace to the backend."""
    return api_post("/api/traces/append", {
        "agent_id": agent_id,
        "crisis_event_id": crisis_event_id,
        "input_summary": input_summary,
        "observations": observations,
        "reasoning": reasoning,
        "decision": decision,
        "action_taken": action_taken,
        "tool_calls": tool_calls,
        "output_summary": output_summary,
        "error_recovery": error_recovery,
    })


# ══════════════════════════════════════════════
# AGENT A1: INTAKE
# ══════════════════════════════════════════════

def local_a1_fallback(complaint: str, reason: str) -> dict:
    text = str(complaint or "").lower()
    crisis_types = []
    if any(word in text for word in ["pani", "flood", "khara"]):
        crisis_types.append("FLOOD")
    if any(word in text for word in ["diarrhea", "beemar", "sick", "health"]):
        crisis_types.append("HEALTH")
    if any(word in text for word in ["nazar nahi", "missing", "laapata", "gum", "bacha"]):
        crisis_types.append("MISSING_PERSON")
    return {
        "location_name": "Ali Pur" if "ali pur" in text else None,
        "district_guess": "Larkana" if "ali pur" in text else None,
        "crisis_type": crisis_types or ["FLOOD"],
        "affected_group": "CHILDREN" if "bacha" in text or "bachay" in text else "ALL",
        "duration_hours": 48 if "2 din" in text or "2 days" in text else None,
        "urgency_keywords": [
            keyword for keyword in ["pani khara", "diarrhea", "beemar", "nazar nahi", "bacha"]
            if keyword in text
        ],
        "missing_person_signal": "nazar nahi" in text or "missing" in text or "bacha" in text,
        "raw_signals": [complaint],
        "fallback_used": True,
        "fallback_reason": str(reason)[:220],
    }


def local_a2_fallback(a1_output: dict, api_data: dict, reason: str) -> dict:
    checks = []
    supports = 0
    crisis_types = set(a1_output.get("crisis_type", []))

    weather = api_data.get("weather", {})
    rainfall = weather.get("rainfall_mm_24hr", 0)
    weather_verdict = "SUPPORTS" if "FLOOD" in crisis_types and rainfall > 0 else ("CONTRADICTS" if "FLOOD" in crisis_types else "NEUTRAL")
    supports += 1 if weather_verdict == "SUPPORTS" else 0
    checks.append({"source": "weather", "value_retrieved": f"rainfall_mm_24hr: {rainfall}, flood_alert: {weather.get('flood_alert', 'N/A')}", "verdict": weather_verdict, "justification": "Local fallback weather comparison"})

    road = api_data.get("road_status", {})
    road_status = road.get("main_road_status") or road.get("status") or "UNKNOWN"
    road_verdict = "SUPPORTS" if road_status in {"BLOCKED", "DAMAGED"} else "NEUTRAL"
    supports += 1 if road_verdict == "SUPPORTS" else 0
    checks.append({"source": "road_status", "value_retrieved": f"main_road_status: {road_status}", "verdict": road_verdict, "justification": "Road status checked locally"})

    health = api_data.get("health", {})
    diarrhea = health.get("diarrhea_cases_7day", 0)
    health_verdict = "SUPPORTS" if "HEALTH" in crisis_types and diarrhea else "NEUTRAL"
    supports += 1 if health_verdict == "SUPPORTS" else 0
    checks.append({"source": "health", "value_retrieved": f"diarrhea_cases_7day: {diarrhea}", "verdict": health_verdict, "justification": "Health cases checked locally"})

    village = api_data.get("village", {})
    risk_zone = village.get("risk_zone", "UNKNOWN")
    village_verdict = "SUPPORTS" if "FLOOD" in crisis_types and "FLOOD" in risk_zone else "NEUTRAL"
    supports += 1 if village_verdict == "SUPPORTS" else 0
    checks.append({"source": "village_profile", "value_retrieved": f"risk_zone: {risk_zone}", "verdict": village_verdict, "justification": "Village risk profile checked locally"})

    missing = api_data.get("missing_persons", {})
    missing_rows = missing.get("data", []) if isinstance(missing, dict) else []
    missing_verdict = "SUPPORTS" if a1_output.get("missing_person_signal") and missing_rows else "NEUTRAL"
    supports += 1 if missing_verdict == "SUPPORTS" else 0
    checks.append({"source": "missing_persons", "value_retrieved": f"open_cases: {len(missing_rows)}", "verdict": missing_verdict, "justification": "Missing-person cases checked locally"})

    return {
        "confidence": "HIGH" if supports >= 4 else ("MEDIUM" if supports >= 2 else "LOW"),
        "evidence_checks": checks,
        "overall_summary": f"Local fallback found {supports}/5 supporting sources.",
        "fallback_used": True,
        "fallback_reason": str(reason)[:220],
    }


def local_a3_fallback(a1_output: dict, a2_output: dict, reason: str) -> dict:
    weights = {}
    crisis_types = set(a1_output.get("crisis_type", []))
    checks = a2_output.get("evidence_checks", [])
    supports = sum(1 for check in checks if check.get("verdict") == "SUPPORTS")
    contradicts = any(check.get("verdict") == "CONTRADICTS" for check in checks)

    if "FLOOD" in crisis_types:
        weights["standing_water"] = 1.0
    if a1_output.get("affected_group") == "CHILDREN":
        weights["children_affected"] = 1.5
    if "HEALTH" in crisis_types:
        weights["disease_present"] = 2.0
    if a1_output.get("missing_person_signal"):
        weights["missing_persons_detected"] = 1.5
    if supports >= 2:
        weights["evidence_support"] = 1.0

    total = round(sum(weights.values()), 1)
    severity = min(5, max(1, int(round(total))))
    authorization = "HOLD_COORDINATOR_REVIEW" if a2_output.get("confidence") == "LOW" else "DISPATCH_AUTHORIZED"
    return {
        "severity_score": severity,
        "weight_breakdown": weights,
        "total_raw_score": total,
        "authorization": authorization,
        "must_verify": bool(contradicts),
        "reasoning": "Local fallback severity score from A1 signals and A2 evidence.",
        "fallback_used": True,
        "fallback_reason": str(reason)[:220],
    }


def normalize_a3_output(result: dict, a1_output: dict, a2_output: dict) -> dict:
    if not isinstance(result, dict):
        return local_a3_fallback(a1_output, a2_output, "Gemini returned non-object A3 output")

    breakdown = result.get("weight_breakdown", {})
    if isinstance(breakdown, list):
        normalized_breakdown = {}
        for item in breakdown:
            if isinstance(item, dict):
                signal = item.get("signal")
                weight = item.get("weight")
                if signal is not None:
                    normalized_breakdown[str(signal)] = weight
        result["weight_breakdown"] = normalized_breakdown
    elif not isinstance(breakdown, dict):
        result["weight_breakdown"] = {}

    if result.get("severity_score") is None:
        return local_a3_fallback(a1_output, a2_output, "Gemini returned incomplete A3 output")

    result.setdefault("authorization", "HOLD_COORDINATOR_REVIEW")
    result.setdefault("must_verify", False)
    result.setdefault("reasoning", "")
    result.setdefault("fallback_used", False)
    result.setdefault("fallback_reason", "")
    return result


def run_a1(client: genai.Client, complaint: str) -> dict:
    """Run Agent A1: parse complaint into structured signals."""
    print_agent_header("A1", "INTAKE AGENT")
    print(f"  Input: {complaint}")

    config = load_agent_config("a1_intake.json")
    t0 = time.time()

    try:
        result = call_gemini(
            client=client,
            system_prompt=config["system_prompt"],
            user_prompt=complaint,
            config=config,
        )
        if result.get("fallback_required"):
            result = local_a1_fallback(complaint, result.get("error", "Gemini unavailable"))
        else:
            result.setdefault("fallback_used", False)
            result.setdefault("fallback_reason", "")
    except GeminiCallError as e:
        print(f"  [WARN] A1 Gemini failed cleanly: {e}")
        print("  [FALLBACK] Using deterministic local A1 intake")
        result = local_a1_fallback(complaint, e)
    except Exception as e:
        print(f"  [WARN] A1 recovered from error: {e}")
        print("  [FALLBACK] Using deterministic local A1 intake")
        result = local_a1_fallback(complaint, e)

    latency = time.time() - t0
    print_a1(result, latency)

    # Post trace
    post_trace(
        agent_id="A1_INTAKE",
        crisis_event_id=None,
        input_summary=f"Raw complaint: {complaint[:100]}",
        observations=f"Extracted {len(result.get('crisis_type', []))} crisis types, "
                     f"location: {result.get('location_name', 'N/A')}",
        reasoning="Parsed Roman Urdu complaint using NLP extraction",
        decision="SIGNALS_EXTRACTED",
        action_taken="Structured JSON output produced, passing to A2",
        tool_calls=[],
        output_summary=json.dumps(result, ensure_ascii=False)[:500],
    )

    return {"output": result, "latency_s": latency}


# ══════════════════════════════════════════════
# AGENT A2: EVIDENCE
# ══════════════════════════════════════════════

def run_a2(client: genai.Client, a1_output: dict) -> dict:
    """Run Agent A2: cross-check against 5 data sources."""
    print_agent_header("A2", "EVIDENCE AGENT")

    config = load_agent_config("a2_evidence.json")
    t0 = time.time()

    # Resolve village info
    location = a1_output.get("location_name", "")
    lookup = VILLAGE_LOOKUP.get(location, {})
    village_id = lookup.get("village_id", "VIL_001")
    district = lookup.get("district", a1_output.get("district_guess", "Larkana"))
    bhu_id = lookup.get("nearest_bhu", "BHU_Larkana_03")

    # Fetch all 5 data sources in parallel
    print(f"  Fetching 5 data sources for {location} ({village_id})...")

    api_data = {}
    tool_calls_log = []

    def fetch(name, path):
        data = api_get(path)
        return name, path, data

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(fetch, "weather", f"/api/weather/{district}"),
            executor.submit(fetch, "road_status", f"/api/roads/{village_id}"),
            executor.submit(fetch, "health", f"/api/health/{bhu_id}"),
            executor.submit(fetch, "village", f"/api/villages/{village_id}"),
            executor.submit(fetch, "missing_persons", "/api/missing/open"),
        ]
        for f in concurrent.futures.as_completed(futures):
            name, path, data = f.result()
            api_data[name] = data
            tool_calls_log.append({
                "tool_name": f"api_get({path})",
                "input": path,
                "output": json.dumps(data, ensure_ascii=False)[:200],
            })
            print(f"    [OK] {name}: fetched")

    # Build prompt for A2 with all evidence
    user_prompt = json.dumps({
        "crisis_event": a1_output,
        "evidence_data": {
            "weather": api_data["weather"],
            "road_status": api_data["road_status"],
            "health_report": api_data["health"],
            "village_profile": api_data["village"],
            "open_missing_persons": api_data["missing_persons"],
        }
    }, indent=2, ensure_ascii=False)

    try:
        result = call_gemini(
            client=client,
            system_prompt=config["system_prompt"],
            user_prompt=user_prompt,
            config=config,
        )
        if result.get("fallback_required") or not isinstance(result.get("evidence_checks"), list):
            result = local_a2_fallback(a1_output, api_data, result.get("error", "Gemini unavailable"))
        else:
            result.setdefault("fallback_used", False)
            result.setdefault("fallback_reason", "")
    except GeminiCallError as e:
        print(f"  [WARN] A2 Gemini failed cleanly: {e}")
        print("  [FALLBACK] Using deterministic local A2 evidence")
        result = local_a2_fallback(a1_output, api_data, e)
    except Exception as e:
        print(f"  [WARN] A2 recovered from error: {e}")
        print("  [FALLBACK] Using deterministic local A2 evidence")
        result = local_a2_fallback(a1_output, api_data, e)

    latency = time.time() - t0
    print_a2(result, latency)

    # Post trace
    post_trace(
        agent_id="A2_EVIDENCE",
        crisis_event_id=None,
        input_summary=f"A1 output for {location}, checking 5 data sources",
        observations=f"Confidence: {result.get('confidence', 'N/A')}, "
                     f"{len(result.get('evidence_checks', []))} checks performed",
        reasoning=result.get("overall_summary", ""),
        decision=f"CONFIDENCE_{result.get('confidence', 'UNKNOWN')}",
        action_taken="Evidence verified, passing to A3",
        tool_calls=tool_calls_log,
        output_summary=json.dumps(result, ensure_ascii=False)[:500],
    )

    return {"output": result, "latency_s": latency, "api_data": api_data}


# ══════════════════════════════════════════════
# AGENT A3: SEVERITY
# ══════════════════════════════════════════════

def run_a3(client: genai.Client, a1_output: dict, a2_output: dict) -> dict:
    """Run Agent A3: weighted scoring and dispatch authorization."""
    print_agent_header("A3", "SEVERITY AGENT")

    config = load_agent_config("a3_severity.json")
    t0 = time.time()

    # Build input combining A1 signals and A2 evidence
    user_prompt = json.dumps({
        "crisis_signals_from_a1": a1_output,
        "evidence_summary_from_a2": a2_output,
        "scoring_weights": config["scoring_weights"],
        "rules": config["rules"],
    }, indent=2, ensure_ascii=False)

    try:
        result = call_gemini(
            client=client,
            system_prompt=config["system_prompt"],
            user_prompt=user_prompt,
            config=config,
        )
        if result.get("fallback_required") or result.get("severity_score") is None:
            result = local_a3_fallback(a1_output, a2_output, result.get("error", "Gemini unavailable"))
        else:
            result.setdefault("fallback_used", False)
            result.setdefault("fallback_reason", "")
    except GeminiCallError as e:
        print(f"  [WARN] A3 Gemini failed cleanly: {e}")
        print("  [FALLBACK] Using deterministic local A3 severity")
        result = local_a3_fallback(a1_output, a2_output, e)
    except Exception as e:
        print(f"  [WARN] A3 recovered from error: {e}")
        print("  [FALLBACK] Using deterministic local A3 severity")
        result = local_a3_fallback(a1_output, a2_output, e)
    result = normalize_a3_output(result, a1_output, a2_output)

    latency = time.time() - t0
    print_a3(result, latency)

    # Post trace
    post_trace(
        agent_id="A3_SEVERITY",
        crisis_event_id=None,
        input_summary=f"A1 signals + A2 evidence (confidence={a2_output.get('confidence', 'N/A')})",
        observations=f"Severity: {result.get('severity_score', 'N/A')}/5, "
                     f"Auth: {result.get('authorization', 'N/A')}",
        reasoning=result.get("reasoning", ""),
        decision=result.get("authorization", "UNKNOWN"),
        action_taken=f"Severity scored at {result.get('severity_score', 'N/A')}/5",
        tool_calls=[],
        output_summary=json.dumps(result, ensure_ascii=False)[:500],
    )

    # Create crisis event if authorized
    if result.get("authorization") == "DISPATCH_AUTHORIZED":
        location = a1_output.get("location_name", "")
        lookup = VILLAGE_LOOKUP.get(location, {})
        village_id = lookup.get("village_id", "VIL_001")

        crisis_result = api_post("/api/crisis/create", {
            "location_village_id": village_id,
            "signals": a1_output.get("crisis_type", []),
            "confidence_level": {"HIGH": 0.9, "MEDIUM": 0.6, "LOW": 0.3}.get(
                a2_output.get("confidence", "MEDIUM"), 0.5
            ),
            "severity_score": result.get("severity_score", 5),
            "source": "AGENT_PIPELINE_A1_A3",
            "raw_complaint_text": DEMO_COMPLAINT,
        })
        print(f"\n  [CRISIS CREATED] {crisis_result['crisis_event']['id']}")

    return {"output": result, "latency_s": latency}


# ══════════════════════════════════════════════
# MAIN PIPELINE
# ══════════════════════════════════════════════

def main():
    print_header("GAON GUARD AI — Crisis Intelligence Pipeline",
                  "A1 (Intake) → A2 (Evidence) → A3 (Severity)")

    # Validate API is running
    try:
        root = api_get("/")
        print(f"\n  [OK] API connected: {root['service']}")
    except Exception as e:
        print(f"\n  [FAIL] Cannot connect to API at {API_BASE}: {e}")
        print("  Start the server: uvicorn main:app --reload --port 8000")
        sys.exit(1)

    # Validate Gemini API key
    if not GEMINI_API_KEY:
        print("\n  [FAIL] GEMINI_API_KEY not set.")
        print("  Set it: $env:GEMINI_API_KEY='your-key-here'")
        sys.exit(1)

    client = genai.Client(api_key=GEMINI_API_KEY)
    print(f"  [OK] Gemini client initialized (model: {MODEL_NAME})")

    total_start = time.time()

    # -- A1: Intake --
    a1_result = run_a1(client, DEMO_COMPLAINT)

    # -- A2: Evidence --
    a2_result = run_a2(client, a1_result["output"])

    # -- A3: Severity --
    a3_result = run_a3(client, a1_result["output"], a2_result["output"])

    total_latency = time.time() - total_start

    # -- Summary --
    print_summary(a1_result["output"], a2_result["output"], a3_result["output"],
                   a1_result["latency_s"], a2_result["latency_s"], a3_result["latency_s"])

    # -- Save trace --
    trace_output = {
        "_doc": "Gaon Guard AI - A1->A2->A3 Pipeline Trace",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "demo_complaint": DEMO_COMPLAINT,
        "a1_intake": {
            "output": a1_result["output"],
            "latency_s": a1_result["latency_s"],
        },
        "a2_evidence": {
            "output": a2_result["output"],
            "latency_s": a2_result["latency_s"],
        },
        "a3_severity": {
            "output": a3_result["output"],
            "latency_s": a3_result["latency_s"],
        },
        "total_latency_s": total_latency,
        "data_type": "SYNTHETIC",
    }

    output_path = OUTPUT_DIR / "a1_a3_trace.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(trace_output, f, indent=2, ensure_ascii=False)
    print(f"\n  Trace saved to: {output_path}")


if __name__ == "__main__":
    main()
