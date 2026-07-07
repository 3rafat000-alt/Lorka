#!/usr/bin/env python3
"""
project_reader — SOFI v5 dashboard: read a project's REAL brain and surface what the
team is actually doing, in the messy real format (not just rigid TKT blocks).

Real SOFI projects log work as:
  - STATE.md          rich `key: value` log; keys like `phaseN_task_status:` /
                      `*_2026-07-02:` carry full narratives with agent slugs, 7-hex
                      commits, ✅/⚠/🔴 outcome markers.
  - HANDOFFS.md       freeform: `## TKT-NNN` blocks AND markdown dispatch tables
                      (| Task | Agent | ... |) AND `Blocker #N (...): <commit> ✅`.
  - reports/*.md      per-run audit/security/feature reports (mtime = recent activity).

This module parses all of that into structured, grounded records so the Observatory
and Task Manager tabs show the team really working — listening, reacting, in context.
It fabricates nothing (grounding C1): every record cites the file/line it came from.
"""
from __future__ import annotations

import pathlib
import re
import sys

_HERE = pathlib.Path(__file__).resolve().parent
_ROOT = _HERE.parent
sys.path.insert(0, str(_ROOT / "company" / "os"))
try:
    from sofi_tools import paths, tickets, gates, brain, registry as sregistry
    _OK = True
except Exception as e:
    print(f"[project_reader] sofi_tools import failed: {e}", file=sys.stderr)
    _OK = False

# The 105 real agent ids (for agent detection in freeform prose) — registry-driven.
ROLE_SLUGS = set()
if _OK:
    try:
        ROLE_SLUGS = set(sregistry.agents())
    except Exception:
        ROLE_SLUGS = set()
# Also match the historical sofi-<slug> agent form and legacy names.
_AGENT_RE = re.compile(r"sofi-([a-z][a-z0-9-]+)|(?<![a-z-])(" +
                       "|".join(sorted((ROLE_SLUGS or {"ceo-sofi"}), key=len, reverse=True)) +
                       r")(?![a-z-])")
_COMMIT_RE = re.compile(r"\b([0-9a-f]{7,40})\b")
_DATE_RE = re.compile(r"(20\d\d-\d\d-\d\d)")
_DONE_RE = re.compile(r"✅|CLOSED|DONE|complete|passed|green|SHIPPED|FIXED|RESOLVED|FINISHED", re.I)
_WARN_RE = re.compile(r"⚠|🟡|FAIL|blocked|BLOCKER|open\b|🔴|🟠|DENIED", re.I)


def _brain(prj: str, name: str) -> pathlib.Path:
    return paths.context_dir(prj) / f"{name}.md"


def _agents_in(text: str) -> list[str]:
    out = []
    for m in _AGENT_RE.finditer(text):
        slug = m.group(1) or m.group(2)
        if slug and slug not in out:
            out.append(slug)
    return out


def _marker(text: str) -> str:
    if _WARN_RE.search(text) and not _DONE_RE.search(text):
        return "warn"
    if _DONE_RE.search(text):
        return "done"
    if _WARN_RE.search(text):
        return "warn"
    return "info"


def state_worklog(prj: str, limit: int = 40) -> list[dict]:
    """Every meaningful STATE.md status/phase entry as a work record."""
    f = _brain(prj, "STATE")
    if not f.exists():
        return []
    out = []
    for i, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        s = line.strip()
        if ":" not in s or s.startswith("#"):
            continue
        key, _, val = s.partition(":")
        key = key.strip()
        # keep entries that read like logged work, not plain config keys
        if not re.search(r"status|phase|blocker|_20\d\d|hardened|done|fix|task|closed|review",
                         key, re.I):
            continue
        if len(val.strip()) < 12:
            continue
        agents = _agents_in(val)
        commit = (_COMMIT_RE.search(val) or [None, None])[1] if _COMMIT_RE.search(val) else None
        date = (_DATE_RE.search(val) or _DATE_RE.search(key))
        out.append({
            "key": key, "line": i, "marker": _marker(val),
            "agents": agents[:4], "commit": commit,
            "date": date.group(1) if date else None,
            "summary": val.strip()[:280], "source": f"STATE.md:{i}",
        })
    # newest dates first, undated keep original order at end
    out.sort(key=lambda r: (r["date"] or "0000-00-00"), reverse=True)
    return out[:limit]


def handoff_tasks(prj: str) -> list[dict]:
    """Tasks from HANDOFFS.md in ALL real formats: TKT blocks + dispatch tables +
    Blocker/✅ entries."""
    out = []
    # 1) rigid TKT blocks (if any)
    try:
        for t in tickets.parse(prj):
            out.append({"title": t.task[:90] or t.id, "agent": t.to or t.frm,
                        "gate": t.gate, "status": t.status or "open",
                        "marker": "done" if t.is_done else ("warn" if re.search(r"block|escalat", t.status, re.I) else "open"),
                        "type": t.field("type"), "id": t.id, "source": "HANDOFFS.md (TKT)"})
    except Exception:
        pass
    f = _brain(prj, "HANDOFFS")
    if not f.exists():
        return out
    lines = f.read_text(encoding="utf-8", errors="ignore").splitlines()
    # 2) markdown dispatch tables that have an "Agent" column
    for i, line in enumerate(lines):
        if "|" in line and re.search(r"\bagent\b", line, re.I) and re.search(r"task|scope|priority", line, re.I):
            cols = [c.strip().lower() for c in line.strip().strip("|").split("|")]
            try:
                ai = next(j for j, c in enumerate(cols) if "agent" in c)
                ti = next(j for j, c in enumerate(cols) if "task" in c or "scope" in c)
            except StopIteration:
                continue
            j = i + 1
            if j < len(lines) and set(lines[j].strip()) <= set("|-: "):
                j += 1  # skip separator row
            while j < len(lines) and lines[j].strip().startswith("|"):
                cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                if len(cells) > max(ai, ti) and cells[ti]:
                    ag = cells[ai] if len(cells) > ai else ""
                    ag = (_agents_in(ag) or [ag])[0]
                    out.append({"title": cells[ti][:90], "agent": ag, "gate": "",
                                "status": "queued", "marker": "open", "type": "dispatch",
                                "source": f"HANDOFFS.md:{j+1} (dispatch table)"})
                j += 1
    # 3) narrative ticket blocks — the format real projects actually use:
    #    "## PRIOR TICKET (2026-07-02, head 81e7e1f) — Permission banners SHIPPED."
    hdrs = []
    for i, line in enumerate(lines):
        m = re.match(r"^#{2,3}\s+(PRIOR|NEXT|OPEN|CURRENT)\s+TICKET\b(.*)$",
                     line.strip(), re.I)
        if m:
            hdrs.append((i, m.group(1).upper(), m.group(2)))
    for n, (i, kind, rest) in enumerate(hdrs):
        end = hdrs[n + 1][0] if n + 1 < len(hdrs) else len(lines)
        body = "\n".join(lines[i:end])
        parts = re.split(r"\s[—–-]\s", rest, 1)
        title = (parts[1] if len(parts) > 1 else parts[0]).strip(" -—:()*")
        if not title:  # bare "## Next ticket" header — first body line is the title
            title = next((l.strip().strip("*") for l in lines[i + 1:end]
                          if l.strip() and not l.strip().startswith("#")), "")
        date = _DATE_RE.search(rest)
        commit = _COMMIT_RE.search(rest)
        mk = _marker(title or body)
        if kind in ("NEXT", "OPEN", "CURRENT") and mk == "info":
            mk = "open"
        out.append({"title": (title or f"{kind} ticket")[:90],
                    "agent": (_agents_in(body) or [""])[0], "gate": "",
                    "status": {"done": "done", "warn": "blocked"}.get(mk, "open"),
                    "marker": mk, "type": kind.lower() + "-ticket",
                    "date": date.group(1) if date else None,
                    "commit": commit.group(1) if commit else None,
                    "source": f"HANDOFFS.md:{i+1}"})
    # 4) "## Backlog" bullet items → queued tasks
    in_bl = False
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if re.match(r"^#{2,3}\s+Backlog\b", s, re.I):
            in_bl = True
            continue
        if in_bl:
            if s.startswith("#"):
                in_bl = False
                continue
            m = re.match(r"^[-*]\s+(.+)$", s)
            if m:
                out.append({"title": m.group(1).strip()[:90],
                            "agent": (_agents_in(s) or [""])[0], "gate": "",
                            "status": "queued", "marker": "open", "type": "backlog",
                            "source": f"HANDOFFS.md:{i}"})
    # 5) Blocker / Task entries with an outcome marker
    for i, line in enumerate(lines, 1):
        m = re.match(r"\s*(?:\*\*)?(Blocker\s*#?\d+|Task\s*[\d.]+)[^:]*[:)]", line)
        if m and (_DONE_RE.search(line) or _WARN_RE.search(line)):
            ag = (_agents_in(line) or [""])[0]
            out.append({"title": line.strip().strip("*")[:90], "agent": ag, "gate": "",
                        "status": "done" if _DONE_RE.search(line) else "blocked",
                        "marker": "done" if _DONE_RE.search(line) else "warn",
                        "type": "blocker", "source": f"HANDOFFS.md:{i}"})
    return out


def recent_reports(prj: str, limit: int = 12) -> list[dict]:
    d = paths.context_dir(prj) / "reports"
    if not d.exists():
        return []
    rs = []
    for p in d.iterdir():
        if p.is_file() and p.suffix in (".md", ".json"):
            try:
                mt = p.stat().st_mtime
            except Exception:
                mt = 0
            rs.append({"name": p.name, "mtime": mt,
                       "kind": p.name.split("-")[0] if "-" in p.name else p.stem})
    rs.sort(key=lambda r: r["mtime"], reverse=True)
    return rs[:limit]


def team_pulse(prj: str) -> dict:
    """A grounded snapshot of what the team is doing — for the Observatory header."""
    st = brain.read_state(prj) if _OK else {}
    wl = state_worklog(prj, 60)
    tasks = handoff_tasks(prj)
    active_agents = []
    for r in wl:
        for a in r["agents"]:
            if a not in active_agents:
                active_agents.append(a)
    readiness = None
    for k, v in st.items():
        m = re.search(r"(\d{2,3})\s*%", str(v))
        if m and re.search(r"readiness|score", k + str(v), re.I):
            readiness = int(m.group(1)); break
    done = sum(1 for t in tasks if t["marker"] == "done")
    return {
        "gate": st.get("gate", "—"),
        "status": st.get("status", ""),
        "branch": st.get("branch", ""),
        "head_sha": st.get("head_sha", ""),
        "blockers": st.get("blockers", ""),
        "readiness": readiness,
        "active_agents": active_agents[:12],
        "worklog_count": len(wl),
        "task_total": len(tasks), "task_done": done,
        "reports": len(recent_reports(prj, 999)),
    }


def observatory(prj: str) -> dict:
    """Everything the Live Observatory tab needs, from the real brain."""
    if not _OK:
        return {"error": "sofi_tools unavailable"}
    try:
        g = {"no_skip": gates.validate_no_skip(prj), "artifacts": gates.validate_artifacts(prj),
             "room_boundary": gates.validate_room_boundary(prj), "evidence": gates.validate_evidence(prj)}
    except Exception as e:
        g = {"error": str(e)}
    return {"pulse": team_pulse(prj), "worklog": state_worklog(prj, 40),
            "reports": recent_reports(prj, 12), "gates": g}


if __name__ == "__main__":
    import argparse, json
    ap = argparse.ArgumentParser()
    ap.add_argument("--prj", required=True)
    ap.add_argument("--what", default="pulse", choices=["pulse", "worklog", "tasks", "reports", "observatory"])
    a = ap.parse_args()
    fn = {"pulse": team_pulse, "worklog": state_worklog, "tasks": handoff_tasks,
          "reports": recent_reports, "observatory": observatory}[a.what]
    print(json.dumps(fn(a.prj), ensure_ascii=False, indent=2))
