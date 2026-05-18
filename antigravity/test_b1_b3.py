"""
Gaon Guard AI - Agent Test Script: B1 (Scanner) -> B2 (Matcher) -> B3 (Cluster)
Tests the Missing Person engine pipeline.

Usage:
    1. Start the FastAPI server: uvicorn main:app --reload --port 8000
    2. Set GEMINI_API_KEY env var
    3. Run: python test_b1_b3.py

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

CONFIGS_DIR = Path(__file__).resolve().parent / "agent_configs"
OUTPUT_DIR = Path(__file__).resolve().parent / "test_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# Village GPS lookup
VILLAGE_GPS = {
    "VIL_001": {"lat": 27.5580, "lng": 68.2120, "name": "Ali Pur"},
    "VIL_004": {"lat": 27.5110, "lng": 68.1890, "name": "Goth Ibrahim"},
    "VIL_008": {"lat": 28.2810, "lng": 68.4520, "name": "Basti Lashari"},
    "VIL_013": {"lat": 27.5950, "lng": 68.2400, "name": "Goth Pir Bux"},
    "VIL_017": {"lat": 28.3100, "lng": 68.4100, "name": "Goth Shah Nawaz"},
    "VIL_021": {"lat": 27.9200, "lng": 69.3500, "name": "Goth Ghulam Hussain"},
    "VIL_005": {"lat": 27.9650, "lng": 69.3150, "name": "Khanpur Mahar"},
    "VIL_032": {"lat": 27.5700, "lng": 68.2000, "name": "Basti Chandio"},
    "VIL_034": {"lat": 29.0800, "lng": 70.3000, "name": "Chak 27/WB"},
    "VIL_019": {"lat": 29.1040, "lng": 70.3290, "name": "Chak 78/NP"},
    "VIL_027": {"lat": 27.5400, "lng": 68.1700, "name": "Goth Wasan"},
    "VIL_050": {"lat": 27.5300, "lng": 68.2300, "name": "Goth Otho"},
}


def load_config(filename):
    with open(CONFIGS_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def call_gemini(client, system_prompt, user_prompt, config):
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


def api_get(path):
    r = requests.get(f"{API_BASE}{path}", timeout=10)
    r.raise_for_status()
    return r.json()


def api_post(path, data):
    r = requests.post(f"{API_BASE}{path}", json=data, timeout=10)
    r.raise_for_status()
    return r.json()


def post_trace(agent_id, input_summary, observations, reasoning,
               decision, action_taken, tool_calls, output_summary):
    return api_post("/api/traces/append", {
        "agent_id": agent_id, "crisis_event_id": None,
        "input_summary": input_summary, "observations": observations,
        "reasoning": reasoning, "decision": decision,
        "action_taken": action_taken, "tool_calls": tool_calls,
        "output_summary": output_summary,
    })


def haversine(lat1, lng1, lat2, lng2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ══════════════════════════════════════════════
# AGENT B1: SCANNER
# ══════════════════════════════════════════════

def run_b1(client, complaint_text):
    """Scan complaint for missing person signals."""
    print("\n" + "=" * 60)
    print("  AGENT B1 - MISSING PERSON SCANNER")
    print("=" * 60)
    print(f"  Input: {complaint_text}")
    print("-" * 60)

    config = load_config("b1_scanner.json")
    t0 = time.time()

    result = call_gemini(client, config["system_prompt"], complaint_text, config)

    latency = time.time() - t0
    print(f"\n  B1 Output ({latency:.2f}s):")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    post_trace(
        agent_id="B1_SCANNER",
        input_summary=f"Scanning: {complaint_text[:80]}",
        observations=f"Signal detected: {result.get('signal_detected')}",
        reasoning=f"Keyword matched: {result.get('keyword_matched', 'none')}",
        decision="SIGNAL_DETECTED" if result.get("signal_detected") else "NO_SIGNAL",
        action_taken="Creating missing person draft" if result.get("signal_detected") else "No action",
        tool_calls=[],
        output_summary=json.dumps(result, ensure_ascii=False)[:500],
    )

    return {"output": result, "latency_s": latency}


# ══════════════════════════════════════════════
# AGENT B2: MATCHER
# ══════════════════════════════════════════════

def run_b2(client):
    """Cross-match missing persons against unidentified camp registrations."""
    print("\n" + "=" * 60)
    print("  AGENT B2 - MISSING PERSON MATCHER")
    print("=" * 60)

    config = load_config("b2_matcher.json")
    t0 = time.time()

    # Fetch data
    missing_data = api_get("/api/missing/open")
    camps_data = api_get("/api/camps/unidentified")
    print(f"  Open missing: {missing_data['count']}")
    print(f"  Unidentified camps: {camps_data['count']}")

    # Enrich missing persons with GPS from village lookup
    for mp in missing_data["data"]:
        vid = mp.get("last_seen_village")
        if vid and vid in VILLAGE_GPS:
            mp["last_seen_lat"] = VILLAGE_GPS[vid]["lat"]
            mp["last_seen_lng"] = VILLAGE_GPS[vid]["lng"]

    user_prompt = json.dumps({
        "open_missing_persons": missing_data["data"],
        "unidentified_camp_registrations": camps_data["data"],
        "scoring_rules": config["scoring_formula"],
        "action_thresholds": config["action_thresholds"],
    }, indent=2, ensure_ascii=False)

    result = call_gemini(client, config["system_prompt"], user_prompt, config)

    latency = time.time() - t0
    print(f"\n  B2 Output ({latency:.2f}s):")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Send alerts for matches with ALERT action
    alerts_sent = 0
    for match in result.get("matches", []):
        if match.get("action") == "ALERT" and match.get("alert_message"):
            # Find the family phone for this missing person
            family_phone = "+92-300-5551001"  # Default to Hassan Ali's family
            for mp in missing_data["data"]:
                if mp.get("id") == match.get("missing_id"):
                    family_phone = mp.get("family_phone", family_phone)
                    break

            notif = api_post("/api/notify", {
                "type": "FAMILY_ALERT",
                "recipient_phone": family_phone,
                "message": match["alert_message"],
                "metadata": {
                    "missing_id": match.get("missing_id"),
                    "camp_reg_id": match.get("camp_reg_id"),
                    "match_score": match.get("score"),
                },
            })
            alerts_sent += 1
            print(f"  [ALERT] Family notified: {notif['notification']['id']} "
                  f"(score: {match.get('score')})")

    post_trace(
        agent_id="B2_MATCHER",
        input_summary=f"{missing_data['count']} missing vs {camps_data['count']} unidentified",
        observations=f"{len(result.get('matches', []))} matches found, {alerts_sent} alerts sent",
        reasoning="Cross-matched using age, proximity, and description scoring",
        decision=f"MATCHES_FOUND_{len(result.get('matches', []))}",
        action_taken=f"Sent {alerts_sent} family alerts",
        tool_calls=[
            {"tool_name": "get_open_missing", "input": "/api/missing/open",
             "output": f"{missing_data['count']} cases"},
            {"tool_name": "get_unidentified_camps", "input": "/api/camps/unidentified",
             "output": f"{camps_data['count']} registrations"},
        ],
        output_summary=json.dumps(result, ensure_ascii=False)[:500],
    )

    return {"output": result, "latency_s": latency}


# ══════════════════════════════════════════════
# AGENT B3: CLUSTER
# ══════════════════════════════════════════════

def run_b3(client, extra_missing=None):
    """Detect geographic clusters of missing persons."""
    print("\n" + "=" * 60)
    print("  AGENT B3 - MISSING PERSON CLUSTER DETECTOR")
    print("=" * 60)

    config = load_config("b3_cluster.json")
    t0 = time.time()

    missing_data = api_get("/api/missing/open")
    cases = missing_data["data"]

    # Add extra test cases if provided (for cluster scenario)
    if extra_missing:
        cases = cases + extra_missing

    # Enrich with GPS
    enriched = []
    for mp in cases:
        vid = mp.get("last_seen_village") or mp.get("last_seen_village_id")
        gps = VILLAGE_GPS.get(vid, {})
        enriched.append({
            **mp,
            "lat": gps.get("lat"),
            "lng": gps.get("lng"),
            "village_name": gps.get("name", "Unknown"),
        })

    print(f"  Total cases to analyze: {len(enriched)}")

    user_prompt = json.dumps({
        "open_missing_persons": enriched,
        "cluster_params": config["cluster_params"],
    }, indent=2, ensure_ascii=False)

    result = call_gemini(client, config["system_prompt"], user_prompt, config)

    latency = time.time() - t0
    print(f"\n  B3 Output ({latency:.2f}s):")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Send cluster alerts
    for cluster in result.get("clusters", []):
        api_post("/api/notify", {
            "type": "ESCALATION",
            "recipient_phone": "+92-300-9990001",
            "message": (f"CLUSTER ALERT: {cluster.get('case_count', 0)} missing person cases "
                        f"detected in {', '.join(cluster.get('village_ids', []))}. "
                        f"Recommended: {cluster.get('recommended_action', 'Deploy search teams')}"),
            "metadata": {"cluster_id": cluster.get("cluster_id"), "agent": "B3_CLUSTER"},
        })

    post_trace(
        agent_id="B3_CLUSTER",
        input_summary=f"Analyzing {len(enriched)} missing person cases for geographic clusters",
        observations=f"Clusters found: {result.get('clusters_found', 0)}",
        reasoning="Haversine pairwise distance with 30km radius threshold",
        decision=f"CLUSTERS_{result.get('clusters_found', 0)}",
        action_taken=f"Generated {result.get('clusters_found', 0)} cluster alerts",
        tool_calls=[],
        output_summary=json.dumps(result, ensure_ascii=False)[:500],
    )

    return {"output": result, "latency_s": latency}


# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════

def main():
    print("\n" + "#" * 60)
    print("  GAON GUARD AI - Missing Person Engine Test")
    print("  Agents: B1 (Scanner) -> B2 (Matcher) -> B3 (Cluster)")
    print("  Data: ALL SYNTHETIC")
    print("#" * 60)

    try:
        api_get("/")
        print(f"\n  [OK] API connected")
    except Exception as e:
        print(f"\n  [FAIL] Cannot connect to API at {API_BASE}: {e}")
        sys.exit(1)

    if not GEMINI_API_KEY:
        print("\n  [FAIL] GEMINI_API_KEY not set.")
        print("  Set it: $env:GEMINI_API_KEY='your-key-here'")
        sys.exit(1)

    client = genai.Client(api_key=GEMINI_API_KEY)
    print(f"  [OK] Gemini client initialized")

    total_start = time.time()

    # ── Scenario 1: B1 scans Ali Pur complaint ──
    print("\n" + "#" * 60)
    print("  SCENARIO 1: B1 scans Ali Pur complaint for missing signal")
    print("#" * 60)
    b1_result = run_b1(
        client,
        "Ali Pur mein 2 din se pani khara hai, bachay diarrhea se "
        "beemar hain aur bacha nazar nahi aa raha"
    )

    # ── Scenario 2: B2 matches Hassan Ali to CAMP_REG_020 ──
    print("\n" + "#" * 60)
    print("  SCENARIO 2: B2 matches missing persons to camp registrations")
    print("#" * 60)
    b2_result = run_b2(client)

    # ── Scenario 3: B3 detects cluster ──
    print("\n" + "#" * 60)
    print("  SCENARIO 3: B3 cluster detection (with extra test cases)")
    print("#" * 60)

    # Inject 3 extra missing persons from neighboring villages near Ali Pur
    extra_cases = [
        {
            "id": "MP_TEST_A", "name": "Amina Bibi", "age": 45, "gender": "female",
            "last_seen_village": "VIL_027", "last_seen_village_id": "VIL_027",
            "last_seen_time": "2026-05-16T15:00:00+05:00",
            "description": "White dupatta, was collecting belongings",
            "status": "OPEN",
        },
        {
            "id": "MP_TEST_B", "name": "Yousuf Khan", "age": 60, "gender": "male",
            "last_seen_village": "VIL_050", "last_seen_village_id": "VIL_050",
            "last_seen_time": "2026-05-16T16:00:00+05:00",
            "description": "Grey beard, brown shalwar kameez, uses cane",
            "status": "OPEN",
        },
        {
            "id": "MP_TEST_C", "name": "Sadia Noor", "age": 14, "gender": "female",
            "last_seen_village": "VIL_032", "last_seen_village_id": "VIL_032",
            "last_seen_time": "2026-05-16T17:00:00+05:00",
            "description": "School uniform, blue bag",
            "status": "OPEN",
        },
    ]
    b3_result = run_b3(client, extra_missing=extra_cases)

    total_latency = time.time() - total_start

    # ── Summary ──
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    print(f"  B1 (Scanner):  {b1_result['latency_s']:.2f}s")
    print(f"    Signal detected: {b1_result['output'].get('signal_detected')}")
    print(f"    Keyword: {b1_result['output'].get('keyword_matched')}")
    print(f"  B2 (Matcher):  {b2_result['latency_s']:.2f}s")
    alerts = [m for m in b2_result["output"].get("matches", []) if m.get("action") == "ALERT"]
    reviews = [m for m in b2_result["output"].get("matches", []) if m.get("action") == "REVIEW"]
    print(f"    ALERTs: {len(alerts)}, REVIEWs: {len(reviews)}")
    for a in alerts:
        print(f"    -> {a.get('missing_id')} <-> {a.get('camp_reg_id')} (score: {a.get('score')})")
    print(f"  B3 (Cluster):  {b3_result['latency_s']:.2f}s")
    print(f"    Clusters found: {b3_result['output'].get('clusters_found', 0)}")
    for c in b3_result["output"].get("clusters", []):
        print(f"    -> {c.get('cluster_id')}: {c.get('case_count')} cases in "
              f"{', '.join(c.get('village_ids', []))}")
    print(f"  Total: {total_latency:.2f}s")
    print("=" * 60)

    # Save trace
    trace = {
        "_doc": "Gaon Guard AI - B1->B2->B3 Pipeline Trace",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scenario_1_scanner": {
            "input": "Ali Pur demo complaint",
            "output": b1_result["output"], "latency_s": b1_result["latency_s"]
        },
        "scenario_2_matcher": {
            "output": b2_result["output"], "latency_s": b2_result["latency_s"]
        },
        "scenario_3_cluster": {
            "extra_cases_injected": 3,
            "output": b3_result["output"], "latency_s": b3_result["latency_s"]
        },
        "total_latency_s": total_latency,
        "data_type": "SYNTHETIC",
    }
    out_path = OUTPUT_DIR / "b1_b3_trace.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2, ensure_ascii=False)
    print(f"\n  Trace saved to: {out_path}")


if __name__ == "__main__":
    main()
