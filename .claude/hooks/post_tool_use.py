#!/usr/bin/env python3
"""SOFI AI — PostToolUse hook (Edit|Write): checkpoint-discipline reminder.

The doctrine: "Uncommitted session = invisible to the next one." When the
working tree accumulates a threshold of uncommitted changes, nudge (once per
threshold band) to run `sofi checkpoint`. Advisory only — never blocks, never
spams: dedupes by counting bands of THRESHOLD changes and only firing when a
new band is crossed (so a commit that shrinks the tree silently re-arms it).

Also captures a memdb observation + a telemetry event for this Edit/Write
(best-effort, fail-OPEN — v6.1 wiring: memdb.capture + telemetry.send_event).

Fails OPEN: any error → emit nothing, exit 0.
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from _common import project_root, find_active_project
except Exception:
    sys.exit(0)

THRESHOLD = 12  # uncommitted changed files per reminder band


def _record_memory(root: Path, prj, tool_name: str, file_path: str) -> None:
    """Best-effort: capture this edit as a memdb observation + emit a
    telemetry event. Never raises, never blocks — swallow everything."""
    try:
        sys.path.insert(0, str(root / "company" / "os"))
        from sofi_tools import memdb, telemetry
        now_ts = datetime.now(timezone.utc).isoformat()
        pid = prj.name if prj else ""
        summary = f"{tool_name or 'edit'}: {file_path}" if file_path else (tool_name or "edit")
        memdb.capture(
            source="post_tool_use", kind="edit", summary=summary[:240],
            body="", ts=now_ts, project=pid,
        )
        telemetry.send_event(
            {"source": "post_tool_use", "kind": "edit", "agent": tool_name, "prj": pid},
            now_ts=now_ts,
        )
    except Exception:
        pass


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


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    try:
        root = project_root()
        prj = find_active_project(root)

        tool_name = data.get("tool_name", "") or ""
        tool_input = data.get("tool_input", {}) or {}
        file_path = tool_input.get("file_path", tool_input.get("filePath", "")) or ""
        _record_memory(root, prj, tool_name, file_path)

        count = uncommitted(root)
        if count < 0:
            sys.exit(0)
        band = count // THRESHOLD

        tracker = root / ".claude" / "memory" / "edit-tracker.json"
        last = 0
        try:
            last = int(json.loads(tracker.read_text()).get("band", 0))
        except Exception:
            last = 0

        if band != last:
            try:
                tracker.parent.mkdir(parents=True, exist_ok=True)
                tracker.write_text(json.dumps({"band": band, "count": count}))
            except Exception:
                pass

        # Only nudge when crossing UP into a new, non-zero band.
        if band > last and band >= 1:
            pid = prj.name if prj else "<PRJ>"
            msg = (
                f"⛏️ {count} uncommitted changes in the tree. Doctrine: checkpoint "
                f"early/often — uncommitted work is invisible to the next session. "
                f"Run `sofi checkpoint {pid} \"<type>(<scope>): <subject>\"` (or /sofi-handoff) "
                f"at the next natural milestone."
            )
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": msg,
                }
            }))
    except Exception:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
