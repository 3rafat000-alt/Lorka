#!/usr/bin/env python3
"""SOFI AI — UserPromptSubmit hook: surface a matching lesson before work starts.

Best-effort topical match against the memory db (memdb.learn_match) and the
managed lessons cache (lessons_cache.vaccine_for) for the active project, so a
known failure pattern surfaces as additionalContext BEFORE the agent acts on
this prompt — the "vaccine" half of reflection.md (v5) / v6.1 wiring. Also
captures a [LEARN] observation when the prompt itself looks like a correction
("no, that's wrong", "actually...", "correction:", ...) — a free training
signal for the reflection loop to distil later.

Fails OPEN: any error → emit nothing, exit 0. Never blocks the prompt (no
'decision' field is ever emitted).
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from _common import project_root, find_active_project
except Exception:
    sys.exit(0)

# Cheap, deterministic "this prompt is correcting the agent" signal — not a
# model call, just a signature match (mirrors sofi_tools.acceptance's style).
_CORRECTION_RE = re.compile(
    r"(?i)\b("
    r"no,?\s+that'?s\s+(?:not|wrong)|"
    r"actually,|"
    r"that'?s\s+not\s+(?:right|correct|what\s+i)|"
    r"you\s+(?:misunderstood|got\s+it\s+wrong)|"
    r"correction:|"
    r"undo\s+that|"
    r"revert\s+that|"
    r"i\s+meant\b"
    r")\b"
)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    try:
        prompt = (data.get("prompt") or "").strip()
        if not prompt:
            sys.exit(0)

        root = project_root()
        sys.path.insert(0, str(root / "company" / "os"))
        from sofi_tools import memdb, lessons_cache

        prj = find_active_project(root)
        pid = prj.name if prj else ""
        now_ts = datetime.now(timezone.utc).isoformat()

        lines: list[str] = []
        try:
            hits = memdb.learn_match(prompt, k=3)
        except Exception:
            hits = []
        for h in hits[:2]:
            lines.append(f"- memory: [{h.get('type', '')}] {h.get('summary', '')[:160]}")

        if pid:
            try:
                vaccine = lessons_cache.vaccine_for(pid, prompt, cap=2)
            except Exception:
                vaccine = []
            for v in vaccine:
                lines.append(f"- lesson [{v.get('scope', '')}] {v.get('sig', '')}: "
                             f"{v.get('rule', '')[:160]}")

        if _CORRECTION_RE.search(prompt):
            try:
                memdb.capture(
                    source="user_prompt_submit", kind="[LEARN]",
                    summary=f"user correction: {prompt[:160]}",
                    body=prompt[:2000], ts=now_ts, project=pid,
                )
            except Exception:
                pass

        if lines:
            context = "## SOFI memory match (auto)\n" + "\n".join(lines)
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": context,
                }
            }))
    except Exception:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
