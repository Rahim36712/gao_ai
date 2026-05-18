"""
Gaon Guard AI — Edge Case Demo Scenarios
6 named demo scenarios that exercise the agentic pipeline's error handling,
conflict resolution, and escalation logic.

All data is SYNTHETIC DEMO DATA.
"""

import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "mock_data"

# In-memory trace store (shared with the API)
agent_traces: list[dict] = []


def _trace(agent: str, group: str, summary: str, reasoning: str,
           decision: str, tools: int = 0, is_arb: bool = False):
    """Log an agent trace entry."""
    entry = {
        "id": f"TRACE_{uuid.uuid4().hex[:8].upper()}",
        "agent": agent,
        "group": group,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "reasoning": reasoning,
        "decision": decision,
        "tool_calls": tools,
        "is_arbitration": is_arb,
    }
    agent_traces.append(entry)
    return entry


# ══════════════════════════════════════════════
# EDGE CASE 1: Flood report vs 0mm rainfall
# ══════════════════════════════════════════════

def edge_case_1():
    """Conflict: report says FLOOD, weather says no rain."""
    result = {"case": 1, "title": "Flood vs No Rain Conflict", "traces": []}

    # A1 intake
    t1 = _trace("A1_INTAKE", "A", "Extracted FLOOD, HEALTH signals for Ali Pur",
                "Parsed Roman Urdu: 'pani khara hai' -> FLOOD, 'diarrhea' -> HEALTH",
                "SIGNALS_EXTRACTED")
    result["traces"].append(t1)

    # A2 evidence — weather contradicts
    t2 = _trace("A2_EVIDENCE", "A",
                "Checked 5 sources. Weather shows 0mm rainfall — CONTRADICTS flood claim.",
                "Rainfall: 0mm (CONTRADICTS). Road: Blocked (SUPPORTS). Health: Diarrhea spike (SUPPORTS). "
                "Crop: Harvest season (NEUTRAL). Nearby: 1 similar report (SUPPORTS). "
                "Result: 4/5 support but weather is a critical contradiction.",
                "CONFIDENCE_MEDIUM", tools=5)
    result["traces"].append(t2)

    # X Coordinator fires
    t3 = _trace("X_COORDINATOR", "X",
                "ARBITRATION: A1 says FLOOD but weather shows 0mm rainfall",
                "Hypothesis 1: Weather station data lag — PMD station last updated 6hrs ago, "
                "possible delay in flood-affected area. "
                "Hypothesis 2: Irrigation canal breach — not rain-based flooding, canal overflow "
                "from upstream release at Sukkur Barrage. "
                "Hypothesis 3: Exaggerated report — complainant may be describing waterlogging "
                "from poor drainage, not active flooding. "
                "Decision: REQUEST_VERIFICATION. SMS sent to Focal Person at Ali Pur: "
                "'Unverified flood report — can you confirm? Reply 1=Yes 2=No'. "
                "Timeout: 20 minutes. If no reply, escalate to District Officer.",
                "REQUEST_VERIFICATION", is_arb=True)
    result["traces"].append(t3)

    # A4 dispatch held
    t4 = _trace("A4_DISPATCH", "A", "Dispatch HELD pending coordinator verification",
                "Authorization status: HOLD. Coordinator X has flagged weather contradiction. "
                "Teams remain on standby. Will auto-dispatch if verification confirms within 20min.",
                "DISPATCH_HELD")
    result["traces"].append(t4)

    result["crisis_event"] = {
        "id": f"CE_{uuid.uuid4().hex[:6].upper()}",
        "status": "WATCHLIST",
        "coordinator_hold": True,
        "village": "Ali Pur",
        "signals": ["FLOOD", "HEALTH"],
        "severity": 4.0,
        "authorization": "HOLD",
    }
    result["notification"] = {
        "type": "SMS",
        "to": "Focal Person Ali Pur",
        "message": "Unverified flood report at Ali Pur — can you confirm? Reply 1=Yes 2=No",
    }
    return result


# ══════════════════════════════════════════════
# EDGE CASE 2: Missing location in report
# ══════════════════════════════════════════════

def edge_case_2():
    """Missing location — cannot process without village."""
    result = {"case": 2, "title": "Missing Location", "traces": []}

    t1 = _trace("A1_INTAKE", "A",
                "Extracted FLOOD signal but location_name is NULL",
                "Input: 'Hamare gaon mein pani khara hai'. Parsed successfully but no village name, "
                "district, or GPS coordinates found. location_name: null, district_guess: null.",
                "SIGNALS_EXTRACTED_INCOMPLETE")
    result["traces"].append(t1)

    t2 = _trace("A3_SEVERITY", "A",
                "Cannot score — LOCATION_REQUIRED",
                "Severity scoring requires village coordinates for distance calculations, "
                "risk zone lookup, and team assignment. Without location, scoring is impossible. "
                "Authorization: HOLD. Reason: LOCATION_REQUIRED.",
                "HOLD_LOCATION_REQUIRED")
    result["traces"].append(t2)

    result["crisis_event"] = {
        "id": f"CE_{uuid.uuid4().hex[:6].upper()}",
        "status": "INCOMPLETE",
        "village": None,
        "signals": ["FLOOD"],
        "severity": None,
        "authorization": "HOLD",
        "hold_reason": "LOCATION_REQUIRED",
    }
    result["prompt"] = "Please select your village or share GPS to continue."
    return result


# ══════════════════════════════════════════════
# EDGE CASE 3: Duplicate CNIC
# ══════════════════════════════════════════════

def edge_case_3():
    """Duplicate CNIC detected in aid distribution."""
    result = {"case": 3, "title": "Duplicate CNIC Detection", "traces": []}

    t1 = _trace("C1_REGISTRY", "C",
                "DUPLICATE CNIC 42101-1234567-1 detected — entry BLOCKED",
                "CNIC 42101-1234567-1 already registered to Abdul Rehman in VIL_002 (Basti Malook). "
                "Second registration attempt by 'Muhammad Aslam' for same CNIC. "
                "duplicate_detected: true, valid: false. Distribution blocked.",
                "BLOCKED_DUPLICATE")
    result["traces"].append(t1)

    t2 = _trace("C2_AUDIT", "C",
                "Officer TEAM_004 flagged — 3rd duplicate attempt",
                "Officer TEAM_004 has submitted 3 duplicate CNICs in the last 24 hours. "
                "Pattern suggests intentional double-registration for aid diversion. "
                "officer_flag: true. Supervisor notification triggered.",
                "OFFICER_FLAGGED", tools=1)
    result["traces"].append(t2)

    result["audit_log"] = {
        "id": f"AUDIT_{uuid.uuid4().hex[:6].upper()}",
        "status": "BLOCKED",
        "reason": "DUPLICATE_CNIC",
        "cnic": "42101-1234567-1",
        "officer_id": "TEAM_004",
        "officer_flag": True,
    }
    result["notification"] = {
        "type": "SMS",
        "to": "District Supervisor",
        "message": "ALERT: Officer TEAM_004 flagged for 3 duplicate CNIC submissions. Investigate immediately.",
    }
    return result


# ══════════════════════════════════════════════
# EDGE CASE 4: Team non-movement escalation
# ══════════════════════════════════════════════

def edge_case_4():
    """Team assigned but does not move — escalation chain."""
    result = {"case": 4, "title": "Team Non-Movement Escalation", "traces": [], "timeline": []}

    ticket_id = f"TKT_{uuid.uuid4().hex[:4].upper()}"

    # T+0: Assigned
    t1 = _trace("A4_DISPATCH", "A",
                f"Ticket {ticket_id} created — Rescue 1122 Alpha assigned to Ali Pur",
                "Nearest DISASTER team: Rescue 1122 Alpha (12.4km, ETA 25min). "
                "Ticket status: ASSIGNED. GPS monitoring started.",
                "TICKET_CREATED", tools=1)
    result["traces"].append(t1)
    result["timeline"].append({"time": "T+0", "status": "ASSIGNED", "detail": "Ticket created"})

    # T+5: Accepted
    t2 = _trace("A4_DISPATCH", "A",
                f"Ticket {ticket_id} — Team ACCEPTED",
                "Rescue 1122 Alpha acknowledged dispatch. Status: ACCEPTED. "
                "Expected departure: immediate. GPS baseline: 27.5560, 68.3690 (depot).",
                "STATUS_ACCEPTED")
    result["traces"].append(t2)
    result["timeline"].append({"time": "T+5min", "status": "ACCEPTED", "detail": "Team acknowledged"})

    # T+30: No movement — reminder
    t3 = _trace("A4_DISPATCH", "A",
                f"NON-MOVEMENT DETECTED — Ticket {ticket_id}",
                "GPS check at T+30min: team still at 27.5560, 68.3690 (depot coordinates). "
                "No movement detected in 25 minutes since acceptance. "
                "Action: Reminder SMS sent to team lead. Escalation timer started (30min).",
                "REMINDER_SENT", tools=1)
    result["traces"].append(t3)
    result["timeline"].append({"time": "T+30min", "status": "REMINDER", "detail": "Non-movement detected, SMS sent"})

    # T+60: Escalation
    t4 = _trace("A4_DISPATCH", "A",
                f"ESCALATION — Ticket {ticket_id} escalated to District Officer",
                "T+60min: Team still at depot. Reminder ignored. "
                "Escalating to Coordinator X and District Officer. Original team flagged for review.",
                "ESCALATED", tools=2)
    result["traces"].append(t4)

    t5 = _trace("X_COORDINATOR", "X",
                "ARBITRATION: Team non-response — reassigning",
                "Rescue 1122 Alpha has failed to respond for 60 minutes. "
                "Identifying next nearest team. Mobile Med Unit 3 is 18.2km from Ali Pur (ETA 35min). "
                "Decision: Reassign to Mobile Med Unit 3. Flag original team for disciplinary review.",
                "REASSIGN_TEAM", is_arb=True)
    result["traces"].append(t5)
    result["timeline"].append({"time": "T+60min", "status": "ESCALATED", "detail": "District Officer notified"})

    # T+70: Reassigned
    new_ticket = f"TKT_{uuid.uuid4().hex[:4].upper()}"
    t6 = _trace("A4_DISPATCH", "A",
                f"New ticket {new_ticket} — Mobile Med Unit 3 assigned",
                f"Original ticket {ticket_id} status: ESCALATED. "
                f"New ticket {new_ticket} created for Mobile Med Unit 3. ETA: 35min.",
                "REASSIGNED", tools=1)
    result["traces"].append(t6)
    result["timeline"].append({"time": "T+70min", "status": "REASSIGNED", "detail": f"New ticket {new_ticket}"})

    result["original_ticket"] = ticket_id
    result["new_ticket"] = new_ticket
    return result


# ══════════════════════════════════════════════
# EDGE CASE 5: Low confidence / ambiguous
# ══════════════════════════════════════════════

def edge_case_5():
    """Ambiguous report with insufficient evidence."""
    result = {"case": 5, "title": "Low Confidence — Ambiguous Report", "traces": []}

    t1 = _trace("A1_INTAKE", "A",
                "Minimal extraction from 'Flood hai' — no location, no detail",
                "Input: 'Flood hai'. Extracted: crisis_type: [FLOOD], location_name: null, "
                "district_guess: null, duration_hours: null, affected_group: null. "
                "Very low signal density.",
                "SIGNALS_MINIMAL")
    result["traces"].append(t1)

    t2 = _trace("A2_EVIDENCE", "A",
                "All 5 sources returned NEUTRAL — no corroboration",
                "Without a location, evidence checks returned generic results. "
                "Rainfall: NEUTRAL (no location to check). Road: NEUTRAL. Health: NEUTRAL. "
                "Crop: NEUTRAL. Nearby: No matching reports found. "
                "Confidence: LOW (0 SUPPORTS, 0 CONTRADICTS, 5 NEUTRAL).",
                "CONFIDENCE_LOW", tools=5)
    result["traces"].append(t2)

    t3 = _trace("A3_SEVERITY", "A",
                "INSUFFICIENT_EVIDENCE — cannot authorize dispatch",
                "Severity cannot be calculated: no location for risk zone lookup, "
                "no corroborating evidence, single vague report. "
                "Authorization: HOLD. Status: WATCHLIST. "
                "Watchlist rule: if 2+ similar reports from nearby villages in 2 hours, auto-upgrade.",
                "HOLD_INSUFFICIENT")
    result["traces"].append(t3)

    result["crisis_event"] = {
        "id": f"CE_{uuid.uuid4().hex[:6].upper()}",
        "status": "WATCHLIST",
        "village": None,
        "signals": ["FLOOD"],
        "severity": None,
        "authorization": "HOLD",
        "hold_reason": "INSUFFICIENT_EVIDENCE",
        "confidence": "LOW",
    }
    return result


# ══════════════════════════════════════════════
# EDGE CASE 6: Match below threshold
# ══════════════════════════════════════════════

def edge_case_6():
    """Missing person match at 52% — below 70% auto-alert threshold."""
    result = {"case": 6, "title": "Match Below Threshold — Human Review", "traces": []}

    t1 = _trace("B1_SCANNER", "B",
                "Missing person signal detected in complaint",
                "Keyword match: 'bacha nazar nahi aa raha' -> missing_person_signal: true. "
                "Extracted: male, approx age 12, last seen Ali Pur.",
                "SIGNAL_DETECTED")
    result["traces"].append(t1)

    t2 = _trace("B2_MATCHER", "B",
                "Partial match found — 52% confidence (below 70% threshold)",
                "Compared against 20 camp registrations. Best match: CAMP_REG_015. "
                "Age score: 15/30 (reported 12, camp record 17 — 5 year gap). "
                "Proximity score: 25/40 (camp is 22km from last seen location). "
                "Description score: 12/30 (partial match on 'dark hair' only). "
                "Total: 52/100. Action: REVIEW (below 70 threshold for auto-alert). "
                "No family notification sent.",
                "REVIEW_REQUIRED", tools=2)
    result["traces"].append(t2)

    t3 = _trace("B2_MATCHER", "B",
                "Operator notification sent — manual review required",
                "Score 52% is in REVIEW range (50-69). Auto-alert suppressed to prevent "
                "false hope for families. Operator must visually confirm before any contact. "
                "Notification: 'Possible match for Hassan Ali — 52% — Manual review required'.",
                "OPERATOR_NOTIFIED", tools=1)
    result["traces"].append(t3)

    result["match"] = {
        "missing_id": "MP_001",
        "missing_name": "Hassan Ali",
        "camp_reg_id": "CAMP_REG_015",
        "score": 52,
        "action": "REVIEW",
        "status": "PENDING_MATCH",
        "family_alerted": False,
        "breakdown": {"age": 15, "proximity": 25, "description": 12},
    }
    result["notification"] = {
        "type": "OPERATOR_PUSH",
        "message": "Possible match for Hassan Ali — 52% confidence — Manual review required",
    }
    return result


# ══════════════════════════════════════════════
# DISPATCHER
# ══════════════════════════════════════════════

EDGE_CASE_HANDLERS = {
    1: edge_case_1,
    2: edge_case_2,
    3: edge_case_3,
    4: edge_case_4,
    5: edge_case_5,
    6: edge_case_6,
}

EDGE_CASE_SUMMARIES = [
    {"case": 1, "title": "Flood vs No Rain Conflict", "screen": 4, "desc": "A2 contradicts A1. Coordinator X arbitrates."},
    {"case": 2, "title": "Missing Location", "screen": 2, "desc": "No village in complaint. Pipeline halts."},
    {"case": 3, "title": "Duplicate CNIC", "screen": 8, "desc": "Same CNIC registered twice. Officer flagged."},
    {"case": 4, "title": "Team Non-Movement", "screen": 6, "desc": "Team doesn't move for 30min. Escalation chain."},
    {"case": 5, "title": "Low Confidence Report", "screen": 4, "desc": "Vague report. All evidence NEUTRAL."},
    {"case": 6, "title": "Match Below Threshold", "screen": 7, "desc": "52% match. Human review required."},
]


def trigger_edge_case(case_number: int) -> dict:
    """Run an edge case and return the full result with traces."""
    handler = EDGE_CASE_HANDLERS.get(case_number)
    if not handler:
        return {"error": f"Edge case {case_number} not found. Valid: 1-6."}
    return handler()
