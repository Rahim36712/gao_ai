"""
Gaon Guard AI — Firestore Seed Script
Seeds 3 pre-staged demo scenarios into Firestore.

Usage:
    python firestore_seed.py

Requires: backend/serviceAccountKey.json or GOOGLE_APPLICATION_CREDENTIALS env var.
All data is SYNTHETIC DEMO DATA.
"""

import sys
from datetime import datetime, timezone
from firebase_config import get_db
from google.cloud.firestore_v1 import SERVER_TIMESTAMP


def seed_crisis_events(db):
    """Seed: Ali Pur crisis event — status WATCHLIST, ready to activate."""
    doc_data = {
        "id": "CRISIS_001",
        "status": "WATCHLIST",
        "location_village_id": "VIL_001",
        "signals": [
            "WEATHER_RED_Larkana",
            "ROAD_BLOCKED_VIL_001",
            "HEALTH_SPIKE_BHU_Larkana_03",
        ],
        "confidence_level": 0.87,
        "severity_score": 8.5,
        "created_at": SERVER_TIMESTAMP,
        "updated_at": SERVER_TIMESTAMP,
        "source": "SIGNAL_FUSION",
        "raw_complaint_text": (
            "Heavy rainfall in Larkana district. Ali Pur main road blocked. "
            "BHU reports 12 diarrhea cases in 7 days. Multiple flood history events."
        ),
        "agent_trace_ref": "TRACE_SEED_001",
    }
    db.collection("crisis_events").document("CRISIS_001").set(doc_data)
    print("[✓] crisis_events/CRISIS_001  — Ali Pur WATCHLIST event seeded")
    return doc_data


def seed_missing_persons_live(db):
    """Seed: Hassan Ali missing person case — status OPEN."""
    doc_data = {
        "id": "MP_LIVE_001",
        "name": "Hassan Ali",
        "age": 12,
        "gender": "male",
        "last_seen_village_id": "VIL_001",
        "last_seen_time": datetime(2026, 5, 16, 14, 30, tzinfo=timezone.utc),
        "description": (
            "Blue shalwar kameez, black hair, approx 4ft5in, thin build, "
            "Sindhi speaking"
        ),
        "family_phone": "+92-300-5551001",
        "status": "OPEN",
        "match_score": None,
        "matched_camp_id": None,
        "alert_sent_at": None,
    }
    db.collection("missing_persons_live").document("MP_LIVE_001").set(doc_data)
    print("[✓] missing_persons_live/MP_LIVE_001  — Hassan Ali OPEN case seeded")
    return doc_data


def seed_aid_distribution(db):
    """Seed: Basti Malook aid distribution placeholder — status PENDING."""
    doc_data = {
        "id": "AID_SEED_001",
        "beneficiary_id": "BEN_0001",
        "village_id": "VIL_002",
        "officer_id": "TEAM_002",
        "items_distributed": {
            "tents": 1,
            "ration_packs": 2,
            "cash_pkr": 25000,
        },
        "gps_distribution": {
            "lat": 26.7320,
            "lng": 67.7750,
        },
        "timestamp": SERVER_TIMESTAMP,
        "audit_status": "PENDING",
        "anomaly_flags": [],
        "audit_brief": "Awaiting audit engine processing.",
    }
    db.collection("aid_distribution_log").document("AID_SEED_001").set(doc_data)
    print("[✓] aid_distribution_log/AID_SEED_001  — Basti Malook PENDING distribution seeded")
    return doc_data


def seed_agent_trace(db):
    """Seed: Initial agent trace for the Ali Pur crisis detection."""
    doc_data = {
        "id": "TRACE_SEED_001",
        "crisis_event_id": "CRISIS_001",
        "agent_id": "ENGINE_TRIAGE",
        "timestamp": SERVER_TIMESTAMP,
        "input_summary": (
            "Weather API returned RED alert for Larkana (95.4mm/24hr). "
            "Road status API shows VIL_001 BLOCKED. Health API shows "
            "BHU_Larkana_03 with 12 diarrhea cases."
        ),
        "observations": (
            "Three independent signals converging on Ali Pur: severe rainfall, "
            "road blockage, and health surveillance spike. Village has HIGH_FLOOD "
            "risk zone with 4 prior flood events."
        ),
        "reasoning": (
            "Signal fusion detected multi-domain crisis indicators. "
            "Weather severity exceeds RED threshold (>80mm/24hr). "
            "Road blockage isolates the village from BHU access. "
            "Health spike suggests contaminated water supply. "
            "Historical flood pattern confirms vulnerability. "
            "Confidence: 87% based on signal convergence."
        ),
        "decision": "CREATE_CRISIS_EVENT at WATCHLIST level",
        "action_taken": "Created CRISIS_001 with severity_score 8.5",
        "tool_calls": [
            {
                "tool_name": "get_weather",
                "input": {"district": "Larkana"},
                "output": "rainfall_mm_24hr=95.4, flood_alert=RED",
            },
            {
                "tool_name": "get_road_status",
                "input": {"village_id": "VIL_001"},
                "output": "main_road_status=BLOCKED",
            },
            {
                "tool_name": "get_health_report",
                "input": {"bhu_id": "BHU_Larkana_03"},
                "output": "diarrhea_cases_7day=12, cholera_alerts=1",
            },
        ],
        "output_summary": (
            "Crisis event CRISIS_001 created for Ali Pur at WATCHLIST status. "
            "Severity 8.5/10. Awaiting DC review for activation."
        ),
        "error_recovery": None,
    }
    db.collection("agent_traces").document("TRACE_SEED_001").set(doc_data)
    print("[✓] agent_traces/TRACE_SEED_001  — Triage engine trace seeded")
    return doc_data


def main():
    print("=" * 60)
    print("  Gaon Guard AI — Firestore Seed Script")
    print("  All data is SYNTHETIC DEMO DATA")
    print("=" * 60)
    print()

    try:
        db = get_db()
        print("[✓] Firebase connection established\n")
    except FileNotFoundError as e:
        print(f"[✗] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[✗] Firebase initialization failed: {e}")
        sys.exit(1)

    # Seed all scenarios
    seed_crisis_events(db)
    seed_missing_persons_live(db)
    seed_aid_distribution(db)
    seed_agent_trace(db)

    print()
    print("=" * 60)
    print("  Seeding complete! 4 documents written to Firestore.")
    print("  Collections populated:")
    print("    - crisis_events       (1 doc)")
    print("    - missing_persons_live (1 doc)")
    print("    - aid_distribution_log (1 doc)")
    print("    - agent_traces         (1 doc)")
    print("=" * 60)


if __name__ == "__main__":
    main()
