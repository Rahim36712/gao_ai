"""
Gaon Guard AI - Agent Test Script: C1 (Registry) -> C2 (Audit) -> C3 (GeoVerify)
Tests the Aid Accountability engine pipeline.

Usage:
    1. Start the FastAPI server: uvicorn main:app --reload --port 8000
    2. Set GEMINI_API_KEY env var
    3. Run: python test_c1_c3.py

All data is SYNTHETIC DEMO DATA.
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from google import genai
from google.genai import types

# Add backend to path for audit_pipeline import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
from audit_pipeline import run_c1, run_c2, run_c3, run_full_audit

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

API_BASE = os.environ.get("API_BASE", "http://localhost:8000")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

OUTPUT_DIR = Path(__file__).resolve().parent / "test_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def api_get(path):
    r = requests.get(f"{API_BASE}{path}", timeout=10)
    r.raise_for_status()
    return r.json()


# ══════════════════════════════════════════════
# SCENARIO 1: Valid entry — should PASS
# ══════════════════════════════════════════════

def scenario_1_valid(client):
    """Valid distribution entry with clean data."""
    print("\n" + "#" * 60)
    print("  SCENARIO 1: Valid Entry (should PASS all checks)")
    print("#" * 60)

    beneficiary = {
        "cnic": "42301-1234567-1",
        "head_name": "Abdul Rehman",
        "village_id": "VIL_002",
        "household_size": 6,
        "gps_home": {"lat": 26.7320, "lng": 67.7750},
        "damage_level": "MODERATE",
    }

    distribution = {
        "village_id": "VIL_002",
        "total_tents": 25,
        "total_ration_packs": 80,
        "total_cash_pkr": 250000,
        "registered_households": 120,
        "officer_id": "TEAM_004",
        "invoice_prices": {
            "tent_pkr": 15000,
            "ration_pack_pkr": 4500,
        },
        "gps_distribution": {"lat": 26.7350, "lng": 67.7800},
    }

    t0 = time.time()

    print("\n  -- C1: Registry Validation --")
    c1 = run_c1(client, beneficiary)
    print(f"  Valid: {c1['output'].get('valid')} ({c1['latency_s']:.2f}s)")
    print(f"  Entitlement: {json.dumps(c1['output'].get('calculated_entitlement', {}))}")

    print("\n  -- C2: Audit Check --")
    c2 = run_c2(client, distribution)
    print(f"  Status: {c2['output'].get('audit_status')} ({c2['latency_s']:.2f}s)")
    print(f"  Flags: {c2['output'].get('anomaly_flags')}")

    print("\n  -- C3: GPS Verify --")
    c3 = run_c3(client, distribution["gps_distribution"], "VIL_002")
    print(f"  Verdict: {c3['output'].get('verdict')} ({c3['latency_s']:.2f}s)")
    print(f"  Distance: {c3['output'].get('distance_km', '?')}km")

    latency = time.time() - t0
    return {
        "c1": c1["output"], "c2": c2["output"], "c3": c3["output"],
        "latency_s": latency,
    }


# ══════════════════════════════════════════════
# SCENARIO 2: Basti Malook 500 tents -> QUANTITY_ANOMALY
# ══════════════════════════════════════════════

def scenario_2_quantity_anomaly(client):
    """500 tents for 120 households -> items_per_household = 4.17."""
    print("\n" + "#" * 60)
    print("  SCENARIO 2: Basti Malook 500 Tents (QUANTITY_ANOMALY)")
    print("#" * 60)

    distribution = {
        "village_id": "VIL_002",
        "total_tents": 500,
        "total_ration_packs": 200,
        "total_cash_pkr": 2500000,
        "registered_households": 120,
        "officer_id": "TEAM_004",
        "invoice_prices": {
            "tent_pkr": 15000,
            "ration_pack_pkr": 4500,
        },
        "gps_distribution": {"lat": 26.7350, "lng": 67.7800},
    }

    t0 = time.time()
    c2 = run_c2(client, distribution)
    latency = time.time() - t0

    print(f"\n  C2 Output ({latency:.2f}s):")
    print(json.dumps(c2["output"], indent=2, ensure_ascii=False))

    # Validate
    flags = c2["output"].get("anomaly_flags", [])
    has_quantity = any("QUANTITY" in f for f in flags)
    print(f"\n  Validation:")
    print(f"    Has QUANTITY_ANOMALY: {has_quantity}")
    print(f"    Audit status: {c2['output'].get('audit_status')}")
    print(f"    Escalation brief: {c2['output'].get('escalation_brief', 'N/A')[:200]}")

    return {"c2": c2["output"], "latency_s": latency}


# ══════════════════════════════════════════════
# SCENARIO 3: GPS 28km off -> SEVERE_LOCATION_MISMATCH
# ══════════════════════════════════════════════

def scenario_3_gps_mismatch(client):
    """Distribution GPS far from village centroid."""
    print("\n" + "#" * 60)
    print("  SCENARIO 3: GPS Mismatch (SEVERE_LOCATION_MISMATCH)")
    print("#" * 60)

    # 27.1234, 68.5678 is far from Basti Malook (26.7320, 67.7750)
    gps_dist = {"lat": 27.1234, "lng": 68.5678}

    t0 = time.time()
    c3 = run_c3(client, gps_dist, "VIL_002")
    latency = time.time() - t0

    print(f"\n  C3 Output ({latency:.2f}s):")
    print(json.dumps(c3["output"], indent=2, ensure_ascii=False))

    # Validate
    print(f"\n  Validation:")
    print(f"    Verdict: {c3['output'].get('verdict')}")
    print(f"    Distance: {c3['output'].get('distance_km', '?')}km")
    print(f"    Escalation required: {c3['output'].get('escalation_required')}")

    return {"c3": c3["output"], "latency_s": latency}


# ══════════════════════════════════════════════
# SCENARIO 4: Duplicate CNIC
# ══════════════════════════════════════════════

def scenario_4_duplicate(client):
    """Submit a CNIC that already exists in the registry."""
    print("\n" + "#" * 60)
    print("  SCENARIO 4: Duplicate CNIC Detection")
    print("#" * 60)

    # Fetch existing registry to find a CNIC to duplicate
    try:
        existing = api_get("/api/beneficiaries/VIL_002")
        existing_registry = existing["data"]
        # Pick the first CNIC from existing records
        duplicate_cnic = existing_registry[0].get("cnic", "42301-0000001-1")
        existing_name = existing_registry[0].get("head_name", "Unknown")
    except Exception:
        duplicate_cnic = "42301-0000001-1"
        existing_name = "Test Existing"
        existing_registry = [{"cnic": duplicate_cnic, "head_name": existing_name}]

    print(f"  Using duplicate CNIC: {duplicate_cnic} (belongs to: {existing_name})")

    new_entry = {
        "cnic": duplicate_cnic,
        "head_name": "Fake Person Duplicate",
        "village_id": "VIL_002",
        "household_size": 4,
        "gps_home": {"lat": 26.7400, "lng": 67.7900},
        "damage_level": "SEVERE",
    }

    t0 = time.time()
    c1 = run_c1(client, new_entry, existing_registry=existing_registry)
    latency = time.time() - t0

    print(f"\n  C1 Output ({latency:.2f}s):")
    print(json.dumps(c1["output"], indent=2, ensure_ascii=False))

    # Validate
    print(f"\n  Validation:")
    print(f"    Valid: {c1['output'].get('valid')}")
    print(f"    Duplicate detected: {c1['output'].get('duplicate_detected')}")
    print(f"    Rejection reasons: {c1['output'].get('rejection_reasons')}")

    return {"c1": c1["output"], "latency_s": latency}


# ══════════════════════════════════════════════
# BONUS: Full pipeline with all flags firing
# ══════════════════════════════════════════════

def scenario_bonus_full_pipeline(client):
    """Combined audit: quantity anomaly + GPS mismatch -> FRAUD_RISK."""
    print("\n" + "#" * 60)
    print("  BONUS: Full Pipeline Audit (multiple flags)")
    print("#" * 60)

    distribution = {
        "village_id": "VIL_002",
        "total_tents": 500,
        "total_ration_packs": 400,
        "total_cash_pkr": 5000000,
        "registered_households": 120,
        "officer_id": "TEAM_SUSPECT",
        "invoice_prices": {
            "tent_pkr": 25000,
            "ration_pack_pkr": 8000,
        },
        "gps_distribution": {"lat": 27.1234, "lng": 68.5678},
    }

    beneficiary = {
        "cnic": "42301-9999999-9",
        "head_name": "Full Pipeline Test",
        "village_id": "VIL_002",
        "household_size": 5,
        "gps_home": {"lat": 26.7320, "lng": 67.7750},
        "damage_level": "SEVERE",
    }

    t0 = time.time()
    result = run_full_audit(client, distribution, beneficiary)
    latency = time.time() - t0

    final = result["final"]
    print(f"\n  Final Result ({latency:.2f}s):")
    print(f"    Status: {final['audit_status']}")
    print(f"    All flags: {final['all_flags']}")
    print(f"    Escalation: {final['escalation_required']}")
    print(f"    Audit log ID: {final['audit_log_id']}")

    return {"final": final, "latency_s": latency}


# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════

def main():
    print("\n" + "#" * 60)
    print("  GAON GUARD AI - Aid Accountability Engine Test")
    print("  Agents: C1 (Registry) -> C2 (Audit) -> C3 (GeoVerify)")
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

    s1 = scenario_1_valid(client)
    s2 = scenario_2_quantity_anomaly(client)
    s3 = scenario_3_gps_mismatch(client)
    s4 = scenario_4_duplicate(client)
    s5 = scenario_bonus_full_pipeline(client)

    total_latency = time.time() - total_start

    # Summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    print(f"  Scenario 1 (Valid):            {s1['latency_s']:.2f}s  "
          f"C2={s1['c2'].get('audit_status')}")
    print(f"  Scenario 2 (500 Tents):        {s2['latency_s']:.2f}s  "
          f"C2={s2['c2'].get('audit_status')} "
          f"Flags={s2['c2'].get('anomaly_flags')}")
    print(f"  Scenario 3 (GPS Off):          {s3['latency_s']:.2f}s  "
          f"C3={s3['c3'].get('verdict')}")
    print(f"  Scenario 4 (Duplicate CNIC):   {s4['latency_s']:.2f}s  "
          f"Dup={s4['c1'].get('duplicate_detected')}")
    print(f"  Bonus (Full Pipeline):         {s5['latency_s']:.2f}s  "
          f"Final={s5['final']['audit_status']} "
          f"Flags={s5['final']['all_flags']}")
    print(f"  Total: {total_latency:.2f}s")
    print("=" * 60)

    # Save trace
    trace = {
        "_doc": "Gaon Guard AI - C1->C2->C3 Pipeline Trace",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scenario_1_valid": s1,
        "scenario_2_quantity_anomaly": s2,
        "scenario_3_gps_mismatch": s3,
        "scenario_4_duplicate_cnic": s4,
        "scenario_bonus_full_pipeline": {"final": s5["final"], "latency_s": s5["latency_s"]},
        "total_latency_s": total_latency,
        "data_type": "SYNTHETIC",
    }
    out_path = OUTPUT_DIR / "c1_c3_trace.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2, ensure_ascii=False)
    print(f"\n  Trace saved to: {out_path}")


if __name__ == "__main__":
    main()
