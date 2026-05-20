# Gaon Guard AI — Firestore Real-Time Listeners Specification

> **Version:** 0.2.0
> **Status:** Specification — Flutter implementation pending
> **Data:** All data is SYNTHETIC DEMO DATA

---

## Overview

The Flutter mobile app connects to Firestore using `onSnapshot()` listeners to receive
real-time updates without polling. Each listener maps to a specific screen or widget and
reacts to server-side document writes from the FastAPI backend and AI agents.

---

## Listener 1: Crisis Events

**Collection:** `crisis_events`

**Query:**
```dart
FirebaseFirestore.instance
    .collection('crisis_events')
    .where('status', whereIn: ['WATCHLIST', 'ACTIVE', 'ESCALATED'])
    .orderBy('severity_score', descending: true)
    .snapshots()
```

**Triggers on:**
- New crisis event created (status → WATCHLIST)
- Status change: WATCHLIST → ACTIVE → ESCALATED → RESOLVED
- Severity score update
- New signals added

**Used by screens:**
- Screen 1: Crisis Dashboard (main list)
- Screen 2: Crisis Detail View (single document listener)

**Latency expectation:** < 2 seconds from Firestore write to Flutter UI update

---

## Listener 2: Dispatch Tickets

**Collection:** `dispatch_tickets`

**Query (DC-level — all active tickets):**
```dart
FirebaseFirestore.instance
    .collection('dispatch_tickets')
    .where('status', whereNotIn: ['CONFIRMED', 'DISPUTED'])
    .orderBy('assigned_at', descending: true)
    .snapshots()
```

**Query (team-level — my tickets):**
```dart
FirebaseFirestore.instance
    .collection('dispatch_tickets')
    .where('team_id', isEqualTo: currentTeamId)
    .where('status', whereNotIn: ['CONFIRMED'])
    .snapshots()
```

**Triggers on:**
- New ticket assigned (ASSIGNED)
- Status transitions: ASSIGNED → ACCEPTED → EN_ROUTE → ARRIVED → EVIDENCE_UPLOADED
- GPS check-in recorded
- Escalation event added
- Field note updated

**Used by screens:**
- Screen 3: Dispatch Board (DC view)
- Screen 4: Team Action View (field team view)
- Screen 5: Evidence Upload Confirmation

**Latency expectation:** < 1 second (critical for field coordination)

---

## Listener 3: Missing Persons Live

**Collection:** `missing_persons_live`

**Query:**
```dart
FirebaseFirestore.instance
    .collection('missing_persons_live')
    .where('status', whereIn: ['OPEN', 'PENDING_MATCH'])
    .orderBy('last_seen_time', descending: true)
    .snapshots()
```

**Triggers on:**
- New missing person report created (OPEN)
- Match score updated by AI matching agent
- Status change: OPEN → PENDING_MATCH → CONFIRMED_FOUND
- `matched_camp_id` populated
- Family alert sent (`alert_sent_at` set)

**Used by screens:**
- Screen 6: Missing Persons Tracker
- Screen 7: Match Confirmation View

**Latency expectation:** < 2 seconds

---

## Listener 4: Agent Traces

**Collection:** `agent_traces`

**Query (by crisis event):**
```dart
FirebaseFirestore.instance
    .collection('agent_traces')
    .where('crisis_event_id', isEqualTo: selectedCrisisId)
    .orderBy('timestamp', descending: true)
    .limit(50)
    .snapshots()
```

**Query (global — latest traces):**
```dart
FirebaseFirestore.instance
    .collection('agent_traces')
    .orderBy('timestamp', descending: true)
    .limit(20)
    .snapshots()
```

**Triggers on:**
- New trace entry appended by any agent
- Error recovery field updated

**Used by screens:**
- Screen 9: Agent Trace / Explainability Viewer
- Screen 2: Crisis Detail (embedded trace timeline)

**Latency expectation:** < 3 seconds (explainability is supplementary, not critical-path)

---

## Listener 5: Notifications Log (Optional)

**Collection:** `notifications_log`

**Query:**
```dart
FirebaseFirestore.instance
    .collection('notifications_log')
    .orderBy('created_at', descending: true)
    .limit(50)
    .snapshots()
```

**Triggers on:**
- New notification logged (simulated SMS/FCM)

**Used by screens:**
- Screen 10: Notification History (admin/debug view)

**Latency expectation:** < 3 seconds

---

## Security Rules (Recommended for Production)

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // Crisis events: read by authenticated users, write by backend only
    match /crisis_events/{eventId} {
      allow read: if request.auth != null;
      allow write: if request.auth.token.role == 'backend';
    }

    // Dispatch tickets: read by team members, write by backend
    match /dispatch_tickets/{ticketId} {
      allow read: if request.auth != null;
      allow update: if request.auth.token.role in ['field_team', 'backend'];
      allow create: if request.auth.token.role == 'backend';
    }

    // Missing persons: read by all auth, write by backend
    match /missing_persons_live/{caseId} {
      allow read: if request.auth != null;
      allow write: if request.auth.token.role == 'backend';
    }

    // Aid distribution: read by auditors, write by backend
    match /aid_distribution_log/{logId} {
      allow read: if request.auth.token.role in ['auditor', 'backend'];
      allow write: if request.auth.token.role == 'backend';
    }

    // Agent traces: read by all auth, write by backend
    match /agent_traces/{traceId} {
      allow read: if request.auth != null;
      allow write: if request.auth.token.role == 'backend';
    }

    // Notifications: read by admins, write by backend
    match /notifications_log/{notifId} {
      allow read: if request.auth.token.role in ['admin', 'backend'];
      allow write: if request.auth.token.role == 'backend';
    }
  }
}
```

> **Note:** For the hackathon demo, Firestore rules are set to open/test mode.
> The rules above are a reference for production deployment.

---

## Connection Lifecycle

1. **App Start:** Establish listeners for `crisis_events` and `dispatch_tickets`
2. **Screen Navigation:** Add/remove listeners per-screen to avoid unnecessary reads
3. **Background:** Maintain `crisis_events` listener for push-style notifications
4. **Offline:** Firestore SDK handles offline caching automatically; sync on reconnect

---

## Data Flow Diagram

```
┌─────────────────┐     Firestore Write     ┌──────────────────┐
│   FastAPI        │ ──────────────────────► │   Firestore      │
│   Backend        │                         │   Collections    │
│                  │                         │                  │
│  /api/crisis/*   │                         │  crisis_events   │
│  /api/dispatch/* │                         │  dispatch_tickets│
│  /api/missing/*  │                         │  missing_persons │
│  /api/audit/*    │                         │  aid_dist_log    │
│  /api/traces/*   │                         │  agent_traces    │
│  /api/notify     │                         │  notifications   │
└─────────────────┘                         └────────┬─────────┘
                                                     │
                                              onSnapshot()
                                                     │
                                                     ▼
                                            ┌──────────────────┐
                                            │   Flutter App    │
                                            │                  │
                                            │  StreamBuilder   │
                                            │  widgets react   │
                                            │  to doc changes  │
                                            └──────────────────┘
```
