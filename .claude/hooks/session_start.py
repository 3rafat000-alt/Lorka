#!/usr/bin/env python3
"""SOFI AI — SessionStart hook: orient, never start blind.

Injects the active project's live brain (STATE.md head + next handoff ticket)
as additionalContext at the top of every session, enforcing the universal
contract from CLAUDE.md: `sofi sync` → read STATE.md (branch + head_sha) →
your ticket in HANDOFFS.md.

Fails OPEN: any error → emit nothing, exit 0.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from _common import project_root, find_active_project, read_state, next_ticket
except Exception:
    sys.exit(0)


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
                "- **how the team works** (no slash-commands — direct & flexible, "
                "`engine/protocols/02-intake-orchestration.md`): the main session reformulates "
                "the ask, wears CEO → tier-advisor personas in sequence (researches the web), "
                "then spawns leaf specialists one hop deep, in parallel. Depth = new rounds, "
                "never nesting.\n"
                "- **Python tools it calls directly** (token-frugal substrate, "
                "`engine/tooling/`): `sofi sync|checkpoint|brain-query|gate-check|gemini|"
                "domain|tunnel` · `python3 engine/tooling/agents/ceo/sofi_scan.py <mode> "
                "\"<q>\" --prj <PRJ> --md` (0-token locate) · `sofi_verify.py` (verify gate). "
                "Loop: orient → scan → delegate → verify → checkpoint → next ticket."
            )
        else:
            lines.append(
                "- no active project brain found under `projects/*/_context/`. "
                "Scaffold one: `bash engine/bin/new-project.sh PRJ-XXXX \"title\" PRIORITY <date>`."
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
