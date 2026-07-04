#!/usr/bin/env python3
"""
reflection_engine — SOFI v5 "dreaming": distil the brain's episodic history into
durable procedural lessons.

role:    ceo-sofi (runs the reflection loop; specialists never self-reflect mid-task)
purpose: mechanically LOCATE learning signals in a project's HANDOFFS/DECISIONS
         history (0 model tokens), dedup them against lessons already recorded, and
         emit a structured digest the model distils into short lessons — then WRITE
         the distilled lessons back to _context/LESSONS.md (procedural memory).
gate:    all (cadence: run at gate-close or on demand — NEVER per-turn)

Why this shape (grounded in .claude/docs/ai-guides/research/self-improving-reflection.md):
  - Reflexion (arXiv:2303.11366): learn by writing a short natural-language lesson
    to an episodic buffer, not by re-reading the raw transcript. Lessons compound;
    logs don't.
  - arXiv:2605.12978: continuous per-turn memory updates measurably DEGRADE memory.
    So reflection is scheduled + retain-by-default: this tool only surfaces signals
    NOT already distilled (dedup by signature), and never rewrites existing lessons.
  - Python does the locating/dedup (cheap, deterministic); the model does only the
    judgment (distil situation+failure -> rule). "few token do trick."

CLI:
  reflection_engine.py scan  --prj PRJ-XXXX [--since N]
      -> prints a markdown digest of NEW learning candidates (not yet in LESSONS.md)
  reflection_engine.py write --prj PRJ-XXXX --sig SIG --situation S --failed F --rule R
                             [--source SRC] [--date YYYY-MM-DD] [--mem procedural]
      -> appends one distilled lesson to LESSONS.md (idempotent on --sig)

exit: 0 ok · 2 usage/no-project
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
from collections import Counter

_p = pathlib.Path(__file__).resolve()
for _up in _p.parents:
    if (_up / "sofi_tools").is_dir():
        sys.path.insert(0, str(_up))
        break
from sofi_tools import paths, tickets  # noqa: E402

# Signals that a ticket carried a learning-worthy outcome.
_BLOCKED = re.compile(r"block|escalat|reject", re.I)
_CIRCUIT = re.compile(r"circuit.?break|escalation_required|4th (failure|attempt)", re.I)


def _sig(*parts: str) -> str:
    """A short, stable dedup signature for a candidate lesson. Two candidates with
    the same (kind, subject) produce the same sig, so a lesson already distilled is
    never re-surfaced (retain-by-default)."""
    raw = "·".join(p.strip().lower() for p in parts if p)
    return re.sub(r"\s+", "-", raw)[:80]


def scan(prj: str, since: int | None = None) -> list[dict]:
    """Locate NEW learning candidates in the ticket history. Returns a list of
    {sig, kind, subject, evidence} dicts, excluding any sig already in LESSONS.md."""
    known = tickets.lesson_signatures(prj)
    tkts = tickets.parse(prj)
    if since:
        tkts = tkts[-since:]
    candidates: list[dict] = []

    # 1) Every escalation / blocked / rejected ticket is a candidate lesson: something
    #    upstream was wrong, ambiguous, or under-specified. The distilled rule should
    #    prevent the next occurrence.
    for t in tkts:
        blob = f"{t.status} {t.task} {' '.join(t.extra.values())}"
        if _BLOCKED.search(blob):
            kind = "circuit-breaker" if _CIRCUIT.search(blob) else "escalation"
            subject = (t.to or t.field("type") or "unknown").strip()
            sig = _sig(kind, subject, t.id)
            if sig not in known:
                candidates.append({
                    "sig": sig, "kind": kind, "subject": subject,
                    "evidence": f"{t.id} (gate {t.gate}) {t.frm}→{t.to}: "
                                f"{t.task[:70]} [status: {t.status[:40]}]",
                })

    # 2) Repeated ticket TYPE against the same target = a recurring friction area
    #    worth a durable pattern/procedure (Memp build->retrieve->update).
    by_target = Counter((t.to.strip(), t.field("type").strip())
                        for t in tkts if t.to and t.field("type"))
    for (target, ttype), n in by_target.items():
        if n >= 3:
            sig = _sig("recurring", ttype, target)
            if sig not in known:
                candidates.append({
                    "sig": sig, "kind": "recurring-pattern",
                    "subject": f"{ttype}→{target}",
                    "evidence": f"{n} '{ttype}' tickets routed to {target} — candidate "
                                f"for a reusable template/checklist (extract-to-template).",
                })
    return candidates


def cmd_scan(a) -> int:
    if not paths.project_dir(a.prj).exists():
        print(f"no such project: {a.prj}", file=sys.stderr)
        return 2
    cands = scan(a.prj, since=a.since)
    print(f"# Reflection digest — {a.prj} ({len(cands)} new candidate(s))")
    print("> Cadence: gate-close or on demand, never per-turn. Retain-by-default: "
          "only candidates NOT already in LESSONS.md are shown.\n")
    if not cands:
        print("_No new learning signals. The brain has already distilled what it saw._")
        return 0
    print("Distil each into ONE short lesson (situation · what-failed · rule), then "
          "`reflection_engine.py write` it. Ground the rule (G1): cite the ticket.\n")
    for c in cands:
        print(f"- **[{c['kind']}]** `{c['sig']}`")
        print(f"  - subject: {c['subject']}")
        print(f"  - evidence: {c['evidence']}")
    return 0


def cmd_write(a) -> int:
    if not paths.project_dir(a.prj).exists():
        print(f"no such project: {a.prj}", file=sys.stderr)
        return 2
    if a.sig.lower() in tickets.lesson_signatures(a.prj):
        print(f"lesson for sig '{a.sig}' already exists — skipping (retain-by-default).")
        return 0
    les_id = tickets.append_lesson(
        a.prj, situation=a.situation, what_failed=a.failed, rule=a.rule,
        sig=a.sig, mem=a.mem, source=a.source, date=a.date or "")
    print(f"wrote {les_id} to {paths.brain_file(a.prj, 'LESSONS')}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="reflection_engine",
                                 description="SOFI v5 reflection/dreaming engine")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scan", help="locate NEW learning candidates (0 model tokens)")
    s.add_argument("--prj", required=True)
    s.add_argument("--since", type=int, default=None,
                   help="only the last N tickets (default: all)")
    s.set_defaults(fn=cmd_scan)

    w = sub.add_parser("write", help="append one distilled lesson to LESSONS.md")
    w.add_argument("--prj", required=True)
    w.add_argument("--sig", required=True, help="dedup signature from the scan digest")
    w.add_argument("--situation", required=True)
    w.add_argument("--failed", required=True, help="what went wrong")
    w.add_argument("--rule", required=True, help="the durable rule to prevent recurrence")
    w.add_argument("--source", default="", help="ticket/decision this came from (G1 cite)")
    w.add_argument("--date", default="", help="YYYY-MM-DD (from caller, never invented)")
    w.add_argument("--mem", default="procedural")
    w.set_defaults(fn=cmd_write)

    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
