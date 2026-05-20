"""
Gaon Guard AI - Agent Test Script: A4 (Dispatch) + X (Coordinator)
Tests dispatch lifecycle and conflict arbitration.

Usage:
    1. Start the FastAPI server: uvicorn main:app --reload --port 8000
    2. Set GEMINI_API_KEY env var
    3. Run: python test_a4_x.py

All data is SYNTHETIC DEMO DATA.
"""

import json
import math
import os
import sys
import time
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


def load_config(filename):
    with open(CONFIGS_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


from gemini_utils import GeminiCallError, call_gemini


def api_get(path):
    r = requests.get(f"{API_BASE}{path}", timeout=10)
    r.raise_for_status()
    return r.json()


def api_post(path, data):
    r = requests.post(f"{API_BASE}{path}", json=data, timeout=10)
    r.raise_for_status()
    return r.json()


def post_trace(agent_id, crisis_event_id, input_summary, observations,
               reasoning, decision, action_taken, tool_calls, output_summary):
    return api_post("/api/traces/append", {
        "agent_id": agent_id, "crisis_event_id": crisis_event_id,
        "input_summary": input_summary, "observations": observations,
        "reasoning": reasoning, "decision": decision,
        "action_taken": action_taken, "tool_calls": tool_calls,
        "output_summary": output_summary,
    })


def haversine(lat1, lng1, lat2, lng2):
    """Calculate distance in km between two GPS points."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _crisis_types(crisis_signals):
    raw = crisis_signals.get("crisis_type", [])
    if isinstance(raw, str):
        raw = [raw]
    return {str(item).upper() for item in raw}


def _fmt_num(value, default="?"):
    try:
        return f"{float(value):.1f}"
    except (TypeError, ValueError):
        return default


def _nearest_team(teams, department, village_data):
    candidates = [t for t in teams if t.get("department") == department]
    if not candidates:
        candidates = list(teams)
    if not candidates:
        return {
            "id": "LOCAL_TEAM",
            "name": "Local emergency team",
            "department": department,
            "lat": village_data.get("lat", 0),
            "lng": village_data.get("lng", 0),
        }

    village_lat = village_data.get("lat", 0)
    village_lng = village_data.get("lng", 0)

    return min(
        candidates,
        key=lambda team: (
            haversine(village_lat, village_lng, team.get("lat", 0), team.get("lng", 0)),
            team.get("id", ""),
        ),
    )


def local_a4_fallback(crisis_signals, severity_output, village_data, teams):
    signals = _crisis_types(crisis_signals)
    desired_departments = []
    if "FLOOD" in signals:
        desired_departments.append(("DISASTER", "Flood response"))
    if "HEALTH" in signals:
        desired_departments.append(("HEALTH", "Health support"))
    if "MISSING_PERSON" in signals or crisis_signals.get("missing_person_signal"):
        desired_departments.append(("RESCUE", "Missing person search"))
    if not desired_departments:
        desired_departments.append(("DISASTER", "General emergency response"))

    tickets = []
    used_team_ids = set()
    for idx, (department, reason) in enumerate(desired_departments[:3], start=1):
        team = _nearest_team(
            [t for t in teams if t.get("id") not in used_team_ids] or teams,
            department,
            village_data,
        )
        used_team_ids.add(team.get("id"))
        distance = round(haversine(
            village_data.get("lat", 0),
            village_data.get("lng", 0),
            team.get("lat", 0),
            team.get("lng", 0),
        ), 1)
        tickets.append({
            "ticket_id": f"A4_LOCAL_{idx:03d}",
            "department": team.get("department", department),
            "team_id": team.get("id", "UNKNOWN"),
            "team_name": team.get("name", "Unknown team"),
            "distance_km": distance,
            "eta_minutes": max(1, int(round((distance / 40) * 60))),
            "status": "ASSIGNED",
            "reason": reason,
        })

    return {
        "tickets": tickets,
        "dispatch_time": datetime.now(timezone.utc).isoformat(),
        "escalation_schedule": {
            "t_plus_30": "Check team acceptance",
            "t_plus_60": "Escalate if no movement",
        },
        "dispatch_summary": f"Local fallback created {len(tickets)} tickets",
        "fallback_used": True,
        "fallback_reason": "Gemini A4 JSON unavailable",
        "severity_score": severity_output.get("severity_score"),
    }


def local_x_fallback(error):
    return {
        "contradiction_summary": "Flood report conflicts with 0mm rainfall evidence.",
        "possible_explanations": [
            "Weather station data lag or malfunction",
            "Irrigation canal breach or upstream water release",
            "Localized standing water not captured by rainfall data",
        ],
        "decision": "REQUEST_VERIFICATION",
        "reasoning": "Local fallback used after Gemini coordinator failure.",
        "timeout_minutes": 30,
        "fallback_action": "Proceed with monitored dispatch if no reply in 30 minutes.",
        "verification_message": "Please verify flood water in Ali Pur despite 0mm rainfall.",
        "fallback_used": True,
        "fallback_reason": str(error)[:220],
    }


# ══════════════════════════════════════════════
# AGENT A4: DISPATCH
# ══════════════════════════════════════════════

def run_a4_dispatch(client, crisis_signals, severity_output, village_data):
    """Run Agent A4: assign teams and create dispatch tickets."""
    print("\n" + "=" * 60)
    print("  AGENT A4 - DISPATCH & TRACKING")
    print("=" * 60)

    config = load_config("a4_dispatch.json")
    t0 = time.time()

    # Fetch available teams
    teams_data = api_get("/api/teams/available")
    print(f"  Available teams: {teams_data['count']}")

    user_prompt = json.dumps({
        "crisis_signals": crisis_signals,
        "severity_output": severity_output,
        "village": village_data,
        "available_teams": teams_data["data"],
    }, indent=2, ensure_ascii=False)

    try:
        if client is None:
            raise GeminiCallError("GEMINI_API_KEY not set")
        result = call_gemini(client, config["system_prompt"], user_prompt, config)
        if not isinstance(result, dict) or not result.get("tickets"):
            raise GeminiCallError("A4 response did not contain dispatch tickets")
    except GeminiCallError as e:
        print(f"  [WARN] A4 Gemini failed cleanly: {e}")
        print("  [FALLBACK] Using deterministic local A4 ticket generator")
        result = local_a4_fallback(
            crisis_signals,
            severity_output,
            village_data,
            teams_data["data"],
        )

    latency = time.time() - t0
    print(f"\n  A4 Output ({latency:.2f}s):")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Post trace
    post_trace(
        agent_id="A4_DISPATCH", crisis_event_id=None,
        input_summary=f"Severity {severity_output.get('severity_score')}/5, "
                      f"{teams_data['count']} teams available",
        observations=f"Created {len(result.get('tickets', []))} dispatch tickets",
        reasoning="Matched nearest available teams by department and Haversine distance",
        decision="TICKETS_CREATED",
        action_taken=f"Dispatched {len(result.get('tickets', []))} teams",
        tool_calls=[{"tool_name": "get_available_teams", "input": "/api/teams/available",
                     "output": f"{teams_data['count']} teams"}],
        output_summary=json.dumps(result, ensure_ascii=False)[:500],
    )

    return {"output": result, "latency_s": latency}


# ══════════════════════════════════════════════
# COORDINATOR AGENT X: CONFLICT ARBITRATION
# ══════════════════════════════════════════════

def run_coordinator_x(client, a1_output, contradicting_evidence):
    """Run Coordinator X: resolve contradictions between agents."""
    print("\n" + "=" * 60)
    print("  AGENT X - COORDINATOR / CONFLICT ARBITRATION")
    print("=" * 60)

    config = load_config("x_coordinator.json")
    t0 = time.time()

    user_prompt = json.dumps({
        "a1_crisis_signals": a1_output,
        "contradicting_evidence": contradicting_evidence,
        "context": "A1 extracted FLOOD signal but A2 weather check returned 0mm rainfall"
    }, indent=2, ensure_ascii=False)

    try:
        if client is None:
            raise GeminiCallError("GEMINI_API_KEY not set")
        result = call_gemini(client, config["system_prompt"], user_prompt, config)
    except GeminiCallError as e:
        print(f"  [WARN] X Gemini failed cleanly: {e}")
        print("  [FALLBACK] Returning REQUEST_VERIFICATION")
        result = local_x_fallback(e)

    latency = time.time() - t0
    print(f"\n  X Output ({latency:.2f}s):")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Post trace
    post_trace(
        agent_id="X_COORDINATOR", crisis_event_id=None,
        input_summary="Contradiction: A1 says FLOOD but weather shows 0mm rainfall",
        observations=f"Decision: {result.get('decision')}, "
                     f"{len(result.get('possible_explanations', []))} explanations generated",
        reasoning=result.get("reasoning", ""),
        decision=result.get("decision", "UNKNOWN"),
        action_taken=f"Arbitration: {result.get('decision')} with {result.get('timeout_minutes')}min timeout",
        tool_calls=[],
        output_summary=json.dumps(result, ensure_ascii=False)[:500],
    )

    # Send verification SMS if REQUEST_VERIFICATION
    if result.get("decision") == "REQUEST_VERIFICATION" and result.get("verification_message"):
        notif = api_post("/api/notify", {
            "type": "ESCALATION",
            "recipient_phone": "+92-300-9990001",
            "message": result["verification_message"],
            "metadata": {"agent": "X_COORDINATOR", "decision": result["decision"]},
        })
        print(f"  [NOTIF] Verification SMS sent: {notif['notification']['id']}")

    return {"output": result, "latency_s": latency}


# ══════════════════════════════════════════════
# SCENARIO 1: Normal dispatch
# ══════════════════════════════════════════════

def scenario_1_normal_dispatch(client):
    """A3 DISPATCH_AUTHORIZED -> A4 creates tickets."""
    print("\n" + "#" * 60)
    print("  SCENARIO 1: Normal Dispatch (no conflicts)")
    print("#" * 60)

    # Simulated A1+A2+A3 outputs (from successful prior pipeline)
    crisis_signals = {
        "location_name": "Ali Pur",
        "crisis_type": ["FLOOD", "HEALTH", "MISSING_PERSON"],
        "affected_group": "CHILDREN",
        "duration_hours": 48,
        "missing_person_signal": True,
    }
    severity_output = {
        "severity_score": 5,
        "authorization": "DISPATCH_AUTHORIZED",
        "must_verify": False,
    }
    village_data = api_get("/api/villages/VIL_001")

    result = run_a4_dispatch(client, crisis_signals, severity_output, village_data)

    # Validate
    tickets = result["output"].get("tickets", [])
    print(f"\n  Validation:")
    print(f"    Tickets created: {len(tickets)}")
    for t in tickets:
        print(f"    - {t.get('department')}: {t.get('team_name')} "
              f"({_fmt_num(t.get('distance_km'))}km, ETA {t.get('eta_minutes', '?')}min)")

    return result


# ══════════════════════════════════════════════
# SCENARIO 2: Conflict -> Coordinator X
# ══════════════════════════════════════════════

def scenario_2_conflict(client):
    """Inject 0mm rainfall into A2 -> trigger Coordinator X."""
    print("\n" + "#" * 60)
    print("  SCENARIO 2: Conflict Dispatch (0mm rainfall vs FLOOD)")
    print("#" * 60)

    a1_output = {
        "location_name": "Ali Pur",
        "district_guess": "Larkana",
        "crisis_type": ["FLOOD", "HEALTH", "MISSING_PERSON"],
        "affected_group": "CHILDREN",
        "duration_hours": 48,
        "urgency_keywords": ["pani khara hai", "beemar", "nazar nahi aa raha"],
        "missing_person_signal": True,
    }

    # Fabricated contradicting evidence (0mm rainfall)
    contradicting_evidence = {
        "evidence_checks": [
            {
                "source": "weather",
                "value_retrieved": "rainfall_mm_24hr: 0, flood_alert: GREEN",
                "verdict": "CONTRADICTS",
                "justification": "Weather data shows 0mm rainfall in last 24hrs but complaint claims 2 days of standing water"
            },
            {
                "source": "road_status",
                "value_retrieved": "main_road_status: BLOCKED",
                "verdict": "SUPPORTS",
                "justification": "Road is confirmed blocked, consistent with flood claim"
            },
            {
                "source": "health",
                "value_retrieved": "diarrhea_cases_7day: 12",
                "verdict": "SUPPORTS",
                "justification": "Health spike supports contaminated water from flooding"
            },
            {
                "source": "village_profile",
                "value_retrieved": "risk_zone: HIGH_FLOOD, flood_history: [2010, 2012, 2022, 2023]",
                "verdict": "SUPPORTS",
                "justification": "Village has extensive flood history"
            },
            {
                "source": "missing_persons",
                "value_retrieved": "Hassan Ali (age 12) reported missing from Ali Pur",
                "verdict": "SUPPORTS",
                "justification": "Missing person report corroborates crisis in area"
            }
        ],
        "confidence": "MEDIUM",
        "overall_summary": "4/5 sources support crisis but weather data contradicts flood claim with 0mm rainfall"
    }

    result = run_coordinator_x(client, a1_output, contradicting_evidence)

    # Validate
    output = result["output"]
    print(f"\n  Validation:")
    print(f"    Decision: {output.get('decision')}")
    print(f"    Explanations: {len(output.get('possible_explanations', []))}")
    print(f"    Timeout: {output.get('timeout_minutes')} minutes")
    has_data_lag = any("lag" in e.lower() or "malfunction" in e.lower() or "delay" in e.lower()
                       for e in output.get("possible_explanations", []))
    has_irrigation = any("irrigation" in e.lower() or "canal" in e.lower() or "dam" in e.lower()
                        for e in output.get("possible_explanations", []))
    print(f"    Has data lag explanation: {has_data_lag}")
    print(f"    Has irrigation/canal explanation: {has_irrigation}")

    return result


# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════

def main():
    print("\n" + "#" * 60)
    print("  GAON GUARD AI - A4 Dispatch + X Coordinator Test")
    print("  Data: ALL SYNTHETIC")
    print("#" * 60)

    try:
        root = api_get("/")
        print(f"\n  [OK] API connected")
    except Exception as e:
        print(f"\n  [FAIL] Cannot connect to API at {API_BASE}: {e}")
        sys.exit(1)

    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
        print(f"  [OK] Gemini client initialized")
    else:
        client = None
        print("  [WARN] GEMINI_API_KEY not set; using local fallbacks")

    total_start = time.time()

    s1_result = scenario_1_normal_dispatch(client)
    s2_result = scenario_2_conflict(client)

    total_latency = time.time() - total_start

    # Summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    print(f"  Scenario 1 (Normal Dispatch): {s1_result['latency_s']:.2f}s")
    print(f"    Tickets: {len(s1_result['output'].get('tickets', []))}")
    print(f"  Scenario 2 (Conflict -> X): {s2_result['latency_s']:.2f}s")
    print(f"    Decision: {s2_result['output'].get('decision')}")
    print(f"    Explanations: {len(s2_result['output'].get('possible_explanations', []))}")
    print(f"  Total: {total_latency:.2f}s")
    print("=" * 60)

    # Save trace
    trace = {
        "_doc": "Gaon Guard AI - A4+X Pipeline Trace",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scenario_1_normal_dispatch": {
            "output": s1_result["output"], "latency_s": s1_result["latency_s"]
        },
        "scenario_2_conflict_arbitration": {
            "output": s2_result["output"], "latency_s": s2_result["latency_s"]
        },
        "total_latency_s": total_latency,
        "data_type": "SYNTHETIC",
    }
    out_path = OUTPUT_DIR / "a4_x_trace.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2, ensure_ascii=False)
    print(f"\n  Trace saved to: {out_path}")


if __name__ == "__main__":
    main()
