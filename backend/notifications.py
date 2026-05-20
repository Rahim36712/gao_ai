"""
Gaon Guard AI — FCM Simulation / Notification Layer
Simulates SMS and push notifications by logging to Firestore.
No real SMS or FCM messages are sent — all entries are marked SIMULATED.

All data is SYNTHETIC DEMO DATA.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field
from firebase_config import get_db


# ──────────────────────────────────────────────
# Notification types
# ──────────────────────────────────────────────

VALID_TYPES = {
    "FAMILY_ALERT",      # Notify family of missing person match
    "TEAM_DISPATCH",     # Notify field team of new dispatch
    "TEAM_REMINDER",     # Follow-up reminder to field team
    "ESCALATION",        # Escalation alert to DC / supervisor
    "AUDIT_FLAG",        # Audit anomaly notification
}


# ──────────────────────────────────────────────
# Pydantic model for API validation
# ──────────────────────────────────────────────

class NotificationRequest(BaseModel):
    type: str = Field(..., description="Notification type")
    recipient_phone: str = Field(..., description="Target phone number")
    message: str = Field(..., description="Notification body")
    metadata: Optional[dict] = Field(default_factory=dict, description="Extra context")


# ──────────────────────────────────────────────
# Core function
# ──────────────────────────────────────────────

def create_notification(
    notif_type: str,
    recipient_phone: str,
    message: str,
    metadata: Optional[dict] = None,
) -> dict:
    """
    Create a simulated notification and log it to Firestore.

    Args:
        notif_type: One of FAMILY_ALERT, TEAM_DISPATCH, TEAM_REMINDER,
                    ESCALATION, AUDIT_FLAG
        recipient_phone: Target phone number (e.g., +92-300-5551001)
        message: Notification message body
        metadata: Optional dict of extra context (crisis_event_id, team_id, etc.)

    Returns:
        dict with notification ID and status

    Raises:
        ValueError: If notif_type is not valid
    """
    if notif_type not in VALID_TYPES:
        raise ValueError(
            f"Invalid notification type '{notif_type}'. "
            f"Valid types: {sorted(VALID_TYPES)}"
        )

    notif_id = f"NOTIF_{uuid.uuid4().hex[:12].upper()}"
    now = datetime.now(timezone.utc)

    doc_data = {
        "id": notif_id,
        "type": notif_type,
        "recipient_phone": recipient_phone,
        "message": message,
        "metadata": metadata or {},
        "status": "SIMULATED",
        "created_at": now,
    }

    # Write to Firestore
    db = get_db()
    db.collection("notifications_log").document(notif_id).set(doc_data)

    result = {
        "notification_id": notif_id,
        "type": notif_type,
        "recipient_phone": recipient_phone,
        "status": "SIMULATED",
        "message_preview": message[:80] + ("..." if len(message) > 80 else ""),
        "created_at": now.isoformat(),
        "note": "No real SMS/FCM sent — logged to Firestore notifications_log",
    }

    print(
        f"[NOTIF] {notif_type} → {recipient_phone} | "
        f"{notif_id} | SIMULATED"
    )

    return result
