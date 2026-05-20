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
OUTPUT_DIR = Path(os.environ.get("GG_TEST_OUTPUT_DIR", r"D:\gaon_guard_test_outputs"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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


from gemini_utils import GeminiCallError, call_gemini


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


def _tokens(*values):
    stopwords = {"and", "the", "with", "from", "near", "does", "not", "know"}
    words = set()
    for value in values:
        for word in str(value or "").lower().replace("-", " ").replace(",", " ").split():
            cleaned = "".join(ch for ch in word if ch.isalnum())
            if len(cleaned) >= 3 and cleaned not in stopwords:
                words.add(cleaned)
    return words


def _age_points(missing, camp):
    try:
        diff = abs(int(missing.get("age")) - int(camp.get("approx_age")))
    except (TypeError, ValueError):
        return 0
    if diff <= 3:
        return 30
    if diff <= 6:
        return 15
    return 0


def _proximity_points(missing, camp):
    if missing.get("last_seen_lat") is None or missing.get("last_seen_lng") is None:
        return 0
    distance = haversine(
        missing["last_seen_lat"],
        missing["last_seen_lng"],
        camp.get("lat", 0),
        camp.get("lng", 0),
    )
    return round(max(0, 40 * (1 - distance / 20)), 1)


def _description_points(missing, camp):
    missing_tokens = _tokens(missing.get("name"), missing.get("gender"), missing.get("description"))
    camp_tokens = _tokens(camp.get("gender"), camp.get("description"))
    if not missing_tokens or not camp_tokens:
        return 0
    overlap = missing_tokens & camp_tokens
    base = min(24, len(overlap) * 6)
    gender_bonus = 6 if missing.get("gender") and missing.get("gender") == camp.get("gender") else 0
    return min(30, base + gender_bonus)


def local_b2_fallback(missing_persons, camp_registrations, reason):
    matches = []
    for missing in missing_persons:
        for camp in camp_registrations:
            age_points = _age_points(missing, camp)
            proximity_points = _proximity_points(missing, camp)
            desc_points = _description_points(missing, camp)
            score = round(age_points + proximity_points + desc_points, 1)
            if score >= 71:
                action = "ALERT"
            elif score >= 40:
                action = "REVIEW"
            else:
                action = "NO_ACTION"
            matches.append({
                "missing_id": missing.get("id"),
                "camp_reg_id": camp.get("id"),
                "score": score,
                "age_points": age_points,
                "proximity_points": proximity_points,
                "desc_points": desc_points,
                "action": action,
                "alert_message": (
                    f"Possible match for {missing.get('name')} at {camp.get('camp_id')}."
                    if action == "ALERT" else ""
                ),
            })

    matches.sort(key=lambda item: (-item["score"], item["missing_id"] or "", item["camp_reg_id"] or ""))
    return {
        "matches": matches[:3],
        "fallback_used": True,
        "fallback_reason": str(reason)[:220],
    }


def local_b1_fallback(complaint_text):
    text = str(complaint_text or "").lower()
    keywords = ["laapata", "nahi mil", "nazar nahi", "gum", "missing", "lost", "bacha"]
    signal_detected = any(keyword in text for keyword in keywords)
    child_mentioned = "bacha" in text or "child" in text or "children" in text
    return {
        "signal_detected": signal_detected,
        "extracted_name": None,
        "extracted_age_estimate": None,
        "risk_level": "HIGH" if child_mentioned else "MEDIUM",
        "fallback_used": True,
        "fallback_reason": "Gemini unavailable",
    }


def local_b3_fallback(enriched_cases, reason):
    min_cases = 3
    radius_km = 30
    indexed_cases = [
        case for case in enriched_cases
        if case.get("lat") is not None and case.get("lng") is not None
    ]
    adjacency = {idx: set() for idx in range(len(indexed_cases))}
    for idx, case in enumerate(indexed_cases):
        for other_idx in range(idx + 1, len(indexed_cases)):
            other = indexed_cases[other_idx]
            distance = haversine(case["lat"], case["lng"], other["lat"], other["lng"])
            if distance <= radius_km:
                adjacency[idx].add(other_idx)
                adjacency[other_idx].add(idx)

    clusters = []
    visited = set()
    for idx in range(len(indexed_cases)):
        if idx in visited:
            continue
        stack = [idx]
        component = set()
        while stack:
            current = stack.pop()
            if current in component:
                continue
            component.add(current)
            stack.extend(adjacency[current] - component)
        visited.update(component)
        if len(component) < min_cases:
            continue

        cases = [indexed_cases[item] for item in sorted(component)]
        village_ids = sorted({
            case.get("last_seen_village_id") or case.get("last_seen_village")
            for case in cases
            if case.get("last_seen_village_id") or case.get("last_seen_village")
        })
        centroid_lat = round(sum(case["lat"] for case in cases) / len(cases), 5)
        centroid_lng = round(sum(case["lng"] for case in cases) / len(cases), 5)
        clusters.append({
            "cluster_id": f"B3_LOCAL_{len(clusters) + 1:03d}",
            "village_ids": village_ids,
            "case_count": len(cases),
            "centroid_lat": centroid_lat,
            "centroid_lng": centroid_lng,
            "recommended_action": "Deploy search teams and verify camp registrations",
            "alert_recipients": ["RESCUE_1122", "DISTRICT_OFFICER"],
        })

    return {
        "clusters_found": len(clusters),
        "clusters": clusters,
        "fallback_used": True,
        "fallback_reason": str(reason)[:220],
    }


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

    try:
        if client is None:
            raise GeminiCallError("GEMINI_API_KEY not set")
        result = call_gemini(client, config["system_prompt"], complaint_text, config)
        if result.get("fallback_required"):
            result = local_b1_fallback(complaint_text)
            result["fallback_reason"] = result.get("fallback_reason") or "Gemini unavailable"
        else:
            result.setdefault("fallback_used", False)
            result.setdefault("fallback_reason", "")
    except GeminiCallError as e:
        print(f"  [WARN] B1 Gemini failed cleanly: {e}")
        print("  [FALLBACK] Using deterministic local B1 scanner")
        result = local_b1_fallback(complaint_text)
    except Exception as e:
        print(f"  [WARN] B1 scanner recovered from error: {e}")
        print("  [FALLBACK] Using deterministic local B1 scanner")
        result = local_b1_fallback(complaint_text)

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

    try:
        if client is None:
            raise GeminiCallError("GEMINI_API_KEY not set")
        result = call_gemini(client, config["system_prompt"], user_prompt, config)
        if result.get("fallback_required") or not isinstance(result.get("matches"), list):
            result = local_b2_fallback(
                missing_data["data"],
                camps_data["data"],
                result.get("error", "Gemini JSON fallback required"),
            )
        else:
            result.setdefault("fallback_used", False)
            result.setdefault("fallback_reason", "")
    except GeminiCallError as e:
        print(f"  [WARN] B2 Gemini failed cleanly: {e}")
        print("  [FALLBACK] Using deterministic local B2 matcher")
        result = local_b2_fallback(missing_data["data"], camps_data["data"], e)
    except Exception as e:
        print(f"  [WARN] B2 matcher recovered from error: {e}")
        print("  [FALLBACK] Using deterministic local B2 matcher")
        result = local_b2_fallback(missing_data["data"], camps_data["data"], e)

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

    try:
        if client is None:
            raise GeminiCallError("GEMINI_API_KEY not set")
        result = call_gemini(client, config["system_prompt"], user_prompt, config)
        if result.get("fallback_required") or not isinstance(result.get("clusters"), list):
            result = local_b3_fallback(
                enriched,
                result.get("error", "Gemini cluster fallback required"),
            )
        else:
            result.setdefault("fallback_used", False)
            result.setdefault("fallback_reason", "")
    except GeminiCallError as e:
        print(f"  [WARN] B3 Gemini failed cleanly: {e}")
        print("  [FALLBACK] Using deterministic local B3 cluster detector")
        result = local_b3_fallback(enriched, e)
    except Exception as e:
        print(f"  [WARN] B3 cluster recovered from error: {e}")
        print("  [FALLBACK] Using deterministic local B3 cluster detector")
        result = local_b3_fallback(enriched, e)

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

    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
        print(f"  [OK] Gemini client initialized")
    else:
        client = None
        print("  [WARN] GEMINI_API_KEY not set; using local fallbacks")

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
