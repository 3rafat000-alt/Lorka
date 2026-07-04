#!/usr/bin/env python3
"""SOFI AI — Stop hook: capture a lightweight session-end memory entry.

Appends one row to .claude/memory/sessions.jsonl recording when a response
turn ended, which project was active, the git HEAD, and whether the tree had
uncommitted work (a "your session may be invisible to the next one" signal).
Complements claude-mem's richer observation capture — this is the durable,
plugin-independent breadcrumb the doctrine relies on.

Never blocks: always exits 0 with no stdout (a non-empty Stop block could loop).
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from _common import project_root, find_active_project, read_state
except Exception:
    sys.exit(0)


def uncommitted(root: Path) -> int:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain"],
            capture_output=True, text=True, timeout=4,
        )
        if out.returncode == 0:
            return len([l for l in out.stdout.splitlines() if l.strip()])
    except Exception:
        pass
    return -1


def git_head(root: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=4,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except Exception:
        pass
    return ""


def main() -> None:
    try:
        try:
            data = json.load(sys.stdin)
        except Exception:
            data = {}
        root = project_root()
        prj = find_active_project(root)
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": "session.stop",
            "project": prj.name if prj else None,
            "head": git_head(root),
            "uncommitted": uncommitted(root),
            "session_id": data.get("session_id"),
        }
        if prj is not None:
            st = read_state(prj / "_context" / "STATE.md")
            entry["gate"] = st.get("gate")
            entry["active_agent"] = st.get("active")
        log = root / ".claude" / "memory" / "sessions.jsonl"
        log.parent.mkdir(parents=True, exist_ok=True)
        with open(log, "a", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")
    except Exception:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
