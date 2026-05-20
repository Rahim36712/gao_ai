# Gaon Guard AI — Demo Video Script

> All data shown is **SYNTHETIC DEMO DATA**. No real individuals are represented.

## Video 1: Full App Demo (4 minutes)

### 0:00–0:15 — Title Card
- Show: App splash / Screen 1
- Say: *"This is Gaon Guard AI — a 3-engine agentic crisis intelligence system for rural Pakistan, built for the Google Antigravity Hackathon, Challenge 3."*
- Highlight: SYNTHETIC DEMO DATA label visible at top

### 0:15–0:45 — Screen 1: Crisis Report Input
- Show: Pre-filled complaint in Roman Urdu
- Say: *"A field worker in Ali Pur has submitted a complaint in Roman Urdu: 'pani khara hai, bachay diarrhea se beemar hain, bacha nazar nahi aa raha.' This means standing water, children sick with diarrhea, and a child missing."*
- Action: Tap **"Analyze & Report"** button

### 0:45–1:15 — Screen 2: AI Signal Extraction
- Show: Shimmer loading animation (2 seconds)
- Show: Badges appearing one by one — FLOOD (blue), HEALTH (red), MISSING_PERSON (orange)
- Say: *"Agent A1 parses the Roman Urdu complaint in 1.8 seconds and extracts three crisis signals: flood, health emergency, and a missing person. Notice the orange banner — Engine 2 has been automatically activated to search for the missing child."*

### 1:15–1:45 — Screen 3: Evidence Panel
- Show: 5 evidence cards loading one at a time
- Highlight: Weather card showing "0mm rainfall" with red CONTRADICTS badge
- Say: *"Agent A2 cross-references 5 data sources. Road status is blocked — supports the claim. But weather data shows 0mm rainfall, which contradicts the flood report. This triggers the Coordinator Agent."*
- Show: Orange warning banner "Conflict detected — Coordinator Agent reviewing"

### 1:45–2:15 — Screen 4: Severity Dashboard
- Show: Animated gauge filling to 4.0/5.0
- Highlight: HOLD — COORDINATOR REVIEW banner
- Say: *"Agent A3 scores severity at 4.0, but dispatch is held. Agent X, the Coordinator, has generated three hypotheses: weather station lag, irrigation canal breach, or exaggerated report. It sends an SMS to the focal person to verify."*
- Show: Agent X reasoning card

### 2:15–2:45 — Screen 5: Response Plan
- Show: Three department cards appearing simultaneously
- Say: *"Once verified, three teams are dispatched in parallel: Rescue 1122 for flood response, a Mobile Medical Unit, and Crop Assessors. Each has a calculated ETA based on Haversine distance."*
- Action: Tap **"Track Live"** on the first card

### 2:45–3:10 — Screen 6: Dispatch Tracker
- Show: Timeline view with status nodes
- Highlight: Escalation card (red) for TKT-992
- Say: *"One team hasn't moved in 30 minutes. Agent A4 detects the non-movement via GPS monitoring and escalates — sending a reminder, then reassigning to the next nearest team."*

### 3:10–3:25 — Screen 7: Missing Persons (Tab 2)
- Show: Orange POSSIBLE MATCH FOUND banner
- Say: *"Engine 2 has found a 78% match for the missing boy Hassan Ali in Camp Dadu 02. The family has been alerted automatically."*
- Tap: Expand to show side-by-side comparison

### 3:25–3:40 — Screen 8: Aid Distribution (Tab 3)
- Show: CNIC verification and fraud detection
- Say: *"When 500 tents are logged for 120 households, Agent C2 instantly flags a quantity anomaly — 4.17 tents per household against the NDMA guideline of 1.0. The red Fraud Risk card appears immediately."*

### 3:40–3:55 — Screen 9: Agent Traces (Tab 4)
- Show: Scrolling through trace entries
- Highlight: Purple-bordered Agent X arbitration entry
- Say: *"Every decision by every agent is logged in the trace viewer. Operators can filter by agent, expand reasoning, and audit the entire decision chain."*

### 3:55–4:00 — Screen 10: Before vs After
- Action: Tap **"Before vs After"** button in top right
- Show: Comparison table
- Say: *"What used to take hours of manual work now happens in under 30 seconds, with full transparency and accountability."*

---

## Video 2: Antigravity Console Demo (2.5 minutes)

### 0:00–0:10 — Terminal Setup
- Show: VS Code terminal
- Say: *"Let me show you the Antigravity agents working in the terminal."*
- Run: `cd antigravity`

### 0:10–0:30 — Set API Key and Start
- Run: `$env:GEMINI_API_KEY="AIza..."`
- Run: `python test_a1_a3.py`
- Say: *"We're running the A1 through A3 pipeline — intake, evidence, and severity."*

### 0:30–1:00 — A1 Output
- Show: Agent A1 JSON output appearing
- Highlight: `crisis_type: ["FLOOD", "HEALTH", "MISSING_PERSON"]`
- Say: *"A1 has parsed the Roman Urdu and correctly identified all three crisis types. Note the missing_person_signal is true."*

### 1:00–1:30 — A2 Evidence
- Show: 5 data sources being fetched
- Highlight: Weather CONTRADICTS
- Say: *"A2 has fetched all 5 data sources. Weather shows 0mm rainfall — a contradiction. This will trigger the Coordinator."*

### 1:30–2:00 — A3 + Summary
- Show: Severity score output
- Say: *"A3 scores severity at 4.0. The full pipeline completed in under 10 seconds."*
- Show: Summary table at bottom

### 2:00–2:20 — Edge Case Demo
- Run: `python test_a4_x.py`
- Say: *"Now let's trigger the dispatch and coordinator test. Watch Agent X generate its 3 hypotheses for the weather contradiction."*
- Highlight: Coordinator X output with hypotheses

### 2:20–2:30 — Closing
- Say: *"All 11 agents, 4 test pipelines, 6 edge cases — all running on Google Antigravity with full trace logging. This is Gaon Guard AI."*
