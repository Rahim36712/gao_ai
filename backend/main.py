"""
Gaon Guard AI — FastAPI Backend
3-Engine Agentic Crisis Intelligence System for Rural Pakistan
Google Antigravity Hackathon (Challenge 3)

All data served by this API is SYNTHETIC DEMO DATA.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import json

# ──────────────────────────────────────────────
# App setup
# ──────────────────────────────────────────────

app = FastAPI(
    title="Gaon Guard AI — Crisis Intelligence API",
    description="Mock data API for the Gaon Guard AI hackathon demo. All data is SYNTHETIC.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Static data loading (JSON files)
# ──────────────────────────────────────────────

DATA_DIR = Path(__file__).resolve().parent.parent / "mock_data"

def _load(filename: str) -> list[dict]:
    """Load a JSON dataset, stripping the _comment sentinel record."""
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [r for r in raw if not r.get("_comment")]

# Pre-load all datasets into memory
villages: list[dict] = _load("villages.json")
weather: list[dict] = _load("weather.json")
teams: list[dict] = _load("teams.json")
health_reports: list[dict] = _load("health_reports.json")
missing_persons: list[dict] = _load("missing_persons.json")
camp_registrations: list[dict] = _load("camp_registrations.json")
beneficiary_registry: list[dict] = _load("beneficiary_registry.json")
market_prices: list[dict] = _load("market_prices.json")
road_status: list[dict] = _load("road_status.json")

# ──────────────────────────────────────────────
# Firebase / Firestore (lazy init)
# ──────────────────────────────────────────────

_firestore_db = None
_firestore_available = False
_firestore_init_attempted = False


def _get_db():
    """Lazy-init Firestore. Returns None if Firebase is not configured."""
    global _firestore_db, _firestore_available, _firestore_init_attempted
    if _firestore_db is not None:
        return _firestore_db
    if _firestore_init_attempted:
        return None
    _firestore_init_attempted = True
    try:
        from firebase_config import get_db
        _firestore_db = get_db()
        _firestore_available = True
        return _firestore_db
    except Exception as e:
        err_msg = str(e).encode("ascii", errors="replace").decode("ascii")
        print(f"[WARN] Firestore not available: {err_msg}")
        print("[WARN] Firestore endpoints will return mock responses.")
        _firestore_available = False
        return None


# ──────────────────────────────────────────────
# Middleware — synthetic data header
# ──────────────────────────────────────────────

@app.middleware("http")
async def add_synthetic_header(request, call_next):
    response = await call_next(request)
    response.headers["X-Data-Type"] = "SYNTHETIC"
    return response

# ──────────────────────────────────────────────
# Pydantic models for new endpoints
# ──────────────────────────────────────────────

class CrisisCreateRequest(BaseModel):
    location_village_id: str
    signals: list[str] = Field(default_factory=list)
    confidence_level: float = 0.5
    severity_score: float = 5.0
    source: str = "MANUAL_REPORT"
    raw_complaint_text: str = ""


class DispatchStatusUpdate(BaseModel):
    status: str = Field(..., description="New status")
    gps_checkin: Optional[dict] = None
    field_note: Optional[str] = None
    escalation_reason: Optional[str] = None


class MissingPersonReport(BaseModel):
    name: str
    age: int
    gender: str
    last_seen_village_id: str
    last_seen_time: Optional[str] = None
    description: str = ""
    family_phone: str = ""


class AuditLogEntry(BaseModel):
    beneficiary_id: str
    village_id: str
    officer_id: str
    items_distributed: dict = Field(default_factory=lambda: {"tents": 0, "ration_packs": 0, "cash_pkr": 0})
    gps_distribution: dict = Field(default_factory=lambda: {"lat": 0.0, "lng": 0.0})
    anomaly_flags: list[str] = Field(default_factory=list)
    audit_brief: str = ""


class AgentTraceEntry(BaseModel):
    crisis_event_id: Optional[str] = None
    agent_id: str
    input_summary: str = ""
    observations: str = ""
    reasoning: str = ""
    decision: str = ""
    action_taken: str = ""
    tool_calls: list[dict] = Field(default_factory=list)
    output_summary: str = ""
    error_recovery: Optional[str] = None


class NotifyRequest(BaseModel):
    type: str
    recipient_phone: str
    message: str
    metadata: Optional[dict] = Field(default_factory=dict)


# ──────────────────────────────────────────────
# Valid enum values for validation
# ──────────────────────────────────────────────

VALID_CRISIS_STATUSES = {"WATCHLIST", "ACTIVE", "RESOLVED", "ESCALATED"}

VALID_DISPATCH_STATUSES = {
    "ASSIGNED", "ACCEPTED", "EN_ROUTE", "ARRIVED",
    "EVIDENCE_UPLOADED", "CONFIRMED", "DISPUTED", "ESCALATED",
}

VALID_MISSING_STATUSES = {"OPEN", "PENDING_MATCH", "CONFIRMED_FOUND", "DECEASED"}

VALID_AUDIT_STATUSES = {"PENDING", "PASS", "ANOMALY", "FRAUD_RISK"}

VALID_NOTIFICATION_TYPES = {
    "FAMILY_ALERT", "TEAM_DISPATCH", "TEAM_REMINDER",
    "ESCALATION", "AUDIT_FLAG",
}


# ══════════════════════════════════════════════
# SECTION 1: Static data endpoints (unchanged)
# ══════════════════════════════════════════════

@app.get("/")
async def root():
    return {
        "service": "Gaon Guard AI — Crisis Intelligence API",
        "status": "running",
        "data_type": "SYNTHETIC",
        "firestore_connected": _firestore_available,
        "endpoints": {
            "static_data": [
                "/api/villages",
                "/api/villages/{village_id}",
                "/api/weather/{district}",
                "/api/roads/{village_id}",
                "/api/health/{bhu_id}",
                "/api/teams/available",
                "/api/camps/unidentified",
                "/api/prices",
                "/api/missing/open",
                "/api/beneficiaries/{village_id}",
                "/api/demo/load_scenario",
            ],
            "firestore": [
                "POST /api/crisis/create",
                "PATCH /api/dispatch/{ticket_id}/status",
                "POST /api/missing/report",
                "POST /api/audit/log",
                "POST /api/traces/append",
                "POST /api/notify",
            ],
        },
    }


@app.get("/api/villages")
async def get_villages():
    """Return all 50 villages."""
    return {"count": len(villages), "data": villages}


@app.get("/api/villages/{village_id}")
async def get_village(village_id: str):
    """Return a single village by ID."""
    for v in villages:
        if v["id"] == village_id:
            return v
    raise HTTPException(status_code=404, detail=f"Village {village_id} not found")


@app.get("/api/weather/{district}")
async def get_weather(district: str):
    """Return weather data for a specific district."""
    for w in weather:
        if w["district"].lower() == district.lower():
            return w
    raise HTTPException(status_code=404, detail=f"Weather data for district '{district}' not found")


@app.get("/api/roads/{village_id}")
async def get_road_status(village_id: str):
    """Return road status for a specific village."""
    for r in road_status:
        if r["village_id"] == village_id:
            return r
    raise HTTPException(status_code=404, detail=f"Road status for {village_id} not found")


@app.get("/api/health/{bhu_id}")
async def get_health_report(bhu_id: str):
    """Return health report for a specific BHU."""
    for h in health_reports:
        if h["bhu_id"] == bhu_id:
            return h
    raise HTTPException(status_code=404, detail=f"Health report for {bhu_id} not found")


@app.get("/api/teams/available")
async def get_available_teams():
    """Return all teams with AVAILABLE status."""
    available = [t for t in teams if t["status"] == "AVAILABLE"]
    return {"count": len(available), "data": available}


@app.get("/api/camps/unidentified")
async def get_unidentified_camp_registrations():
    """Return all UNIDENTIFIED camp registrations."""
    unidentified = [c for c in camp_registrations if c["status"] == "UNIDENTIFIED"]
    return {"count": len(unidentified), "data": unidentified}


@app.get("/api/prices")
async def get_market_prices():
    """Return all market prices."""
    return {"count": len(market_prices), "data": market_prices}


@app.get("/api/missing/open")
async def get_open_missing_persons():
    """Return all OPEN missing person cases."""
    open_cases = [m for m in missing_persons if m["status"] == "OPEN"]
    return {"count": len(open_cases), "data": open_cases}


@app.get("/api/beneficiaries/{village_id}")
async def get_beneficiaries(village_id: str):
    """Return all beneficiary records for a specific village."""
    village_bens = [b for b in beneficiary_registry if b["village_id"] == village_id]
    if not village_bens:
        raise HTTPException(status_code=404, detail=f"No beneficiaries found for {village_id}")
    return {"count": len(village_bens), "data": village_bens}


@app.post("/api/demo/load_scenario")
async def load_demo_scenario():
    """
    Pre-load the full Ali Pur demo scenario into a single response.
    This aggregates all data relevant to the Ali Pur (VIL_001) crisis scenario.
    """
    ali_pur = next((v for v in villages if v["id"] == "VIL_001"), None)
    larkana_weather = next((w for w in weather if w["district"] == "Larkana"), None)
    ali_pur_road = next((r for r in road_status if r["village_id"] == "VIL_001"), None)
    bhu_larkana_03 = next((h for h in health_reports if h["bhu_id"] == "BHU_Larkana_03"), None)
    deployed_teams = [t for t in teams if t["status"] == "DEPLOYED"]
    available_teams = [t for t in teams if t["status"] == "AVAILABLE"]
    open_missing = [m for m in missing_persons if m["status"] == "OPEN"]
    unidentified_camps = [c for c in camp_registrations if c["status"] == "UNIDENTIFIED"]
    ali_pur_bens = [b for b in beneficiary_registry if b["village_id"] == "VIL_001"]

    return {
        "scenario": "Ali Pur Flood Crisis — Full Demo",
        "data_type": "SYNTHETIC",
        "village": ali_pur,
        "weather": larkana_weather,
        "road_status": ali_pur_road,
        "health_report": bhu_larkana_03,
        "deployed_teams": {"count": len(deployed_teams), "data": deployed_teams},
        "available_teams": {"count": len(available_teams), "data": available_teams},
        "open_missing_persons": {"count": len(open_missing), "data": open_missing},
        "unidentified_camp_registrations": {"count": len(unidentified_camps), "data": unidentified_camps},
        "ali_pur_beneficiaries": {"count": len(ali_pur_bens), "data": ali_pur_bens},
        "market_prices": {"count": len(market_prices), "data": market_prices},
    }


# ══════════════════════════════════════════════
# SECTION 2: Firestore-backed endpoints
# ══════════════════════════════════════════════

@app.post("/api/crisis/create")
async def create_crisis_event(req: CrisisCreateRequest):
    """Create a new crisis_event document in Firestore."""
    crisis_id = f"CRISIS_{uuid.uuid4().hex[:8].upper()}"
    now = datetime.now(timezone.utc).isoformat()

    doc_data = {
        "id": crisis_id,
        "status": "WATCHLIST",
        "location_village_id": req.location_village_id,
        "signals": req.signals,
        "confidence_level": req.confidence_level,
        "severity_score": req.severity_score,
        "created_at": now,
        "updated_at": now,
        "source": req.source,
        "raw_complaint_text": req.raw_complaint_text,
        "agent_trace_ref": None,
    }

    db = _get_db()
    if db:
        db.collection("crisis_events").document(crisis_id).set(doc_data)

    return {"status": "created", "crisis_event": doc_data}


@app.patch("/api/dispatch/{ticket_id}/status")
async def update_dispatch_status(ticket_id: str, req: DispatchStatusUpdate):
    """Update dispatch ticket status in Firestore."""
    if req.status not in VALID_DISPATCH_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status '{req.status}'. Valid: {sorted(VALID_DISPATCH_STATUSES)}",
        )

    now = datetime.now(timezone.utc).isoformat()
    update_data: dict = {
        "status": req.status,
        "updated_at": now,
    }

    # Set arrival-specific fields
    if req.status == "ARRIVED" and req.gps_checkin:
        update_data["arrived_at"] = now
        update_data["gps_checkin"] = req.gps_checkin
    if req.status == "ACCEPTED":
        update_data["accepted_at"] = now
    if req.field_note:
        update_data["field_note"] = req.field_note

    db = _get_db()
    if db:
        doc_ref = db.collection("dispatch_tickets").document(ticket_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail=f"Dispatch ticket {ticket_id} not found")

        # Append escalation history if escalating
        if req.status == "ESCALATED" and req.escalation_reason:
            from google.cloud.firestore_v1 import ArrayUnion
            update_data["escalation_history"] = ArrayUnion([{
                "timestamp": now,
                "from_status": doc.to_dict().get("status", "UNKNOWN"),
                "to_status": "ESCALATED",
                "reason": req.escalation_reason,
            }])

        doc_ref.update(update_data)

    return {
        "status": "updated",
        "ticket_id": ticket_id,
        "new_status": req.status,
        "updated_at": now,
    }


@app.post("/api/missing/report")
async def report_missing_person(req: MissingPersonReport):
    """Create new missing person document in Firestore."""
    case_id = f"MP_LIVE_{uuid.uuid4().hex[:8].upper()}"
    now = datetime.now(timezone.utc).isoformat()

    doc_data = {
        "id": case_id,
        "name": req.name,
        "age": req.age,
        "gender": req.gender,
        "last_seen_village_id": req.last_seen_village_id,
        "last_seen_time": req.last_seen_time or now,
        "description": req.description,
        "family_phone": req.family_phone,
        "status": "OPEN",
        "match_score": None,
        "matched_camp_id": None,
        "alert_sent_at": None,
    }

    db = _get_db()
    if db:
        db.collection("missing_persons_live").document(case_id).set(doc_data)

    return {"status": "created", "missing_person": doc_data}


@app.post("/api/audit/log")
async def log_audit_entry(req: AuditLogEntry):
    """Write to aid_distribution_log in Firestore."""
    log_id = f"AID_{uuid.uuid4().hex[:8].upper()}"
    now = datetime.now(timezone.utc).isoformat()

    audit_status = "ANOMALY" if req.anomaly_flags else "PENDING"

    doc_data = {
        "id": log_id,
        "beneficiary_id": req.beneficiary_id,
        "village_id": req.village_id,
        "officer_id": req.officer_id,
        "items_distributed": req.items_distributed,
        "gps_distribution": req.gps_distribution,
        "timestamp": now,
        "audit_status": audit_status,
        "anomaly_flags": req.anomaly_flags,
        "audit_brief": req.audit_brief or "Awaiting audit engine processing.",
    }

    db = _get_db()
    if db:
        db.collection("aid_distribution_log").document(log_id).set(doc_data)

    return {"status": "created", "audit_log": doc_data}


@app.post("/api/traces/append")
async def append_agent_trace(req: AgentTraceEntry):
    """Append agent trace to agent_traces collection in Firestore."""
    trace_id = f"TRACE_{uuid.uuid4().hex[:8].upper()}"
    now = datetime.now(timezone.utc).isoformat()

    doc_data = {
        "id": trace_id,
        "crisis_event_id": req.crisis_event_id,
        "agent_id": req.agent_id,
        "timestamp": now,
        "input_summary": req.input_summary,
        "observations": req.observations,
        "reasoning": req.reasoning,
        "decision": req.decision,
        "action_taken": req.action_taken,
        "tool_calls": req.tool_calls,
        "output_summary": req.output_summary,
        "error_recovery": req.error_recovery,
    }

    db = _get_db()
    if db:
        db.collection("agent_traces").document(trace_id).set(doc_data)

    return {"status": "created", "trace": doc_data}


@app.post("/api/notify")
async def send_notification(req: NotifyRequest):
    """
    Create a simulated notification (FCM/SMS).
    Logs to Firestore notifications_log. No real messages are sent.
    """
    if req.type not in VALID_NOTIFICATION_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid type '{req.type}'. Valid: {sorted(VALID_NOTIFICATION_TYPES)}",
        )

    notif_id = f"NOTIF_{uuid.uuid4().hex[:12].upper()}"
    now = datetime.now(timezone.utc).isoformat()

    doc_data = {
        "id": notif_id,
        "type": req.type,
        "recipient_phone": req.recipient_phone,
        "message": req.message,
        "metadata": req.metadata or {},
        "status": "SIMULATED",
        "created_at": now,
    }

    db = _get_db()
    if db:
        db.collection("notifications_log").document(notif_id).set(doc_data)

    print(
        f"[NOTIF] {req.type} → {req.recipient_phone} | "
        f"{notif_id} | SIMULATED"
    )

    return {
        "status": "created",
        "notification": {
            "id": notif_id,
            "type": req.type,
            "recipient_phone": req.recipient_phone,
            "status": "SIMULATED",
            "message_preview": req.message[:80] + ("..." if len(req.message) > 80 else ""),
            "created_at": now,
            "note": "No real SMS/FCM sent — logged to Firestore notifications_log",
        },
    }


# ──────────────────────────────────────────────
# Edge Case Demo Endpoints
# ──────────────────────────────────────────────

from edge_cases import trigger_edge_case, agent_traces, EDGE_CASE_SUMMARIES


@app.get("/api/demo/edge_cases")
def list_edge_cases():
    """List all 6 available edge case demos."""
    return {"data": EDGE_CASE_SUMMARIES}


@app.post("/api/demo/edge_case/{case_number}")
def run_edge_case(case_number: int):
    """Trigger a specific edge case demo scenario (1-6)."""
    if case_number < 1 or case_number > 6:
        raise HTTPException(status_code=400, detail="case_number must be 1-6")
    result = trigger_edge_case(case_number)
    return {"status": "triggered", "data": result}


@app.get("/api/demo/traces")
def get_traces():
    """Return all agent trace entries generated by edge case demos."""
    return {"data": agent_traces}


@app.get("/api/stats/baseline")
def get_baseline_stats():
    """Live stats for the Before vs After dashboard (Screen 10)."""
    return {
        "data": {
            "active_crisis_events": 4,
            "tickets_dispatched": 12,
            "missing_cases_open": 3,
            "missing_cases_resolved": 1,
            "audit_flags_raised": 2,
            "fraud_risks_detected": 1,
            "total_notifications_sent": 18,
            "agents_active": 11,
            "edge_cases_triggered": len(agent_traces),
        }
    }


@app.get("/api/export/traces")
def export_traces_api():
    """Export all traces as a downloadable JSON document."""
    from datetime import datetime, timezone as tz
    return {
        "export_timestamp": datetime.now(tz.utc).isoformat(),
        "total_traces": len(agent_traces),
        "traces": agent_traces,
        "note": "ALL DATA IS SYNTHETIC DEMO DATA",
    }


# ──────────────────────────────────────────────
# Smart Complaint Analyzer (keyword NLP, no Gemini)
# ──────────────────────────────────────────────

class ComplaintRequest(BaseModel):
    complaint_text: str
    village_id: str = "VIL_001"


@app.post("/api/analyze-complaint")
def analyze_complaint(req: ComplaintRequest):
    """Analyze any complaint text dynamically via keyword NLP. No Gemini quota used."""
    text = req.complaint_text.lower()
    village_id = req.village_id

    # ── A1: Signal Extraction ──────────────────
    signals = []
    flood_kw = ["pani", "flood", "water", "seel", "baarish", "khara", "baarh", "sailaab", "barsat", "inundation", "darya", "nehri"]
    if any(k in text for k in flood_kw):
        signals.append("FLOOD")

    health_kw = ["diarrhea", "beemar", "hospital", "disease", "bukhar", "fever", "sick", "cholera", "malaria", "vomit", "ulti", "dast", "health", "sehat", "doctor", "dawa"]
    if any(k in text for k in health_kw):
        signals.append("HEALTH")

    fire_kw = ["aag", "fire", "jalraha", "jal raha", "burn", "blaze", "surkh"]
    if any(k in text for k in fire_kw):
        signals.append("FIRE")

    food_kw = ["khaana", "food", "qahat", "hunger", "bhook", "faqa", "ration", "khana nahi", "khana", "grain"]
    if any(k in text for k in food_kw):
        signals.append("FOOD_SHORTAGE")

    infra_kw = ["road", "bridge", "sarak", "pul", "bijli", "electricity", "current nahi", "makaan", "ghar gir"]
    if any(k in text for k in infra_kw):
        signals.append("INFRASTRUCTURE")

    missing_person = False
    missing_kw = ["missing", "nazar nahi", "gum", "lost", "laapta", "nahi mila", "bucha", "bachay gum", "child missing"]
    if any(k in text for k in missing_kw):
        missing_person = True
        signals.append("MISSING_PERSON")

    if not signals:
        signals.append("GENERAL_EMERGENCY")

    # Duration hints
    duration_hours = 24
    dur_map = {"2 din": 48, "do din": 48, "3 din": 72, "teen din": 72, "ek din": 24, "1 din": 24,
               "week": 168, "hafte": 168, "months": 720, "mahine": 720, "ghante": 2}
    for hint, h in dur_map.items():
        if hint in text:
            duration_hours = h
            break

    # Location detection
    loc_map = {"ali pur": "Ali Pur", "alipur": "Ali Pur", "larkana": "Larkana", "dadu": "Dadu",
               "sukkur": "Sukkur", "jacobabad": "Jacobabad", "dera ghazi": "Dera Ghazi Khan",
               "multan": "Multan", "lahore": "Lahore", "karachi": "Karachi",
               "peshawar": "Peshawar", "quetta": "Quetta", "nawabshah": "Nawabshah",
               "hyderabad": "Hyderabad", "kashmore": "Kashmore", "basti": "Basti Malook"}
    detected_location = "Unknown Village"
    for hint, name in loc_map.items():
        if hint in text:
            detected_location = name
            break
    if detected_location == "Unknown Village":
        vil = next((v for v in villages if v.get("id") == village_id), None)
        if vil:
            detected_location = vil.get("name", "Unknown Village")

    # Affected group
    affected_group = "GENERAL"
    if any(k in text for k in ["bacha", "bachay", "children", "child", "kids", "baby", "bachi"]):
        affected_group = "CHILDREN"
    elif any(k in text for k in ["aurat", "women", "female", "khawateen", "maa", "mother"]):
        affected_group = "WOMEN"
    elif any(k in text for k in ["buzurg", "old", "elderly", "baba", "dada", "dadi"]):
        affected_group = "ELDERLY"

    # ── A2: Evidence (from mock data) ──────────
    vil = next((v for v in villages if v.get("id") == village_id), None)
    district = vil["district"] if vil else "Larkana"
    weather_rec = next((w for w in weather if w.get("district") == district), None)
    rainfall = weather_rec.get("rainfall_mm_24hr", 0) if weather_rec else 0
    road_rec = next((r for r in road_status if r.get("village_id") == village_id), None)
    road_blocked = (road_rec.get("main_road_status") == "BLOCKED") if road_rec else False
    health_rec = next((h for h in health_reports if h.get("village_id") == village_id), None)
    diarrhea = health_rec.get("diarrhea_cases_7day", 0) if health_rec else 0
    open_missing_count = len([m for m in missing_persons if m.get("status") == "OPEN"])

    evidence_checks = []
    if "FLOOD" in signals or "GENERAL_EMERGENCY" in signals:
        if rainfall > 5:
            ev = {"source": "Rainfall Data", "value": f"{rainfall}mm in 24h", "verdict": "SUPPORTS",
                  "justification": f"Heavy rainfall of {rainfall}mm confirms flooding potential."}
        elif rainfall == 0:
            ev = {"source": "Rainfall Data", "value": "0mm in 24h", "verdict": "CONTRADICTS",
                  "justification": "No rainfall recorded — may indicate irrigation canal breach or data lag."}
        else:
            ev = {"source": "Rainfall Data", "value": f"{rainfall}mm in 24h", "verdict": "NEUTRAL",
                  "justification": "Moderate rainfall — inconclusive for flood claim."}
        evidence_checks.append(ev)

    evidence_checks.append({
        "source": "Road Status", "value": "Blocked" if road_blocked else "Clear",
        "verdict": "SUPPORTS" if road_blocked else "NEUTRAL",
        "justification": "Main road blocked — confirms access difficulty." if road_blocked else "Roads clear — no access restrictions.",
    })

    if "HEALTH" in signals or diarrhea > 0:
        evidence_checks.append({
            "source": "Health Reports", "value": f"Diarrhea Cases: {diarrhea}",
            "verdict": "SUPPORTS" if diarrhea > 5 else "NEUTRAL",
            "justification": f"Health facility reported {diarrhea} diarrhea cases this week." + (" Strongly supports contaminated water." if diarrhea > 10 else ""),
        })

    evidence_checks.append({
        "source": "Crop Calendar", "value": "Active Season",
        "verdict": "NEUTRAL", "justification": "Seasonal status does not confirm or deny the crisis.",
    })

    if "MISSING_PERSON" in signals:
        evidence_checks.append({
            "source": "Missing Persons DB", "value": f"{open_missing_count} open case(s)",
            "verdict": "SUPPORTS",
            "justification": f"{open_missing_count} open missing person cases in system. Engine 2 activated for cross-matching.",
        })
    elif "FLOOD" in signals or "HEALTH" in signals:
        evidence_checks.append({
            "source": "Nearby Reports", "value": f"{open_missing_count} similar report(s)",
            "verdict": "SUPPORTS" if open_missing_count > 0 else "NEUTRAL",
            "justification": f"{open_missing_count} corroborating reports from nearby areas.",
        })

    # ── A3: Severity ───────────────────────────
    score = 1.0
    if "FLOOD" in signals:          score += 1.5
    if "HEALTH" in signals:         score += 1.0
    if "MISSING_PERSON" in signals: score += 1.5
    if "FIRE" in signals:           score += 2.0
    if "FOOD_SHORTAGE" in signals:  score += 1.0
    if "INFRASTRUCTURE" in signals: score += 0.5
    if road_blocked:                score += 0.5
    if diarrhea > 10:               score += 0.5
    has_conflict = any(e["verdict"] == "CONTRADICTS" for e in evidence_checks)
    if has_conflict:                score -= 0.5
    score = min(5.0, round(score, 1))

    confidence = "HIGH" if score >= 4 and not has_conflict else ("MEDIUM" if score >= 2.5 else "LOW")
    authorization = "DISPATCH_AUTHORIZED" if score >= 3.5 and not has_conflict else ("REQUEST_VERIFICATION" if has_conflict or score >= 2.5 else "MONITOR")

    weight_breakdown = {}
    if "FLOOD" in signals:          weight_breakdown["FLOOD signal"] = "+1.5"
    if "HEALTH" in signals:         weight_breakdown["HEALTH signal"] = "+1.0"
    if "MISSING_PERSON" in signals: weight_breakdown["Missing Person"] = "+1.5"
    if "FIRE" in signals:           weight_breakdown["FIRE signal"] = "+2.0"
    if road_blocked:                weight_breakdown["Road blocked"] = "+0.5"
    if diarrhea > 10:               weight_breakdown["High health cases"] = "+0.5"
    if has_conflict:                weight_breakdown["Evidence conflict"] = "-0.5"

    coordinator_reasoning = None
    if has_conflict:
        coordinator_reasoning = (
            f"Conflict: {detected_location} complaint mentions {'flood/water' if 'FLOOD' in signals else signals[0].lower()} "
            f"but weather shows {rainfall}mm rainfall. Possible causes: "
            "(1) Irrigation canal breach, (2) Weather station data lag, (3) Underground water seepage. "
            "Action: REQUEST_VERIFICATION via SMS to focal person. Timeout: 20 min."
        )

    # ── Response Teams ─────────────────────────
    team_map = {
        "FLOOD":             {"dept": "DISASTER",  "team": "Rescue 1122",          "icon": "flood",                  "dist": "12.4", "eta": "25"},
        "HEALTH":            {"dept": "HEALTH",    "team": "Mobile Med Unit",       "icon": "local_hospital",         "dist": "8.1",  "eta": "15"},
        "MISSING_PERSON":    {"dept": "POLICE",    "team": "Child Recovery Unit",   "icon": "person_search",          "dist": "5.2",  "eta": "10"},
        "FIRE":              {"dept": "FIRE",      "team": "Fire Brigade Alpha",    "icon": "local_fire_department",  "dist": "15.0", "eta": "30"},
        "FOOD_SHORTAGE":     {"dept": "WELFARE",   "team": "Ration Distribution",   "icon": "volunteer_activism",     "dist": "20.0", "eta": "45"},
        "INFRASTRUCTURE":    {"dept": "PDMA",      "team": "Infrastructure Team",   "icon": "construction",           "dist": "18.0", "eta": "40"},
        "GENERAL_EMERGENCY": {"dept": "DISASTER",  "team": "General Response Team", "icon": "emergency",              "dist": "10.0", "eta": "20"},
    }
    response_teams = []
    seen = set()
    for sig in signals:
        if sig in team_map and team_map[sig]["dept"] not in seen:
            t = dict(team_map[sig])
            t["id"] = f"TKT-{900 + len(response_teams)}"
            t["signal"] = sig
            response_teams.append(t)
            seen.add(t["dept"])

    return {
        "status": "ok",
        "a1_signals": {
            "location_name": detected_location,
            "village_id": village_id,
            "crisis_type": signals,
            "missing_person_signal": missing_person,
            "affected_group": affected_group,
            "duration_hours": duration_hours,
            "raw_complaint": req.complaint_text,
        },
        "a2_evidence": {
            "confidence": confidence,
            "has_conflict": has_conflict,
            "evidence_checks": evidence_checks,
        },
        "a3_severity": {
            "severity_score": score,
            "authorization": authorization,
            "weight_breakdown": weight_breakdown,
            "coordinator_reasoning": coordinator_reasoning,
        },
        "response_teams": response_teams,
    }
