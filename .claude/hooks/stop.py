#!/usr/bin/env python3
"""SOFI AI — Stop hook: capture a lightweight session-end memory entry.

Appends one row to .claude/memory/sessions.jsonl recording when a response
turn ended, which project was active, the git HEAD, and whether the tree had
uncommitted work (a "your session may be invisible to the next one" signal).
Complements claude-mem's richer observation capture — this is the durable,
plugin-independent breadcrumb the doctrine relies on.

Also (v6.1, best-effort, fail-OPEN): folds this session's memdb observations
into one summary row (memdb.compress_session), and — ONLY when a project is
active and transitions.gate_proof_required says it is sitting at a gate
boundary — surfaces a graduated (soft→strong) reminder to record gate
evidence. Never sets a "decision" field, so it can never block Stop; severity
is capped (a hard deadlock cap) so a stuck project can't escalate forever.

Never hard-blocks: always exits 0 (an emitted context note is advisory only;
a non-empty *blocking* Stop response is what could loop, and this hook never
emits one).
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

_REMINDER_CAP = 5  # hard deadlock cap — severity never escalates past this


def _reminder_path(root: Path) -> Path:
    return root / ".claude" / "memory" / "gate_reminders.json"


def _reminder_counts(root: Path) -> dict:
    try:
        return json.loads(_reminder_path(root).read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_reminder_counts(root: Path, data: dict) -> None:
    try:
        p = _reminder_path(root)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data), encoding="utf-8")
    except Exception:
        pass


def _gate_reminder(root: Path, prj) -> str:
    """Project-scoped, graduated, capped gate-evidence reminder. Returns an
    advisory message string, or '' when nothing applies. NEVER emits a
    'decision' field — purely informational context, never a block."""
    if prj is None:
        return ""
    pid = prj.name
    try:
        sys.path.insert(0, str(root / "company" / "os"))
        from sofi_tools import transitions
        required = transitions.gate_proof_required(pid)
    except Exception:
        return ""

    counts = _reminder_counts(root)
    if not required:
        if counts.get(pid):
            counts[pid] = 0
            _write_reminder_counts(root, counts)
        return ""

    n = min(int(counts.get(pid, 0)) + 1, _REMINDER_CAP)
    counts[pid] = n
    _write_reminder_counts(root, counts)

    if n <= 1:
        return (f"note: {pid} is sitting at a gate boundary — remember to paste "
                f"gate evidence (`sofi gate-check {pid}`) before advancing.")
    if n <= 3:
        return (f"reminder ({n}/{_REMINDER_CAP}): {pid} still needs gate evidence "
                f"recorded before this gate can close.")
    return (f"STRONG reminder ({n}/{_REMINDER_CAP}, capped): {pid} has sat at a gate "
            f"boundary across {n} sessions with no recorded evidence — run "
            f"`sofi gate-check {pid}` and paste proof. (advisory only — never blocks Stop)")


def _compress_session(root: Path, session_id: str, ts: str) -> None:
    """Best-effort: fold this session's memdb observations into one summary
    row. Never raises."""
    if not session_id:
        return
    try:
        sys.path.insert(0, str(root / "company" / "os"))
        from sofi_tools import memdb
        memdb.compress_session(session_id, ts=ts)
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

        _compress_session(root, data.get("session_id") or "", entry["ts"])

        msg = _gate_reminder(root, prj)
        if msg:
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "Stop",
                    "additionalContext": msg,
                }
            }))
    except Exception:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
