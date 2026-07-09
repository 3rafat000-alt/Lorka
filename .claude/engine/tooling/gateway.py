#!/usr/bin/env python3
"""
gateway.py — SOFI Semantic Gateway / Input Refiner (the deterministic half).

A human types a raw / slangy request. An LLM "Translator" persona
(gateway/translator.prompt.md) turns that intent into ONE structured gateway
JSON payload. THIS tool ingests the structured payload, VALIDATES it (by
shelling out to the sibling validate.py) and ENQUEUES concrete tasks into the
task queue (by shelling out to the sibling taskq.py).

It is the deterministic bridge only — it performs NO NLP itself.

Rules of the house:
  * Python 3, standard library only. No pip, no third-party.
  * Sibling tools are shelled out to, never imported.
  * Every subcommand supports --json (exactly one JSON object to stdout).
  * Exit 0 = ok, 1 = logical failure (rejected / invalid), 2 = usage error.
  * A traceback never leaks to the user.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# --- locations -------------------------------------------------------------
# Sibling tools live next to this file; the prompt persona lives in gateway/.
SIB = Path(__file__).resolve().parent
PROMPT_PATH = SIB / "gateway" / "translator.prompt.md"


def paths():
    """Resolve ROOT / SOFI on demand (isolation-aware).

    Resolved per call — not at import — so that `selftest` (which runs children
    under a throw-away SOFI_HOME) never touches the real ROOT/.sofi.
    """
    root = Path(os.environ.get("SOFI_HOME") or Path(__file__).resolve().parents[3])
    sofi = root / ".sofi"
    sofi.mkdir(parents=True, exist_ok=True)
    return root, sofi


# --- routing tables --------------------------------------------------------
# sub_system -> default recipient agent (when an action has no explicit recipient)
SUBSYS_AGENT = {
    "BACKEND": "bck-api-engineer",
    "WEB_UI": "fnt-vue-engineer",
    "MOBILE_UI": "mob-flutter-engineer",
    "DATA": "dat-db-engineer",
    "SECURITY": "sec-appsec-engineer",
    "DEVOPS": "ops-cicd-engineer",
    "DOCS": "knw-doc-writer",
}

# sub_system -> taskq action enum (the delegation/taskq `action` field)
SUBSYS_ACTION = {
    "BACKEND": "UPDATE_SCHEMA",
    "WEB_UI": "GENERATE_UI_SCREEN",
    "MOBILE_UI": "GENERATE_UI_SCREEN",
    "DATA": "UPDATE_SCHEMA",
    "SECURITY": "REVIEW_DIFF",
    "DEVOPS": "RUN_CHECK",
    "DOCS": "GENERIC",
}

# --- canonical worked example (mirrors gateway/translator.prompt.md) --------
EXAMPLE_RAW = "ضبط لي صفحة البروفايل... خلي المستخدم يضيف رقم تليفونه ويتسيف بالـ DB"
EXAMPLE_PAYLOAD = {
    "instruction_type": "FEATURE",
    "priority": "NORMAL",
    "target_stacks": ["backend", "web"],
    "summary": "Let the user add a phone number on the profile page and persist it to the database.",
    "actions": [
        {
            "sub_system": "BACKEND",
            "task": (
                "Add a nullable phone_number column to the users table via a reversible "
                "migration, expose it on the profile-update endpoint, and validate it "
                "server-side (E.164 format, unique)."
            ),
            "recipient": "bck-api-engineer",
        },
        {
            "sub_system": "WEB_UI",
            "task": (
                "Add a phone-number field to the profile form (Vue 3), wire it into the "
                "profile store state, and submit it through the profile-update API."
            ),
            "recipient": "fnt-vue-engineer",
        },
    ],
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# --- subprocess plumbing ---------------------------------------------------
def _run(cmd):
    """Run a sibling tool.

    Returns (returncode, parsed_json_or_None, raw_stdout, stderr). A nonzero
    return code is a failure the caller must surface; stdout is still parsed so
    that a tool which emits JSON *and* exits 1 (e.g. a REJECT) is understood.
    """
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError as exc:
        return 127, None, "", "tool not found: {}".format(exc)
    except Exception as exc:  # pragma: no cover - defensive
        return 1, None, "", "failed to run tool: {}".format(exc)
    out = proc.stdout or ""
    try:
        parsed = json.loads(out)
    except Exception:
        parsed = None
    return proc.returncode, parsed, out, (proc.stderr or "")


def validate_payload(payload):
    """Shell out to sibling validate.py. Return (ok, errors)."""
    cmd = [
        sys.executable, str(SIB / "validate.py"), "gateway",
        "--payload", json.dumps(payload), "--json",
    ]
    rc, parsed, out, err = _run(cmd)
    if parsed is None:
        msg = err.strip() or out.strip() or "validator produced no JSON output"
        return False, ["validator error: {}".format(msg)]
    rejected = (
        rc != 0
        or parsed.get("ok") is False
        or parsed.get("valid") is False
        or str(parsed.get("verdict") or parsed.get("status") or "").upper() == "REJECT"
    )
    if rejected:
        errors = parsed.get("errors")
        if not errors:
            single = parsed.get("error")
            errors = [single] if single else ["payload rejected by validator"]
        if not isinstance(errors, list):
            errors = [str(errors)]
        return False, errors
    return True, []


def taskq_create(action_enum, recipient, task_payload):
    """Shell out to sibling taskq.py `create`. Return (task_id, error)."""
    cmd = [
        sys.executable, str(SIB / "taskq.py"), "create",
        "--action", action_enum, "--to", recipient,
        "--payload", json.dumps(task_payload), "--json",
    ]
    rc, parsed, out, err = _run(cmd)
    if rc != 0 or parsed is None:
        msg = err.strip() or out.strip() or "taskq produced no JSON output"
        return None, "taskq error: {}".format(msg)
    tid = parsed.get("task_id")
    if tid is None:
        tid = parsed.get("id")
    if tid is None and isinstance(parsed.get("task"), dict):
        tid = parsed["task"].get("id")
    if tid is None:
        return None, "taskq did not return a task id"
    return tid, None


def _extract_tasks(parsed):
    """Pull a task list out of whatever shape taskq.py list returns."""
    if parsed is None:
        return []
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict):
        for key in ("tasks", "items", "queue", "created"):
            value = parsed.get(key)
            if isinstance(value, list):
                return value
    return []


# --- output ----------------------------------------------------------------
def emit(args, obj, code):
    """Emit one result object as JSON, or a short human rendering. Return code."""
    if getattr(args, "json", False):
        print(json.dumps(obj, ensure_ascii=False))
        return code
    if obj.get("ok"):
        created = obj.get("created")
        if created is not None:
            print("OK — {} task(s) enqueued:".format(obj.get("count", len(created))))
            for c in created:
                print("  #{}  {:<9} -> {}".format(c["task_id"], c["sub_system"], c["assigned_to"]))
        else:
            print("OK")
    else:
        print("REJECTED at stage '{}':".format(obj.get("stage", "?")), file=sys.stderr)
        for e in obj.get("errors", []):
            print("  - {}".format(e), file=sys.stderr)
    return code


# --- subcommands -----------------------------------------------------------
def cmd_ingest(args):
    # 0) load the payload from --payload or --payload-file
    if args.payload_file:
        try:
            raw = Path(args.payload_file).read_text(encoding="utf-8")
        except Exception as exc:
            return emit(args, {"ok": False, "stage": "input",
                               "errors": ["cannot read payload-file: {}".format(exc)]}, 1)
    elif args.payload is not None:
        raw = args.payload
    else:
        return emit(args, {"ok": False, "stage": "input",
                           "errors": ["provide --payload or --payload-file"]}, 2)

    try:
        payload = json.loads(raw)
    except Exception as exc:
        return emit(args, {"ok": False, "stage": "input",
                           "errors": ["payload is not valid JSON: {}".format(exc)]}, 1)
    if not isinstance(payload, dict):
        return emit(args, {"ok": False, "stage": "input",
                           "errors": ["payload must be a JSON object"]}, 1)

    paths()  # ensure .sofi exists for this (real) invocation

    # 1) validate; on REJECT, enqueue nothing
    ok, errors = validate_payload(payload)
    if not ok:
        return emit(args, {"ok": False, "stage": "validate", "errors": errors}, 1)

    actions = payload.get("actions")
    if not isinstance(actions, list) or not actions:
        return emit(args, {"ok": False, "stage": "validate",
                           "errors": ["payload.actions must be a non-empty list"]}, 1)

    # 1b) pre-flight the routing map so a bad action never leaves a partial enqueue
    for i, action in enumerate(actions):
        if not isinstance(action, dict):
            return emit(args, {"ok": False, "stage": "map",
                               "errors": ["action[{}] is not an object".format(i)]}, 1)
        ss = action.get("sub_system")
        if ss not in SUBSYS_ACTION:
            return emit(args, {"ok": False, "stage": "map",
                               "errors": ["action[{}] has unknown sub_system: {!r}".format(i, ss)]}, 1)

    instruction_type = payload.get("instruction_type")
    priority = payload.get("priority")

    # 2) enqueue one task per action
    created = []
    for action in actions:
        ss = action["sub_system"]
        action_enum = SUBSYS_ACTION[ss]
        recipient = action.get("recipient") or SUBSYS_AGENT[ss]
        task_payload = dict(action)
        task_payload["instruction_type"] = instruction_type
        task_payload["priority"] = priority
        task_payload["enqueued_at"] = now_iso()
        tid, err = taskq_create(action_enum, recipient, task_payload)
        if err:
            return emit(args, {"ok": False, "stage": "taskq",
                               "errors": [err], "created": created}, 1)
        created.append({"task_id": tid, "assigned_to": recipient, "sub_system": ss})

    # 3) done
    return emit(args, {"ok": True, "created": created, "count": len(created)}, 0)


def cmd_prompt(args):
    if not PROMPT_PATH.exists():
        return emit(args, {"ok": False, "stage": "prompt",
                           "errors": ["missing prompt file: {}".format(PROMPT_PATH)]}, 1)
    content = PROMPT_PATH.read_text(encoding="utf-8")
    if args.json:
        print(json.dumps({"ok": True, "path": str(PROMPT_PATH), "content": content},
                         ensure_ascii=False))
    else:
        print(str(PROMPT_PATH))
        print()
        print(content)
    return 0


def cmd_example(args):
    obj = {"ok": True, "raw_input": EXAMPLE_RAW, "payload": EXAMPLE_PAYLOAD}
    if args.json:
        print(json.dumps(obj, ensure_ascii=False))
    else:
        print("RAW INPUT:")
        print("  " + EXAMPLE_RAW)
        print()
        print("GATEWAY PAYLOAD:")
        print(json.dumps(EXAMPLE_PAYLOAD, ensure_ascii=False, indent=2))
    return 0


def cmd_selftest(args):
    """Exercise ingest end-to-end against real siblings under a throw-away SOFI_HOME."""
    checks = []
    tmp = tempfile.mkdtemp(prefix="sofi-gw-selftest-")
    env_backup = os.environ.get("SOFI_HOME")
    os.environ["SOFI_HOME"] = tmp  # children inherit -> isolated queue, real .sofi untouched
    passed = True
    try:
        valid_payload = {
            "instruction_type": "FEATURE_EXPANSION",
            "priority": "MEDIUM",
            "target_stacks": ["backend", "web"],
            "summary": "selftest: add phone number to profile",
            "actions": [
                {"sub_system": "BACKEND", "task": "add phone_number migration + validation"},
                {"sub_system": "WEB_UI", "task": "add phone field to profile form"},
            ],
        }
        rc, parsed, out, _ = _run([sys.executable, str(SIB / "gateway.py"),
                                   "ingest", "--payload", json.dumps(valid_payload), "--json"])
        ok1 = rc == 0 and isinstance(parsed, dict) and parsed.get("ok") is True and parsed.get("count") == 2
        checks.append(("valid 2-action ingest creates 2 tasks", ok1, {"rc": rc, "out": parsed or out}))
        passed = passed and ok1

        rc2, parsed2, _, _ = _run([sys.executable, str(SIB / "taskq.py"), "list", "--json"])
        listed = _extract_tasks(parsed2)
        ok2 = rc2 == 0 and len(listed) == 2
        checks.append(("taskq list shows the 2 tasks", ok2, {"rc": rc2, "count": len(listed)}))
        passed = passed and ok2

        invalid_payload = {
            "instruction_type": "FEATURE_EXPANSION",
            "priority": "MEDIUM",
            "target_stacks": ["backend"],
            "summary": "selftest: invalid (no actions)",
            "actions": [],
        }
        rc3, parsed3, out3, _ = _run([sys.executable, str(SIB / "gateway.py"),
                                      "ingest", "--payload", json.dumps(invalid_payload), "--json"])
        ok3 = rc3 == 1 and isinstance(parsed3, dict) and parsed3.get("ok") is False
        checks.append(("invalid ingest is REJECTED (exit 1)", ok3, {"rc": rc3, "out": parsed3 or out3}))
        passed = passed and ok3

        rc4, parsed4, _, _ = _run([sys.executable, str(SIB / "taskq.py"), "list", "--json"])
        listed4 = _extract_tasks(parsed4)
        ok4 = rc4 == 0 and len(listed4) == 2
        checks.append(("nothing enqueued on reject (still 2)", ok4, {"rc": rc4, "count": len(listed4)}))
        passed = passed and ok4
    finally:
        if env_backup is None:
            os.environ.pop("SOFI_HOME", None)
        else:
            os.environ["SOFI_HOME"] = env_backup
        shutil.rmtree(tmp, ignore_errors=True)

    obj = {
        "ok": passed,
        "verdict": "PASS" if passed else "FAIL",
        "checks": [{"name": n, "pass": bool(p), "detail": d} for (n, p, d) in checks],
    }
    if args.json:
        print(json.dumps(obj, ensure_ascii=False))
    else:
        for n, p, _ in checks:
            print("[{}] {}".format("PASS" if p else "FAIL", n))
        print("PASS" if passed else "FAIL")
    return 0 if passed else 1


# --- CLI -------------------------------------------------------------------
def build_parser():
    parser = argparse.ArgumentParser(
        prog="gateway.py",
        description="SOFI Semantic Gateway / Input Refiner (deterministic half).",
    )
    sub = parser.add_subparsers(dest="command")

    p_ingest = sub.add_parser("ingest", help="validate a gateway payload and enqueue its actions")
    p_ingest.add_argument("--payload", help="the gateway JSON payload as a string")
    p_ingest.add_argument("--payload-file", dest="payload_file", help="path to a file holding the payload JSON")
    p_ingest.add_argument("--json", action="store_true", help="emit one JSON object to stdout")

    p_prompt = sub.add_parser("prompt", help="print the Translator persona system prompt")
    p_prompt.add_argument("--json", action="store_true")

    p_example = sub.add_parser("example", help="print a sample raw-input -> gateway-payload example")
    p_example.add_argument("--json", action="store_true")

    p_selftest = sub.add_parser("selftest", help="run an isolated end-to-end self-test")
    p_selftest.add_argument("--json", action="store_true")

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help(sys.stderr)
        return 2
    handlers = {
        "ingest": cmd_ingest,
        "prompt": cmd_prompt,
        "example": cmd_example,
        "selftest": cmd_selftest,
    }
    handler = handlers.get(args.command)
    if handler is None:
        parser.print_help(sys.stderr)
        return 2
    try:
        return handler(args)
    except SystemExit:
        raise
    except Exception as exc:  # never leak a traceback
        msg = "{}: {}".format(type(exc).__name__, exc)
        if getattr(args, "json", False):
            print(json.dumps({"ok": False, "stage": "internal", "errors": [msg]}, ensure_ascii=False))
        else:
            print("ERROR: " + msg, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
