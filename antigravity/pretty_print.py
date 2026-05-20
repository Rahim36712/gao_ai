"""
Gaon Guard AI - Console Pretty Printer
Formats agent outputs as human-readable tables instead of raw JSON.
Works on Windows cmd/powershell (ASCII-safe).
"""

import sys
import io

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass


# ANSI color codes
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"
    BLUE = "\033[94m"


def _box(title, width=62):
    """Print a boxed section header."""
    pad = width - len(title) - 4
    print(f"\n  {C.CYAN}{'=' * width}{C.RESET}")
    print(f"  {C.CYAN}|{C.RESET}  {C.BOLD}{C.WHITE}{title}{C.RESET}{' ' * max(pad, 1)}{C.CYAN}|{C.RESET}")
    print(f"  {C.CYAN}{'=' * width}{C.RESET}")


def _row(label, value, color=C.WHITE):
    """Print a key-value row."""
    print(f"  {C.DIM}|{C.RESET}  {C.BOLD}{label:.<28s}{C.RESET} {color}{value}{C.RESET}")


def _badge(text, color=C.GREEN):
    """Return a colored badge string."""
    return f"{color}[{text}]{C.RESET}"


def print_header(title, subtitle=""):
    """Print a major section header."""
    w = 62
    print(f"\n  {C.CYAN}+{'=' * (w - 2)}+{C.RESET}")
    pad = w - len(title) - 4
    print(f"  {C.CYAN}|{C.RESET}  {C.BOLD}{C.WHITE}{title}{C.RESET}{' ' * max(pad, 1)}{C.CYAN}|{C.RESET}")
    if subtitle:
        pad2 = w - len(subtitle) - 4
        print(f"  {C.CYAN}|{C.RESET}  {C.DIM}{subtitle}{C.RESET}{' ' * max(pad2, 1)}{C.CYAN}|{C.RESET}")
    print(f"  {C.CYAN}+{'=' * (w - 2)}+{C.RESET}")


def print_agent_header(agent_name, agent_desc):
    """Print an agent section header."""
    _box(f">> {agent_name} -- {agent_desc}")


def print_a1(result, latency):
    """Pretty-print A1 Intake output."""
    _box(f"A1 RESULT  ({latency:.1f}s)")
    _row("Location", result.get("location_name", "-"), C.GREEN)
    _row("District (guess)", result.get("district_guess") or "-")

    crisis = result.get("crisis_type", [])
    badges = "  ".join([
        _badge(c, C.RED if c in ("FLOOD", "HEALTH") else C.YELLOW)
        for c in crisis
    ])
    _row("Crisis Signals", badges)
    _row("Affected Group", result.get("affected_group") or "-")
    _row("Duration", f'{result.get("duration_hours", "?")} hours')
    missing = result.get("missing_person_signal", False)
    _row("Missing Person?", "!! YES !!" if missing else "No",
         C.RED if missing else C.GREEN)

    raw = result.get("raw_signals", [])
    if raw:
        print(f"  {C.DIM}|{C.RESET}")
        print(f"  {C.DIM}|  Raw signals:{C.RESET}")
        for s in raw:
            print(f"  {C.DIM}|    * {s}{C.RESET}")
    print()


def print_a2(result, latency):
    """Pretty-print A2 Evidence output."""
    conf = result.get("confidence", "?")
    conf_color = {
        "HIGH": C.GREEN, "MEDIUM": C.YELLOW, "LOW": C.RED
    }.get(conf, C.WHITE)

    _box(f"A2 RESULT  ({latency:.1f}s)")
    _row("Confidence", conf, conf_color)
    print(f"  {C.DIM}|{C.RESET}")

    checks = result.get("evidence_checks", [])
    for i, ev in enumerate(checks):
        src = ev.get("source", "?")
        verdict = ev.get("verdict", "?")
        v_color = {"SUPPORTS": C.GREEN, "CONTRADICTS": C.RED,
                   "NEUTRAL": C.YELLOW}.get(verdict, C.WHITE)
        val = ev.get("value_retrieved", "")

        num = f"[{i + 1}/{len(checks)}]"
        print(f"  {C.DIM}|{C.RESET}  {C.BOLD}{src:.<20s}{C.RESET} {_badge(verdict, v_color)}  {C.DIM}{num}{C.RESET}")
        if val:
            val = str(val)
            short = val[:80] + ("..." if len(val) > 80 else "")
            print(f"  {C.DIM}|     -> {short}{C.RESET}")
    print()


def print_a3(result, latency):
    """Pretty-print A3 Severity output."""
    score = result.get("severity_score", "?")
    _box(f"A3 RESULT  ({latency:.1f}s)")

    if isinstance(score, (int, float)):
        if score >= 4:
            sc = C.RED
        elif score >= 3:
            sc = C.YELLOW
        else:
            sc = C.GREEN
        bar = "#" * int(score) + "." * (5 - int(score))
        _row("Severity Score", f"{score}/5  {sc}[{bar}]{C.RESET}", sc)
    else:
        _row("Severity Score", str(score))

    auth = result.get("authorization")
    if auth:
        auth_color = C.GREEN if auth == "DISPATCH" else C.RED
        _row("Authorization", auth, auth_color)

    verify = result.get("must_verify")
    if verify:
        _row("Must Verify", ", ".join(verify) if isinstance(verify, list) else str(verify), C.YELLOW)

    breakdown = result.get("weight_breakdown", {})
    if breakdown:
        print(f"  {C.DIM}|{C.RESET}")
        print(f"  {C.DIM}|  Weight Breakdown:{C.RESET}")
        for k, v in breakdown.items():
            print(f"  {C.DIM}|    * {k}: {v}{C.RESET}")
    print()


def print_summary(a1_result, a2_result, a3_result, a1_t, a2_t, a3_t):
    """Print the final pipeline summary."""
    total = a1_t + a2_t + a3_t
    print_header("PIPELINE COMPLETE", f"Total runtime: {total:.1f}s")

    print(f"\n  {C.DIM}  Timing:{C.RESET}")
    print(f"    A1 Intake ...... {a1_t:.1f}s")
    print(f"    A2 Evidence .... {a2_t:.1f}s")
    print(f"    A3 Severity .... {a3_t:.1f}s")
    print(f"    {'-' * 25}")
    print(f"    {C.BOLD}Total .......... {total:.1f}s{C.RESET}")

    loc = a1_result.get("location_name", "?")
    crisis = a1_result.get("crisis_type", [])
    missing = a1_result.get("missing_person_signal", False)
    conf = a2_result.get("confidence", "?")
    score = a3_result.get("severity_score", "?")
    auth = a3_result.get("authorization")

    print(f"\n  {C.DIM}  Decision Summary:{C.RESET}")
    print(f"    Village: {C.GREEN}{loc}{C.RESET}")
    print(f"    Signals: {' '.join([_badge(c, C.RED) for c in crisis])}")
    miss_label = f"{C.RED}!! YES !!{C.RESET}" if missing else f"{C.GREEN}No{C.RESET}"
    print(f"    Missing Child: {miss_label}")
    print(f"    Evidence Confidence: {C.BOLD}{conf}{C.RESET}")

    if isinstance(score, (int, float)):
        bar = "#" * int(score) + "." * (5 - int(score))
        sc = C.RED if score >= 4 else C.YELLOW if score >= 3 else C.GREEN
        print(f"    Severity: {sc}{score}/5 [{bar}]{C.RESET}")

    if auth:
        ac = C.GREEN if auth == "DISPATCH" else C.RED
        print(f"    Authorization: {ac}{auth}{C.RESET}")

    print()
