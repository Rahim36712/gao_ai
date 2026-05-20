"""
Gaon Guard AI - Combined Audit Pipeline (C1 -> C2 -> C3)
Runs all three Aid Accountability agents on a distribution entry.

Usage:
    from audit_pipeline import run_full_audit
    result = run_full_audit(client, distribution_entry)

All data is SYNTHETIC DEMO DATA.
"""

import json
import math
import os
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
CONFIGS_DIR = Path(__file__).resolve().parent.parent / "antigravity" / "agent_configs"


def _load_config(filename):
    with open(CONFIGS_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "antigravity"))
from gemini_utils import call_gemini as _call_gemini
from gemini_utils import GeminiCallError


def _api_get(path):
    r = requests.get(f"{API_BASE}{path}", timeout=10)
    r.raise_for_status()
    return r.json()


def _api_post(path, data):
    r = requests.post(f"{API_BASE}{path}", json=data, timeout=10)
    r.raise_for_status()
    return r.json()


def _post_trace(agent_id, input_summary, observations, reasoning,
                decision, action_taken, tool_calls, output_summary):
    return _api_post("/api/traces/append", {
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


def _normalize_result(result, fallback_factory, fallback_reason):
    """Gemini sometimes returns lists or fallback markers; always return a dict."""
    if isinstance(result, list) and len(result) > 0:
        result = result[0]
    if isinstance(result, dict) and not result.get("fallback_required"):
        return result
    reason = fallback_reason
    if isinstance(result, dict):
        reason = result.get("error") or fallback_reason
    return fallback_factory(reason)


def _safe_call_gemini(client, config, user_prompt, fallback_factory):
    try:
        result = _call_gemini(client, config["system_prompt"], user_prompt, config)
    except (GeminiCallError, Exception) as exc:
        return fallback_factory(f"Gemini unavailable: {str(exc)[:180]}")
    return _normalize_result(result, fallback_factory, "Gemini returned malformed output")


def _cnic_present(cnic):
    return isinstance(cnic, str) and len(cnic.strip()) > 0


def _cnic_format_ok(cnic):
    if not _cnic_present(cnic):
        return False
    parts = cnic.split("-")
    return (
        len(parts) == 3
        and len(parts[0]) == 5
        and len(parts[1]) == 7
        and len(parts[2]) == 1
        and all(part.isdigit() for part in parts)
    )


def _local_c1_fallback(beneficiary_entry, existing_registry, reason):
    cnic = beneficiary_entry.get("cnic")
    duplicate = bool(cnic) and any(row.get("cnic") == cnic for row in existing_registry or [])
    rejection_reasons = []
    if not _cnic_present(cnic):
        rejection_reasons.append("CNIC missing")
    elif not _cnic_format_ok(cnic):
        rejection_reasons.append("CNIC format invalid")
    if duplicate:
        rejection_reasons.append("Duplicate CNIC in registry")

    household_size = beneficiary_entry.get("household_size") or 0
    try:
        household_size = int(household_size)
    except (TypeError, ValueError):
        household_size = 0
        rejection_reasons.append("Household size invalid")
    if household_size < 1 or household_size > 20:
        rejection_reasons.append("Household size outside allowed range")

    damage_cash = {"SEVERE": 15000, "MAJOR": 10000, "MODERATE": 10000, "MINOR": 5000, "MILD": 5000}
    valid = len(rejection_reasons) == 0
    decision = "VALID" if valid else "REJECTED"
    return {
        "valid": valid,
        "duplicate_detected": duplicate,
        "reason": "; ".join(rejection_reasons) or "CNIC present and no duplicate found",
        "decision": decision,
        "rejection_reasons": rejection_reasons,
        "calculated_entitlement": {
            "tents": 1 if valid else 0,
            "ration_packs": math.ceil(household_size / 4) if household_size > 0 else 0,
            "cash_pkr": damage_cash.get(str(beneficiary_entry.get("damage_level", "")).upper(), 0),
        },
        "officer_flag": False,
        "fallback_used": True,
        "fallback_reason": reason,
    }


def _normalize_c1_output(result, beneficiary_entry, existing_registry):
    fallback = _local_c1_fallback(
        beneficiary_entry,
        existing_registry,
        "Gemini returned incomplete C1 output",
    )
    if not isinstance(result, dict):
        return fallback

    normalized = dict(result)
    duplicate = bool(normalized.get("duplicate_detected", fallback["duplicate_detected"]))
    cnic = beneficiary_entry.get("cnic")
    if cnic and any(row.get("cnic") == cnic for row in existing_registry or []):
        duplicate = True

    rejection_reasons = normalized.get("rejection_reasons")
    if not isinstance(rejection_reasons, list):
        rejection_reasons = list(fallback["rejection_reasons"])
    if duplicate and "Duplicate CNIC in registry" not in rejection_reasons:
        rejection_reasons.append("Duplicate CNIC in registry")
    if not _cnic_present(cnic) and "CNIC missing" not in rejection_reasons:
        rejection_reasons.append("CNIC missing")
    elif cnic and not _cnic_format_ok(cnic) and "CNIC format invalid" not in rejection_reasons:
        rejection_reasons.append("CNIC format invalid")

    if "valid" in normalized and isinstance(normalized.get("valid"), bool):
        valid = normalized["valid"] and not duplicate and len(rejection_reasons) == 0
    else:
        valid = fallback["valid"] and not duplicate and len(rejection_reasons) == 0

    entitlement = normalized.get("calculated_entitlement")
    if not isinstance(entitlement, dict):
        entitlement = fallback["calculated_entitlement"]

    reason = normalized.get("reason") or "; ".join(rejection_reasons) or "C1 validation approved"
    decision = normalized.get("decision") or ("APPROVED" if valid else "REJECTED")
    if duplicate or not valid:
        decision = "REJECTED"

    normalized.update({
        "valid": valid,
        "duplicate_detected": duplicate,
        "rejection_reasons": rejection_reasons,
        "reason": reason,
        "decision": decision,
        "calculated_entitlement": entitlement,
        "officer_flag": bool(normalized.get("officer_flag", False)),
        "fallback_used": bool(normalized.get("fallback_used", False)),
    })
    return normalized


def _local_c2_fallback(distribution_entry, registered_households, reason):
    try:
        households = int(registered_households or distribution_entry.get("registered_households") or 0)
    except (TypeError, ValueError):
        households = 0
    total_tents = float(distribution_entry.get("total_tents", 0) or 0)
    total_ration = float(distribution_entry.get("total_ration_packs", 0) or 0)
    tents_per_household = total_tents / households if households > 0 else 0
    ration_per_household = total_ration / households if households > 0 else 0
    abnormal_quantity = tents_per_household > 1.5 or ration_per_household > 4

    flags = []
    if abnormal_quantity:
        flags.append("QUANTITY_ANOMALY")
    severity = "HIGH" if tents_per_household > 3 else ("MEDIUM" if abnormal_quantity else "LOW")
    audit_status = "FRAUD_RISK" if severity == "HIGH" else ("ANOMALY" if abnormal_quantity else "PASS")
    explanation = (
        f"Quantity check: {total_tents:g} tents for {households} households "
        f"({tents_per_household:.2f} tents/household)."
    )
    return {
        "anomaly_detected": abnormal_quantity,
        "severity": severity,
        "reason": explanation,
        "decision": audit_status,
        "anomaly_flags": flags,
        "escalation_required": abnormal_quantity,
        "escalation_brief": explanation if abnormal_quantity else "No abnormal quantity detected.",
        "audit_status": audit_status,
        "fallback_used": True,
        "fallback_reason": reason,
    }


def _local_c3_fallback(distribution_gps, village_data, reason):
    distance = round(haversine(
        distribution_gps.get("lat", 0),
        distribution_gps.get("lng", 0),
        village_data.get("lat", 0),
        village_data.get("lng", 0),
    ), 2)
    if distance > 30:
        verdict = "SEVERE_LOCATION_MISMATCH"
    elif distance > 5:
        verdict = "LOCATION_MISMATCH"
    else:
        verdict = "PASS"
    mismatch = verdict != "PASS"
    explanation = (
        f"Distribution GPS is {distance}km from {village_data.get('name', 'village')} centroid."
    )
    return {
        "location_mismatch": mismatch,
        "distance_km": distance,
        "reason": explanation,
        "decision": verdict,
        "gps_distribution": distribution_gps,
        "village_centroid": {"lat": village_data.get("lat"), "lng": village_data.get("lng")},
        "verdict": verdict,
        "escalation_required": verdict == "SEVERE_LOCATION_MISMATCH",
        "mismatch_explanation": explanation if mismatch else "GPS within acceptable range.",
        "fallback_used": True,
        "fallback_reason": reason,
    }


def _normalize_c3_output(result, distribution_gps, village_data):
    required = ["distance_km", "verdict", "escalation_required"]
    if not isinstance(result, dict) or any(result.get(key) is None for key in required):
        return _local_c3_fallback(distribution_gps, village_data, "Gemini returned incomplete C3 output")

    verdict = result.get("verdict")
    if verdict not in {"PASS", "LOCATION_MISMATCH", "SEVERE_LOCATION_MISMATCH"}:
        return _local_c3_fallback(distribution_gps, village_data, "Gemini returned invalid C3 verdict")

    distance = result.get("distance_km")
    try:
        distance = round(float(distance), 2)
    except (TypeError, ValueError):
        return _local_c3_fallback(distribution_gps, village_data, "Gemini returned invalid C3 distance")

    if verdict == "LOCATION_MISMATCH" and distance > 30:
        verdict = "SEVERE_LOCATION_MISMATCH"

    mismatch = verdict != "PASS"
    reason = result.get("reason") or result.get("mismatch_explanation") or (
        f"Distribution GPS is {distance}km from {village_data.get('name', 'village')} centroid."
        if mismatch else "GPS within acceptable range."
    )

    normalized = dict(result)
    normalized.update({
        "location_mismatch": bool(result.get("location_mismatch", mismatch)),
        "distance_km": distance,
        "verdict": verdict,
        "escalation_required": bool(result.get("escalation_required") or verdict == "SEVERE_LOCATION_MISMATCH"),
        "reason": reason,
        "mismatch_explanation": result.get("mismatch_explanation") or reason,
        "gps_distribution": result.get("gps_distribution") or distribution_gps,
        "village_centroid": result.get("village_centroid") or {
            "lat": village_data.get("lat"),
            "lng": village_data.get("lng"),
        },
        "fallback_used": bool(result.get("fallback_used", False)),
    })
    return normalized


# ══════════════════════════════════════════════
# C1: REGISTRY VALIDATION
# ══════════════════════════════════════════════

def run_c1(client, beneficiary_entry, existing_registry=None):
    """Validate a beneficiary entry: CNIC format, duplicates, fields, entitlements."""
    config = _load_config("c1_registry.json")
    t0 = time.time()

    # Fetch existing registry for duplicate check if not provided
    if existing_registry is None:
        village_id = beneficiary_entry.get("village_id", "VIL_002")
        try:
            existing_registry = _api_get(f"/api/beneficiaries/{village_id}")["data"]
        except Exception:
            existing_registry = []

    user_prompt = json.dumps({
        "new_entry": beneficiary_entry,
        "existing_registry": existing_registry,
        "validation_rules": config["validation_rules"],
    }, indent=2, ensure_ascii=False)

    result = _safe_call_gemini(
        client,
        config,
        user_prompt,
        lambda reason: _local_c1_fallback(beneficiary_entry, existing_registry, reason),
    )
    result = _normalize_c1_output(result, beneficiary_entry, existing_registry)
    latency = time.time() - t0

    _post_trace(
        agent_id="C1_REGISTRY",
        input_summary=f"Validating beneficiary: {beneficiary_entry.get('head_name', 'N/A')}",
        observations=f"Valid: {result.get('valid')}, Duplicate: {result.get('duplicate_detected')}",
        reasoning=", ".join(result.get("rejection_reasons", [])) or "All checks passed",
        decision="VALID" if result.get("valid") else "REJECTED",
        action_taken="Entry accepted" if result.get("valid") else "Entry rejected",
        tool_calls=[{"tool_name": "get_beneficiaries", "input": beneficiary_entry.get("village_id")}],
        output_summary=json.dumps(result, ensure_ascii=False)[:500],
    )

    return {"output": result, "latency_s": latency}


# ══════════════════════════════════════════════
# C2: AUDIT ANOMALY DETECTION
# ══════════════════════════════════════════════

def run_c2(client, distribution_entry, officer_history=None):
    """Run statistical anomaly detection on a distribution log entry."""
    config = _load_config("c2_audit.json")
    t0 = time.time()

    # Fetch market prices for price comparison
    prices_data = _api_get("/api/prices")

    # Fetch beneficiary count for village
    village_id = distribution_entry.get("village_id", "VIL_002")
    try:
        ben_data = _api_get(f"/api/beneficiaries/{village_id}")
        registered_households = ben_data["count"]
    except Exception:
        registered_households = distribution_entry.get("registered_households", 100)

    user_prompt = json.dumps({
        "distribution_entry": distribution_entry,
        "registered_households_in_village": registered_households,
        "market_prices": prices_data["data"],
        "officer_distribution_history": officer_history or [],
        "ndma_guideline_tents_per_household": 1.0,
        "checks": config["checks"],
    }, indent=2, ensure_ascii=False)

    result = _safe_call_gemini(
        client,
        config,
        user_prompt,
        lambda reason: _local_c2_fallback(distribution_entry, registered_households, reason),
    )
    latency = time.time() - t0

    _post_trace(
        agent_id="C2_AUDIT",
        input_summary=f"Auditing distribution at {village_id}: "
                      f"{distribution_entry.get('total_tents', 0)} tents",
        observations=f"Flags: {result.get('anomaly_flags')}, "
                     f"Status: {result.get('audit_status')}",
        reasoning=result.get("escalation_brief", "No anomalies"),
        decision=result.get("audit_status", "PASS"),
        action_taken="Escalation sent" if result.get("escalation_required") else "No escalation",
        tool_calls=[
            {"tool_name": "get_prices", "input": "/api/prices"},
            {"tool_name": "get_beneficiaries", "input": f"/api/beneficiaries/{village_id}"},
        ],
        output_summary=json.dumps(result, ensure_ascii=False)[:500],
    )

    return {"output": result, "latency_s": latency}


# ══════════════════════════════════════════════
# C3: GPS GEOVERIFICATION
# ══════════════════════════════════════════════

def run_c3(client, distribution_gps, village_id):
    """Validate GPS coordinates against village centroid."""
    config = _load_config("c3_geoverify.json")
    t0 = time.time()

    # Fetch village data for centroid
    village_data = _api_get(f"/api/villages/{village_id}")

    user_prompt = json.dumps({
        "gps_distribution": distribution_gps,
        "village_id": village_id,
        "village_centroid": {"lat": village_data["lat"], "lng": village_data["lng"]},
        "village_name": village_data["name"],
        "thresholds": config["thresholds"],
    }, indent=2, ensure_ascii=False)

    result = _safe_call_gemini(
        client,
        config,
        user_prompt,
        lambda reason: _local_c3_fallback(distribution_gps, village_data, reason),
    )
    result = _normalize_c3_output(result, distribution_gps, village_data)
    latency = time.time() - t0

    _post_trace(
        agent_id="C3_GEOVERIFY",
        input_summary=f"GPS verify: distribution at ({distribution_gps['lat']:.4f}, "
                      f"{distribution_gps['lng']:.4f}) vs {village_data['name']}",
        observations=f"Distance: {result.get('distance_km', '?')}km, "
                     f"Verdict: {result.get('verdict')}",
        reasoning=result.get("mismatch_explanation", "GPS within acceptable range"),
        decision=result.get("verdict", "PASS"),
        action_taken="Escalation" if result.get("escalation_required") else "No action",
        tool_calls=[{"tool_name": "get_village", "input": f"/api/villages/{village_id}"}],
        output_summary=json.dumps(result, ensure_ascii=False)[:500],
    )

    return {"output": result, "latency_s": latency}


# ══════════════════════════════════════════════
# COMBINED PIPELINE
# ══════════════════════════════════════════════

def run_full_audit(client, distribution_entry, beneficiary_entry=None):
    """
    Run the complete audit pipeline: C1 -> C2 -> C3.

    Args:
        client: google.genai.Client instance
        distribution_entry: dict with village_id, total_tents, officer_id,
                           invoice_prices, gps_distribution, etc.
        beneficiary_entry: optional dict for C1 validation

    Returns:
        Combined audit result with all flags and traces.
    """
    results = {}
    all_flags = []
    escalation_required = False

    # C1: Registry validation (if beneficiary entry provided)
    if beneficiary_entry:
        c1 = run_c1(client, beneficiary_entry)
        results["c1_registry"] = c1
        if not c1["output"].get("valid"):
            all_flags.append("REGISTRY_INVALID")
        if c1["output"].get("duplicate_detected"):
            all_flags.append("DUPLICATE_CNIC")
        if c1["output"].get("officer_flag"):
            all_flags.append("OFFICER_FLAGGED")
            escalation_required = True

    # C2: Statistical audit
    c2 = run_c2(client, distribution_entry)
    results["c2_audit"] = c2
    all_flags.extend(c2["output"].get("anomaly_flags", []))
    if c2["output"].get("escalation_required"):
        escalation_required = True

    # C3: GPS verification
    gps = distribution_entry.get("gps_distribution")
    village_id = distribution_entry.get("village_id", "VIL_002")
    if gps:
        c3 = run_c3(client, gps, village_id)
        results["c3_geoverify"] = c3
        if c3["output"].get("verdict") != "PASS":
            all_flags.append(c3["output"]["verdict"])
        if c3["output"].get("escalation_required"):
            escalation_required = True

    # Determine final status
    if len(all_flags) == 0:
        final_status = "PASS"
    elif len(all_flags) >= 2 or any("FRAUD" in f or "SEVERE" in f for f in all_flags):
        final_status = "FRAUD_RISK"
    else:
        final_status = "ANOMALY"

    # Write audit log
    audit_result = _api_post("/api/audit/log", {
        "beneficiary_id": (beneficiary_entry or {}).get("cnic", "N/A"),
        "village_id": village_id,
        "officer_id": distribution_entry.get("officer_id", "UNKNOWN"),
        "items_distributed": {
            "tents": distribution_entry.get("total_tents", 0),
            "ration_packs": distribution_entry.get("total_ration_packs", 0),
            "cash_pkr": distribution_entry.get("total_cash_pkr", 0),
        },
        "gps_distribution": gps or {"lat": 0, "lng": 0},
        "anomaly_flags": all_flags,
        "audit_brief": c2["output"].get("escalation_brief", "No anomalies detected."),
    })

    # Escalate if needed
    if escalation_required:
        _api_post("/api/notify", {
            "type": "AUDIT_FLAG",
            "recipient_phone": "+92-300-9990002",
            "message": (f"AUDIT ALERT for {village_id}: "
                        f"{len(all_flags)} flag(s) detected. "
                        f"Status: {final_status}. "
                        f"Flags: {', '.join(all_flags)}. "
                        f"Brief: {c2['output'].get('escalation_brief', 'N/A')[:200]}"),
            "metadata": {"audit_log_id": audit_result.get("audit_log", {}).get("id"),
                         "flags": all_flags, "status": final_status},
        })

    results["final"] = {
        "audit_status": final_status,
        "all_flags": all_flags,
        "escalation_required": escalation_required,
        "audit_log_id": audit_result.get("audit_log", {}).get("id"),
    }

    return results
