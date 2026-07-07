#!/usr/bin/env python3
"""SOFI AI — SessionStart hook: orient, never start blind.

Injects the active project's live brain (STATE.md head + next handoff ticket)
as additionalContext at the top of every session, enforcing the universal
contract from CLAUDE.md: `sofi sync` → read STATE.md (branch + head_sha) →
your ticket in HANDOFFS.md.

Also appends a token-bounded memory digest (memdb.inject_digest — v6.1) when
an active project exists: latest STATE head + next ticket + recent
observations, so the session opens with more than just the brain files.

Fails OPEN: any error → emit nothing, exit 0.
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from _common import project_root, find_active_project, read_state, next_ticket
except Exception:
    sys.exit(0)


def _memory_digest(root: Path, pid: str) -> str:
    """Best-effort SessionStart digest via memdb.inject_digest. Returns '' on
    any failure (unavailable module, unreadable db, ...) — never raises."""
    try:
        sys.path.insert(0, str(root / "company" / "os"))
        from sofi_tools import memdb
        now_ts = datetime.now(timezone.utc).isoformat()
        return memdb.inject_digest(pid, token_budget=1000, now_ts=now_ts)
    except Exception:
        return ""


def git_head(root: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "log", "-1", "--format=%h %s"],
            capture_output=True, text=True, timeout=4,
        )
        if out.returncode == 0:
            return out.stdout.strip()[:120]
    except Exception:
        pass
    return ""


def git_branch(root: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=4,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except Exception:
        pass
    return ""


def main() -> None:
    try:
        root = project_root()
        prj = find_active_project(root)
        lines = ["## SOFI orientation (auto — no blind start)"]
        branch = git_branch(root)
        head = git_head(root)
        if branch:
            lines.append(f"- **branch:** `{branch}`" + (f" · **HEAD:** {head}" if head else ""))

        if prj is not None:
            ctx = prj / "_context"
            state = read_state(ctx / "STATE.md")
            pid = prj.name
            title = state.get("title", pid)
            lines.append(f"- **active project:** `{pid}` — {title}")
            bits = []
            for k in ("gate", "active", "local_domain", "status", "blockers"):
                if state.get(k):
                    bits.append(f"{k}: {state[k]}")
            if bits:
                lines.append("- **state:** " + " · ".join(b[:160] for b in bits))
            tk = next_ticket(ctx / "HANDOFFS.md")
            if tk:
                lines.append(f"- **next ticket (HANDOFFS):** {tk}")
            lines.append(
                "- **contract:** read STATE/CONTEXT/HANDOFFS before acting · "
                "checkpoint every milestone · record `head_sha` on handoff.\n"
                "- **palette** (`company/constitution/00-operating-system.md`): spine "
                "`/sofi-boot` `/sofi-team` `/sofi-delegate` `/sofi-gate` `/sofi-handoff` · "
                "power tools `/sofi-audit <layer>` `/sofi-spec-review \"<feature>\"` "
                "`/sofi-feature \"<feature>\"` (big one — full loop) "
                "`/sofi-secure <mode>` `/sofi-fix <target>` "
                "`/sofi-report <kind>` `/sofi-design-taste`. Loop: "
                "boot → audit/secure → fix → report → gate → handoff."
            )
            digest = _memory_digest(root, pid)
            if digest:
                lines.append("\n" + digest)
        else:
            lines.append(
                "- no active project brain found under `projects/*/_context/`. "
                "Scaffold one: `bash company/os/bin/new-project.sh PRJ-XXXX \"title\" PRIORITY <date>`."
            )

        context = "\n".join(lines)
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context,
            }
        }))
    except Exception:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
