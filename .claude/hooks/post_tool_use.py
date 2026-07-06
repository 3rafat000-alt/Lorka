#!/usr/bin/env python3
"""SOFI AI — PostToolUse hook (Edit|Write): checkpoint-discipline reminder.

The doctrine: "Uncommitted session = invisible to the next one." When the
working tree accumulates a threshold of uncommitted changes, nudge (once per
threshold band) to run `sofi checkpoint`. Advisory only — never blocks, never
spams: dedupes by counting bands of THRESHOLD changes and only firing when a
new band is crossed (so a commit that shrinks the tree silently re-arms it).

Fails OPEN: any error → emit nothing, exit 0.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from _common import project_root, find_active_project
except Exception:
    sys.exit(0)

THRESHOLD = 12  # uncommitted changed files per reminder band


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
        root = project_root()
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
            prj = find_active_project(root)
            pid = prj.name if prj else "<PRJ>"
            msg = (
                f"⛏️ {count} uncommitted changes in the tree. Doctrine: checkpoint "
                f"early/often — uncommitted work is invisible to the next session. "
                f"Run `sofi checkpoint {pid} \"<type>(<scope>): <subject>\"` "
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
