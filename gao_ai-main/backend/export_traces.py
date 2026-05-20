"""
Gaon Guard AI — Trace Export Script
Exports all agent trace entries to a submission-ready JSON file.
All data is SYNTHETIC DEMO DATA.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from edge_cases import trigger_edge_case, agent_traces


def export_traces():
    """Generate all demo traces and export to submission file."""
    print("Generating traces from all 6 edge cases...")

    # Clear any previous traces
    agent_traces.clear()

    # Trigger all 6 edge cases to populate traces
    for i in range(1, 7):
        result = trigger_edge_case(i)
        print(f"  Case {i}: {result['title']} -> {len(result['traces'])} traces")

    total = len(agent_traces)
    print(f"\nTotal traces generated: {total}")

    # Build export document
    export = {
        "_doc": "Gaon Guard AI - Antigravity Agent Trace Export",
        "_note": "ALL DATA IS SYNTHETIC DEMO DATA",
        "export_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_traces": total,
        "edge_cases_triggered": list(range(1, 7)),
        "traces": agent_traces,
    }

    # Write to submission file
    out_dir = Path(__file__).resolve().parent.parent / "antigravity"
    out_path = out_dir / "submission_traces.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2, ensure_ascii=False)

    print(f"Exported to: {out_path}")
    print(f"Trace count: {total}")

    # Verify key traces exist
    agents_found = set(t["agent"] for t in agent_traces)
    required = {"A1_INTAKE", "A2_EVIDENCE", "A3_SEVERITY", "A4_DISPATCH",
                "X_COORDINATOR", "B1_SCANNER", "B2_MATCHER", "C1_REGISTRY", "C2_AUDIT"}
    missing = required - agents_found
    if missing:
        print(f"WARNING: Missing agent traces: {missing}")
    else:
        print("All required agent traces present.")

    return export


if __name__ == "__main__":
    export_traces()
