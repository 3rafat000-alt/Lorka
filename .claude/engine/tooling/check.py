#!/usr/bin/env python3
"""SOFI Self-Correction Runtime Runner.

Runs real stack linters/tests (Laravel / Web / Flutter) inside a configured app
directory and returns STRUCTURED results so an agent can self-heal BEFORE it
hands off. The actual app code is NOT in this repo, so this tool is
CONFIG-DRIVEN and DEGRADES GRACEFULLY: it never crashes when paths or tools are
absent -- it reports "unconfigured" / "tool_missing" instead.

Exit codes (per subcommand):
  0  all checks passed
  1  a check FAILED (ran, non-zero return, or timeout)
  2  misconfig (app path not configured, or a required tool is missing)

Every subcommand accepts --json and emits exactly ONE JSON object to stdout.
Stdlib only. No third-party dependencies.
"""

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# --- Roots -----------------------------------------------------------------
ROOT = Path(os.environ.get("SOFI_HOME") or Path(__file__).resolve().parents[3])
SOFI = ROOT / ".sofi"

# Convention: ensure ROOT/.sofi exists at setup. Skipped for `selftest`, which
# MUST NOT touch the real ROOT/.sofi -- it exercises the tool via child
# processes pointed at a tempfile SOFI_HOME instead.
_IS_SELFTEST = len(sys.argv) > 1 and sys.argv[1] == "selftest"
if not _IS_SELFTEST:
    try:
        SOFI.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

# --- Configuration ---------------------------------------------------------
DEFAULT_CONFIG = {"laravel_path": "", "web_path": "", "flutter_path": ""}

CFG_KEYS = {"laravel": "laravel_path", "web": "web_path", "flutter": "flutter_path"}
ENV_KEYS = {
    "laravel": "SAKK_LARAVEL_PATH",
    "web": "SAKK_WEB_PATH",
    "flutter": "SAKK_FLUTTER_PATH",
}

TIMEOUT = 300  # seconds per check
TAIL_LINES = 40

# Each check: name, command (shlex-split, never shell=True), and a probe that
# decides tool availability without running anything.
#   ("local_script", rel)  -> app_dir/rel must exist
#   ("npx_bin", bin)       -> npx on PATH AND app_dir/node_modules/.bin/<bin>
#   ("path_bin", bin)      -> <bin> on PATH
CHECKS = {
    "laravel": [
        {"name": "pint", "cmd": "./vendor/bin/pint --test",
         "probe": ("local_script", "vendor/bin/pint")},
        {"name": "phpstan", "cmd": "./vendor/bin/phpstan analyse --no-progress",
         "probe": ("local_script", "vendor/bin/phpstan")},
    ],
    "web": [
        {"name": "tsc", "cmd": "npx --no-install vue-tsc --noEmit",
         "probe": ("npx_bin", "vue-tsc")},
        {"name": "eslint", "cmd": "npx --no-install eslint .",
         "probe": ("npx_bin", "eslint")},
        {"name": "test", "cmd": "npx --no-install vitest run",
         "probe": ("npx_bin", "vitest")},
    ],
    "flutter": [
        {"name": "analyze", "cmd": "flutter analyze", "probe": ("path_bin", "flutter")},
        {"name": "test", "cmd": "flutter test", "probe": ("path_bin", "flutter")},
    ],
}


# --- Helpers ---------------------------------------------------------------
def _as_text(value):
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    return value


def tail(text, n=TAIL_LINES):
    text = _as_text(text)
    if not text:
        return ""
    return "\n".join(text.splitlines()[-n:])


def load_config():
    data = dict(DEFAULT_CONFIG)
    cfg_path = SOFI / "config.json"
    if cfg_path.exists():
        try:
            loaded = json.loads(cfg_path.read_text())
            if isinstance(loaded, dict):
                for key in DEFAULT_CONFIG:
                    val = loaded.get(key)
                    if isinstance(val, str):
                        data[key] = val
        except (OSError, ValueError):
            pass
    return data


def resolve_path(stack, cfg, path_override):
    if path_override:
        return path_override
    env_val = os.environ.get(ENV_KEYS[stack])
    if env_val:
        return env_val
    return cfg.get(CFG_KEYS[stack], "") or ""


def path_source(stack, cfg, path_override=None):
    if path_override:
        return "flag"
    if os.environ.get(ENV_KEYS[stack]):
        return "env"
    if cfg.get(CFG_KEYS[stack]):
        return "config"
    return "unset"


def probe_tool(app_dir, kind, arg):
    """Return (available: bool, detail: str) without executing the tool."""
    if kind == "local_script":
        target = app_dir / arg
        if target.exists():
            return True, str(target)
        return False, "missing: {}".format(arg)
    if kind == "npx_bin":
        if shutil.which("npx") is None:
            return False, "npx not on PATH"
        local = app_dir / "node_modules" / ".bin" / arg
        if not local.exists():
            return False, "missing: node_modules/.bin/{}".format(arg)
        return True, str(local)
    if kind == "path_bin":
        found = shutil.which(arg)
        if found:
            return True, found
        return False, "{} not on PATH".format(arg)
    return False, "unknown probe: {}".format(kind)


def run_command(app_dir, cmd, timeout=TIMEOUT):
    """Run one command; return a normalized dict (never raises)."""
    try:
        argv = shlex.split(cmd)
    except ValueError as exc:
        return {"returncode": None, "stdout": "", "stderr": str(exc), "error": True}
    try:
        proc = subprocess.run(
            argv, cwd=str(app_dir), capture_output=True, text=True, timeout=timeout
        )
        return {
            "returncode": proc.returncode,
            "stdout": _as_text(proc.stdout),
            "stderr": _as_text(proc.stderr),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "returncode": None,
            "stdout": _as_text(exc.stdout),
            "stderr": _as_text(exc.stderr),
            "timed_out": True,
        }
    except (FileNotFoundError, OSError) as exc:
        return {"returncode": None, "stdout": "", "stderr": str(exc), "error": True}


def eval_check(app_dir, check):
    """Evaluate one check inside an existing app_dir."""
    kind, arg = check["probe"]
    available, detail = probe_tool(app_dir, kind, arg)
    if not available:
        return {"name": check["name"], "status": "tool_missing", "tool": detail}

    res = run_command(app_dir, check["cmd"])
    if res.get("timed_out"):
        return {
            "name": check["name"], "status": "timeout",
            "stdout_tail": tail(res["stdout"]), "stderr_tail": tail(res["stderr"]),
        }
    if res.get("error"):
        return {
            "name": check["name"], "status": "tool_missing",
            "tool": "exec error", "stderr_tail": tail(res["stderr"]),
        }
    rc = res["returncode"]
    return {
        "name": check["name"],
        "status": "pass" if rc == 0 else "fail",
        "returncode": rc,
        "stdout_tail": tail(res["stdout"]),
        "stderr_tail": tail(res["stderr"]),
    }


def run_stack(stack, cfg, path_override):
    raw = resolve_path(stack, cfg, path_override)
    app_dir = Path(raw) if raw else None
    if not raw or app_dir is None or not app_dir.is_dir():
        checks = [{"name": c["name"], "status": "unconfigured"} for c in CHECKS[stack]]
        return {
            "stack": stack, "path": raw or "", "source": path_source(stack, cfg, path_override),
            "configured": False, "unconfigured": True, "checks": checks, "ok": False,
        }
    checks = [eval_check(app_dir, c) for c in CHECKS[stack]]
    ok = bool(checks) and all(c["status"] == "pass" for c in checks)
    return {
        "stack": stack, "path": str(app_dir), "source": path_source(stack, cfg, path_override),
        "configured": True, "unconfigured": False, "checks": checks, "ok": ok,
    }


def aggregate_exit(results, skip_unconfigured):
    statuses = []
    any_ran = False
    for r in results:
        if r.get("unconfigured"):
            if skip_unconfigured:
                continue
            statuses.extend(c["status"] for c in r["checks"])
        else:
            any_ran = True
            statuses.extend(c["status"] for c in r["checks"])
    if skip_unconfigured and not any_ran:
        return 2  # nothing configured to run -> misconfig
    if any(s in ("fail", "timeout") for s in statuses):
        return 1
    if statuses and all(s == "pass" for s in statuses):
        return 0
    return 2  # only unconfigured / tool_missing remain


# --- Output ----------------------------------------------------------------
def _stack_line(r):
    parts = ["{}:".format(r["stack"])]
    parts += ["{}={}".format(c["name"], c["status"]) for c in r["checks"]]
    parts.append("ok={}".format(r.get("ok")))
    return "  ".join(parts)


def human(obj):
    cmd = obj.get("command")
    lines = []
    if cmd == "init":
        lines.append("config: {} ({})".format(
            obj["config_path"], "created" if obj["created"] else "exists"))
    elif cmd == "status":
        lines.append("root:   {}".format(obj["root"]))
        lines.append("config: {} ({})".format(
            obj["config_path"], "found" if obj["config_exists"] else "absent"))
        for name, s in obj["stacks"].items():
            lines.append("  {:8s} path={} exists={} source={}".format(
                name, s["path"] or "-", s["exists"], s["source"]))
            for tname, t in s["tools"].items():
                mark = "OK  " if t["available"] else "MISS"
                lines.append("      {:8s} {} {}".format(tname, mark, t["detail"]))
    elif cmd == "all":
        for r in obj["stacks"]:
            lines.append(_stack_line(r))
        lines.append("ok={}".format(obj["ok"]))
    elif cmd == "selftest":
        for c in obj["cases"]:
            suffix = "" if c["pass"] else "  -- " + c["detail"]
            lines.append("[{}] {}{}".format("PASS" if c["pass"] else "FAIL", c["name"], suffix))
        lines.append(obj["result"])
    elif "stack" in obj:
        lines.append(_stack_line(obj))
    else:
        lines.append(json.dumps(obj))
    return "\n".join(lines)


def emit(obj, args):
    if getattr(args, "json", False):
        print(json.dumps(obj, indent=2))
    else:
        print(human(obj))


# --- Subcommands -----------------------------------------------------------
def cmd_init(args):
    try:
        SOFI.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    example = Path(__file__).resolve().parent / "config.example.json"
    target = SOFI / "config.json"
    created = False
    if not target.exists():
        content = None
        if example.exists():
            try:
                raw = example.read_text()
                json.loads(raw)  # validate
                content = raw
            except (OSError, ValueError):
                content = None
        if content is None:
            content = json.dumps(DEFAULT_CONFIG, indent=2) + "\n"
        target.write_text(content)
        created = True
    obj = {"command": "init", "config_path": str(target),
           "created": created, "ok": True}
    emit(obj, args)
    return 0


def cmd_stack(args):
    cfg = load_config()
    result = run_stack(args.command, cfg, args.path)
    result["command"] = args.command
    emit(result, args)
    return aggregate_exit([result], skip_unconfigured=False)


def cmd_all(args):
    cfg = load_config()
    results = [run_stack(s, cfg, None) for s in ("laravel", "web", "flutter")]
    code = aggregate_exit(results, skip_unconfigured=True)
    obj = {"command": "all", "stacks": results, "ok": code == 0}
    emit(obj, args)
    return code


def cmd_status(args):
    cfg = load_config()
    missing_dir = Path("/nonexistent-sofi-app")
    stacks = {}
    for stack in ("laravel", "web", "flutter"):
        raw = resolve_path(stack, cfg, None)
        app_dir = Path(raw) if raw else None
        exists = bool(app_dir and app_dir.is_dir())
        probe_dir = app_dir if app_dir is not None else missing_dir
        tools = {}
        for c in CHECKS[stack]:
            avail, detail = probe_tool(probe_dir, c["probe"][0], c["probe"][1])
            tools[c["name"]] = {"available": avail, "detail": detail}
        stacks[stack] = {
            "path": raw or "", "source": path_source(stack, cfg),
            "exists": exists, "tools": tools,
        }
    cfg_path = SOFI / "config.json"
    obj = {
        "command": "status", "root": str(ROOT), "sofi": str(SOFI),
        "config_path": str(cfg_path), "config_exists": cfg_path.exists(),
        "stacks": stacks, "ok": True,
    }
    emit(obj, args)
    return 0


def _child_run(script, cmd_args, env, timeout=120):
    return subprocess.run(
        [sys.executable, script] + cmd_args,
        capture_output=True, text=True, env=env, timeout=timeout,
    )


def _parse_json(proc):
    try:
        return json.loads(proc.stdout)
    except (ValueError, TypeError):
        return None


def cmd_selftest(args):
    script = str(Path(__file__).resolve())
    cases = []
    with tempfile.TemporaryDirectory(prefix="sofi-selftest-") as tmp:
        env = dict(os.environ)
        env["SOFI_HOME"] = tmp
        for key in ENV_KEYS.values():
            env.pop(key, None)

        # (a) unconfigured stack -> "unconfigured" + exit 2
        pa = _child_run(script, ["laravel", "--json"], env)
        if "Traceback" in pa.stderr:
            ok_a, why_a = False, "child crashed: " + tail(pa.stderr, 5)
        elif pa.returncode != 2:
            ok_a, why_a = False, "exit {} != 2".format(pa.returncode)
        else:
            data = _parse_json(pa)
            st = [c.get("status") for c in (data or {}).get("checks", [])]
            if st and all(s == "unconfigured" for s in st):
                ok_a, why_a = True, "exit 2, all unconfigured"
            else:
                ok_a, why_a = False, "statuses={}".format(st)
        cases.append({"name": "unconfigured stack -> unconfigured + exit 2",
                      "pass": ok_a, "detail": why_a})

        # (b) status runs cleanly (exit 0, valid JSON)
        pb = _child_run(script, ["status", "--json"], env)
        if "Traceback" in pb.stderr:
            ok_b, why_b = False, "child crashed: " + tail(pb.stderr, 5)
        elif pb.returncode != 0:
            ok_b, why_b = False, "exit {} != 0".format(pb.returncode)
        else:
            data = _parse_json(pb)
            if data and "stacks" in data:
                ok_b, why_b = True, "exit 0, valid JSON"
            else:
                ok_b, why_b = False, "invalid status JSON"
        cases.append({"name": "status runs cleanly (exit 0)",
                      "pass": ok_b, "detail": why_b})

        # (c) empty dir -> tool_missing, no crash
        empty = os.path.join(tmp, "emptyapp")
        os.makedirs(empty, exist_ok=True)
        pc = _child_run(script, ["web", "--path", empty, "--json"], env)
        if "Traceback" in pc.stderr:
            ok_c, why_c = False, "child crashed: " + tail(pc.stderr, 5)
        else:
            data = _parse_json(pc)
            st = [c.get("status") for c in (data or {}).get("checks", [])]
            if st and all(s == "tool_missing" for s in st) and pc.returncode == 2:
                ok_c, why_c = True, "all tool_missing, exit 2"
            else:
                ok_c, why_c = False, "statuses={} exit={}".format(st, pc.returncode)
        cases.append({"name": "empty dir -> tool_missing without crash",
                      "pass": ok_c, "detail": why_c})

    all_pass = all(c["pass"] for c in cases)
    obj = {"command": "selftest", "cases": cases, "ok": all_pass,
           "result": "PASS" if all_pass else "FAIL"}
    emit(obj, args)
    return 0 if all_pass else 1


# --- CLI -------------------------------------------------------------------
def build_parser():
    parser = argparse.ArgumentParser(
        prog="check", description="SOFI Self-Correction Runtime Runner")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true",
                        help="emit one JSON object to stdout")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", parents=[common],
                   help="create .sofi/config.json from config.example.json")
    for stack in ("laravel", "web", "flutter"):
        sp = sub.add_parser(stack, parents=[common], help="run {} checks".format(stack))
        sp.add_argument("--path", default=None, help="override the app path")
    sub.add_parser("all", parents=[common], help="run every configured stack")
    sub.add_parser("status", parents=[common],
                   help="show resolved config + tool availability (no execution)")
    sub.add_parser("selftest", parents=[common],
                   help="self-test the runner without a real app")
    return parser


DISPATCH = {
    "init": cmd_init,
    "laravel": cmd_stack,
    "web": cmd_stack,
    "flutter": cmd_stack,
    "all": cmd_all,
    "status": cmd_status,
    "selftest": cmd_selftest,
}


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return DISPATCH[args.command](args)
    except SystemExit:
        raise
    except Exception as exc:  # never leak a traceback
        payload = {"command": getattr(args, "command", None),
                   "error": type(exc).__name__, "message": str(exc), "ok": False}
        if getattr(args, "json", False):
            print(json.dumps(payload, indent=2))
        else:
            sys.stderr.write("error: {}: {}\n".format(type(exc).__name__, exc))
        return 2


if __name__ == "__main__":
    sys.exit(main())
