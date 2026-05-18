# Gaon Guard AI — Mock Data Documentation

> **⚠️ ALL DATA IN THIS PROJECT IS SYNTHETIC DEMO DATA**
> Created for the Google Antigravity Hackathon (Challenge 3).
> No real personal information, locations, or events are represented.

---

## Dataset Overview

| # | File | Records | Description |
|---|------|---------|-------------|
| 1 | `villages.json` | 50 | Village profiles across Sindh & Punjab |
| 2 | `weather.json` | 14 | Per-district 24hr weather window |
| 3 | `teams.json` | 20 | Response teams (4 departments × 5) |
| 4 | `health_reports.json` | 30 | Per-BHU health surveillance |
| 5 | `missing_persons.json` | 10 | Open missing person cases |
| 6 | `camp_registrations.json` | 20 | Relief camp intake records |
| 7 | `beneficiary_registry.json` | 200 | Aid beneficiary household records |
| 8 | `market_prices.json` | 10 | Relief supply market prices |
| 9 | `road_status.json` | 50 | Per-village road accessibility |

---

## 1. villages.json

Village profiles for the crisis-affected area.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique village ID (e.g., `VIL_001`) |
| `name` | string | Village name |
| `district` | string | Administrative district |
| `province` | string | Province (Sindh or Punjab) |
| `lat` | float | Latitude |
| `lng` | float | Longitude |
| `population` | int | Estimated population |
| `households` | int | Number of households |
| `risk_zone` | enum | `HIGH_FLOOD`, `MEDIUM_FLOOD`, or `LOW_FLOOD` |
| `nearest_bhu` | string | ID of nearest Basic Health Unit |
| `main_road_status` | enum | `OPEN`, `BLOCKED`, or `DAMAGED` |
| `alt_route` | string | Alternative route description |
| `flood_history` | string[] | Years of previous flooding |

**Key demo records:**
- `VIL_001` — Ali Pur (Larkana, Sindh) — `HIGH_FLOOD`, road `BLOCKED`
- `VIL_002` — Basti Malook (Dadu, Sindh) — `MEDIUM_FLOOD`
- `VIL_003` — Khairpur Tamewali (Bahawalpur, Punjab) — `LOW_FLOOD`

---

## 2. weather.json

24-hour weather readings per district.

| Field | Type | Description |
|-------|------|-------------|
| `district` | string | District name |
| `timestamp` | ISO8601 | Reading timestamp |
| `rainfall_mm_24hr` | float | 24-hour cumulative rainfall (mm) |
| `rainfall_mm_6hr` | float | 6-hour cumulative rainfall (mm) |
| `flood_alert` | enum | `RED`, `ORANGE`, or `GREEN` |
| `temperature_c` | float | Temperature in Celsius |
| `humidity_pct` | int | Relative humidity percentage |

**Key demo record:** Larkana — `rainfall_mm_24hr: 95.4`, `flood_alert: RED`

---

## 3. teams.json

Emergency response teams across 4 departments.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Team ID (e.g., `TEAM_001`) |
| `name` | string | Team name |
| `department` | enum | `DISASTER`, `HEALTH`, `AGRICULTURE`, `RESCUE` |
| `lat` | float | Current latitude |
| `lng` | float | Current longitude |
| `status` | enum | `AVAILABLE`, `DEPLOYED`, `OFFLINE` |
| `capacity` | int | Team member count |
| `equipment` | string[] | Available equipment |
| `phone` | string | Contact phone number |

**Distribution:** 5 teams per department, spread across Sindh and Punjab.

---

## 4. health_reports.json

Health surveillance data per Basic Health Unit (BHU).

| Field | Type | Description |
|-------|------|-------------|
| `bhu_id` | string | BHU identifier |
| `district` | string | District |
| `village_id` | string | Associated village ID |
| `diarrhea_cases_7day` | int | Diarrhea cases in last 7 days |
| `cholera_alerts` | int | Active cholera alerts |
| `malaria_cases` | int | Malaria cases |
| `date_updated` | date | Last update date |

**Key demo record:** `BHU_Larkana_03` — `diarrhea_cases_7day: 12`, `cholera_alerts: 1`

---

## 5. missing_persons.json

Open missing person cases during the crisis.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Case ID (e.g., `MP_001`) |
| `name` | string | Person's name |
| `age` | int | Age |
| `gender` | string | Gender |
| `last_seen_village` | string | Village ID where last seen |
| `last_seen_time` | ISO8601 | Time last seen |
| `description` | string | Physical description |
| `family_phone` | string | Family contact number |
| `reported_by` | string | Who reported the case |
| `status` | enum | `OPEN`, `MATCHED`, `FOUND` |

**Key demo record:** Hassan Ali — age 12, male, Ali Pur, blue shalwar kameez, 4ft5in

---

## 6. camp_registrations.json

Relief camp intake registrations.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Registration ID (e.g., `CAMP_REG_001`) |
| `camp_id` | string | Camp identifier |
| `status` | enum | `IDENTIFIED` or `UNIDENTIFIED` |
| `approx_age` | int | Approximate age |
| `gender` | string | Gender |
| `description` | string | Physical/situational description |
| `registered_by` | string | Registering authority |
| `timestamp` | ISO8601 | Registration time |
| `lat` | float | Camp latitude |
| `lng` | float | Camp longitude |

**Key demo record:** `CAMP_REG_019` — unidentified, age ~10, male, blue shalwar kameez, confused, Camp Dadu 02

---

## 7. beneficiary_registry.json

Aid distribution beneficiary records.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Beneficiary ID (e.g., `BEN_0001`) |
| `cnic` | string | Masked CNIC (`XXXXX-XXXXXXX-X`) |
| `head_name` | string | Household head name |
| `village_id` | string | Village ID |
| `household_size` | int | Number in household |
| `damage_level` | enum | `SEVERE`, `MAJOR`, `MODERATE`, `MINOR` |
| `entitlement.tents` | int | Tents allocated |
| `entitlement.ration_packs` | int | Ration packs allocated |
| `entitlement.cash_pkr` | int | Cash assistance in PKR |
| `gps_home.lat` | float | Home GPS latitude |
| `gps_home.lng` | float | Home GPS longitude |
| `registered_by` | string | Registering authority |
| `timestamp` | ISO8601 | Registration time |

**Key constraint:** Basti Malook (`VIL_002`) has exactly **120** registered households.

---

## 8. market_prices.json

Relief supply market price monitoring.

| Field | Type | Description |
|-------|------|-------------|
| `item` | string | Item name |
| `unit` | string | Measurement unit |
| `market_rate_pkr` | int | Current market rate in PKR |
| `govt_guideline_pkr` | int | Government guideline price |
| `flag_threshold_pkr` | int | Price gouging threshold |
| `source` | string | Data source (always `SYNTHETIC`) |

**Key demo record:** `tent_standard` — market: 1800, guideline: 2000, flag: 2800

---

## 9. road_status.json

Road accessibility per village.

| Field | Type | Description |
|-------|------|-------------|
| `village_id` | string | Village ID |
| `main_road_status` | enum | `OPEN`, `BLOCKED`, `DAMAGED` |
| `alt_route` | string | Alternative route if blocked |
| `blocked_since` | ISO8601 | When blockage started (null if OPEN) |
| `cause` | string | Cause of blockage (null if OPEN) |

**Key demo record:** Ali Pur (`VIL_001`) — `BLOCKED` since 2026-05-16T12:00

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/villages` | All 50 villages |
| GET | `/api/villages/{village_id}` | Single village |
| GET | `/api/weather/{district}` | Weather by district |
| GET | `/api/roads/{village_id}` | Road status by village |
| GET | `/api/health/{bhu_id}` | Health report by BHU |
| GET | `/api/teams/available` | All available teams |
| GET | `/api/camps/unidentified` | Unidentified camp registrations |
| GET | `/api/prices` | Market prices |
| GET | `/api/missing/open` | Open missing person cases |
| GET | `/api/beneficiaries/{village_id}` | Beneficiaries by village |
| POST | `/api/demo/load_scenario` | Full Ali Pur demo scenario |

All responses include the `X-Data-Type: SYNTHETIC` header.

---

## Confirmation

✅ **All data in this project is 100% synthetic and generated for demonstration purposes only.**
No real names, CNICs, phone numbers, or geographic data of actual individuals are used.
