#!/usr/bin/env python3
"""
next_ticket — dependency-aware unblocked-frontier resolver for HANDOFFS.md (0 model tokens).

Doctrine: *few token do trick* (`engine/protocols/handoff-and-interconnection.md`
§Dependency-aware next-ticket). `HANDOFFS.md` is a hand-picked queue the brain layer used
to eyeball by gate-order; the optional `depends_on:` ticket field turns it into a real
dependency DAG. This tool answers, deterministically and without model tokens, "which
tickets can START RIGHT NOW" (every open ticket whose `depends_on` are all `done`) — so
parallel worktree squads pick work from a machine frontier, not a judgment call.

Grounded in claude-task-master's `next` (dependency-aware unblocked resolution).
The brain layer scans the frontier; leaves still get one frozen RCCF. Gate-order no-skip
(`00-operating-system.md`) still binds — a dependency edge never lets work jump a gate.

CLI
---
    python3 next_ticket.py --prj PRJ-SAKK              # print the unblocked frontier (+ blocked, with pending deps)
    python3 next_ticket.py --prj PRJ-SAKK --md         # markdown table form
    python3 next_ticket.py --prj PRJ-SAKK --check TKT-014   # exit 0 if startable, 1 if deps unmet, 2 if not found

Exit codes: 0 ok / startable · 1 deps-unmet · 2 usage-or-not-found. Pure stdlib, read-only.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ── workspace resolution (reuse sofi_tools when importable; fallback otherwise) ──
try:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tooling"))
    from sofi_tools import paths as _paths  # type: ignore

    def _context_dir(prj: str) -> Path:
        return _paths.context_dir(prj)
except Exception:  # standalone fallback
    def _context_dir(prj: str) -> Path:
        root = Path(__file__).resolve().parents[4]
        return root / "projects" / prj / "_context"


def _handoffs_path(prj: str) -> Path:
    return _context_dir(prj) / "HANDOFFS.md"


DONE_STATES = {"done", "accepted-done", "closed", "merged"}   # a dep counts satisfied only when truly closed
# A ticket is a *candidate to start* when it is not already finished/dead.
TERMINAL_STATES = {"done", "closed", "merged", "rejected", "cancelled", "canceled"}

_HDR = re.compile(r"^#{1,6}\s+(TKT-[0-9A-Za-z]+)\b(.*)$")
_TKT = re.compile(r"TKT-[0-9A-Za-z]+")


def _parse(md: str) -> "dict[str, dict]":
    """Parse HANDOFFS.md into {tkt_id: {status, depends_on:[...], gate, header}}.

    A ticket block starts at a heading naming a TKT id and runs until the next such
    heading. Within it we read the first `status:` and `depends_on:` fields we see.
    """
    tickets: "dict[str, dict]" = {}
    cur = None
    for raw in md.splitlines():
        m = _HDR.match(raw.strip())
        if m:
            tid = m.group(1)
            gate = ""
            gm = re.search(r"gate\s*([0-9]+)", m.group(2), re.I)
            if gm:
                gate = gm.group(1)
            cur = {"id": tid, "status": "", "depends_on": [], "gate": gate,
                   "header": raw.strip()}
            # last heading for an id wins only if we haven't recorded a status yet;
            # keep the FIRST full block per id (queues append newest last, but the
            # canonical block for an id is its original — status is updated in place).
            tickets.setdefault(tid, cur)
            cur = tickets[tid]
            continue
        if cur is None:
            continue
        low = raw.strip().lower()
        if low.startswith("status:") and not cur["status"]:
            cur["status"] = low.split(":", 1)[1].strip().split()[0] if low.split(":", 1)[1].strip() else ""
        elif low.startswith("depends_on:") and not cur["depends_on"]:
            val = raw.split(":", 1)[1].strip()
            if val.lower() in ("", "none", "-", "n/a", "na"):
                cur["depends_on"] = []
            else:
                cur["depends_on"] = _TKT.findall(val)
    return tickets


def _status(t: dict) -> str:
    return (t.get("status") or "").strip().lower()


def _unmet(tid: str, tickets: dict) -> "list[str]":
    """Return the deps of tid that are NOT satisfied (missing ticket or not done)."""
    t = tickets.get(tid, {})
    unmet = []
    for dep in t.get("depends_on", []):
        d = tickets.get(dep)
        if d is None or _status(d) not in DONE_STATES:
            unmet.append(dep)
    return unmet


def main() -> int:
    ap = argparse.ArgumentParser(prog="next_ticket.py")
    ap.add_argument("--prj", required=True)
    ap.add_argument("--check", metavar="TKT", help="exit 0 if this ticket is startable, 1 if deps unmet, 2 if not found")
    ap.add_argument("--md", action="store_true", help="markdown table output")
    args = ap.parse_args()

    hp = _handoffs_path(args.prj)
    if not hp.exists():
        print(f"HANDOFFS.md not found for {args.prj}: {hp}", file=sys.stderr)
        return 2
    tickets = _parse(hp.read_text(encoding="utf-8", errors="replace"))

    if args.check:
        tid = args.check
        if tid not in tickets:
            print(f"{tid}: not found in HANDOFFS.md", file=sys.stderr)
            return 2
        unmet = _unmet(tid, tickets)
        if unmet:
            print(f"{tid}: BLOCKED — deps not done: {', '.join(unmet)}")
            return 1
        print(f"{tid}: startable — all deps done")
        return 0

    # candidates = not terminal; split into unblocked frontier vs blocked
    frontier, blocked = [], []
    for tid, t in tickets.items():
        if _status(t) in TERMINAL_STATES:
            continue
        unmet = _unmet(tid, tickets)
        (blocked if unmet else frontier).append((tid, t, unmet))

    def _g(row):  # sort by gate then id for stable, gate-ordered output
        g = row[1].get("gate") or "99"
        return (int(g) if g.isdigit() else 99, row[0])

    frontier.sort(key=_g)
    blocked.sort(key=_g)

    if args.md:
        print(f"# unblocked frontier — {args.prj}  ({len(frontier)} startable · {len(blocked)} blocked)\n")
        print("| ticket | gate | status | deps |")
        print("|---|---|---|---|")
        for tid, t, _u in frontier:
            print(f"| {tid} | {t.get('gate') or '-'} | {_status(t) or 'open'} | ✅ clear |")
        for tid, t, u in blocked:
            print(f"| {tid} | {t.get('gate') or '-'} | {_status(t) or 'open'} | ⛔ {', '.join(u)} |")
        return 0

    if not frontier and not blocked:
        print(f"{args.prj}: no open tickets (queue empty or all terminal).")
        return 0
    print(f"UNBLOCKED FRONTIER — {args.prj}  ({len(frontier)} startable now):")
    for tid, t, _u in frontier:
        print(f"  ▶ {tid}  (gate {t.get('gate') or '-'} · {_status(t) or 'open'})")
    if not frontier:
        print("  (none — every open ticket is blocked on a dependency)")
    if blocked:
        print(f"\nBLOCKED ({len(blocked)}):")
        for tid, t, u in blocked:
            print(f"  ⛔ {tid}  (gate {t.get('gate') or '-'}) → waiting on: {', '.join(u)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
