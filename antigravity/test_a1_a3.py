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
MODEL_NAME = "gemini-2.5-flash"

CONFIGS_DIR = Path(__file__).resolve().parent / "agent_configs"
OUTPUT_DIR = Path(__file__).resolve().parent / "test_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

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


def call_gemini(client: genai.Client, system_prompt: str, user_prompt: str, config: dict) -> dict:
    """Call Gemini API and return parsed JSON response."""
    response = client.models.generate_content(
        model=config["model"]["model_name"],
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=config["model"]["temperature"],
            max_output_tokens=config["model"]["max_output_tokens"],
            response_mime_type=config["model"]["response_mime_type"],
        ),
    )
    text = response.text.strip()
    if text.startswith("`json"): text = text[7:]
    if text.startswith("`"): text = text[3:]
    if text.endswith("`"): text = text[:-3]
    return json.loads(text.strip())


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

def run_a1(client: genai.Client, complaint: str) -> dict:
    """Run Agent A1: parse complaint into structured signals."""
    print("\n" + "=" * 60)
    print("  AGENT A1 - INTAKE AGENT")
    print("=" * 60)
    print(f"  Input: {complaint}")
    print("-" * 60)

    config = load_agent_config("a1_intake.json")
    t0 = time.time()

    result = call_gemini(
        client=client,
        system_prompt=config["system_prompt"],
        user_prompt=complaint,
        config=config,
    )

    latency = time.time() - t0
    print(f"\n  A1 Output ({latency:.2f}s):")
    print(json.dumps(result, indent=2, ensure_ascii=False))

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
    print("\n" + "=" * 60)
    print("  AGENT A2 - EVIDENCE AGENT")
    print("=" * 60)

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

    result = call_gemini(
        client=client,
        system_prompt=config["system_prompt"],
        user_prompt=user_prompt,
        config=config,
    )

    latency = time.time() - t0
    print(f"\n  A2 Output ({latency:.2f}s):")
    print(json.dumps(result, indent=2, ensure_ascii=False))

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
    print("\n" + "=" * 60)
    print("  AGENT A3 - SEVERITY AGENT")
    print("=" * 60)

    config = load_agent_config("a3_severity.json")
    t0 = time.time()

    # Build input combining A1 signals and A2 evidence
    user_prompt = json.dumps({
        "crisis_signals_from_a1": a1_output,
        "evidence_summary_from_a2": a2_output,
        "scoring_weights": config["scoring_weights"],
        "rules": config["rules"],
    }, indent=2, ensure_ascii=False)

    result = call_gemini(
        client=client,
        system_prompt=config["system_prompt"],
        user_prompt=user_prompt,
        config=config,
    )

    latency = time.time() - t0
    print(f"\n  A3 Output ({latency:.2f}s):")
    print(json.dumps(result, indent=2, ensure_ascii=False))

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
    print("\n" + "#" * 60)
    print("  GAON GUARD AI - Crisis Intelligence Pipeline Test")
    print("  Agents: A1 (Intake) -> A2 (Evidence) -> A3 (Severity)")
    print("  Demo: Ali Pur Flood Crisis")
    print("  Data: ALL SYNTHETIC")
    print("#" * 60)

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
    print("\n" + "=" * 60)
    print("  PIPELINE SUMMARY")
    print("=" * 60)
    print(f"  A1 Latency: {a1_result['latency_s']:.2f}s")
    print(f"  A2 Latency: {a2_result['latency_s']:.2f}s")
    print(f"  A3 Latency: {a3_result['latency_s']:.2f}s")
    print(f"  Total:      {total_latency:.2f}s")
    print()
    print(f"  Location:      {a1_result['output'].get('location_name')}")
    print(f"  Crisis Types:  {a1_result['output'].get('crisis_type')}")
    print(f"  Missing Child: {a1_result['output'].get('missing_person_signal')}")
    print(f"  Confidence:    {a2_result['output'].get('confidence')}")
    print(f"  Severity:      {a3_result['output'].get('severity_score')}/5")
    print(f"  Authorization: {a3_result['output'].get('authorization')}")
    print(f"  Must Verify:   {a3_result['output'].get('must_verify')}")
    print("=" * 60)

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
