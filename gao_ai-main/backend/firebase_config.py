"""
Gaon Guard AI — Firebase Configuration
Shared Firebase Admin SDK initialization.

Expects a service account key file at one of:
  1. Path set in GOOGLE_APPLICATION_CREDENTIALS env var
  2. backend/serviceAccountKey.json (gitignored)

For the hackathon demo, download the key from Firebase Console:
  Project Settings → Service Accounts → Generate New Private Key
"""

import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

# ──────────────────────────────────────────────
# Singleton initialization
# ──────────────────────────────────────────────

_db = None


def get_db():
    """Return the Firestore client, initializing Firebase on first call."""
    global _db
    if _db is not None:
        return _db

    # Try env var first, then local file
    key_path = os.environ.get(
        "GOOGLE_APPLICATION_CREDENTIALS",
        str(Path(__file__).resolve().parent / "serviceAccountKey.json"),
    )

    if not Path(key_path).exists():
        raise FileNotFoundError(
            f"Firebase service account key not found at: {key_path}\n"
            "Please download it from Firebase Console > Project Settings > "
            "Service Accounts > Generate New Private Key, and save it as:\n"
            "  backend/serviceAccountKey.json\n"
            "Or set GOOGLE_APPLICATION_CREDENTIALS env var."
        )

    if not firebase_admin._apps:
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)

    _db = firestore.client()
    return _db
