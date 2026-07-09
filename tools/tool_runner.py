#!/usr/bin/env python3
"""SOFI tools — command-line runner.

Thin CLI over :class:`tools.room_manager.RoomManager`. Subcommands:

  rooms                 list room codes + tool counts
  list [--room R]       list tools (name · room · summary)
  spec <name>           print a tool's full spec (incl. input_schema)
  run <name> ...        run a tool with --params '<json>' or --params-file <path>
  selftest              run every tool against its sample; exit 0 if ok else 1

Every subcommand accepts ``--json`` to emit exactly one JSON object (no rich).
Human output uses ``rich`` tables when available, with a plain-print fallback.
No traceback ever reaches the user: unexpected errors become a JSON error object
plus a non-zero exit.

Exit codes:  0 ok · 1 not-ok (failed run / failed selftest / unknown tool) ·
2 bad input (invalid JSON params, missing file) or unexpected internal error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# --- ensure repo root is importable when run as `python3 tools/tool_runner.py` ---
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.room_manager import RoomManager  # noqa: E402  (after sys.path fix)

# --- optional pretty output; graceful fallback to plain print --------------
try:
    from rich.console import Console
    from rich.table import Table

    _console: Optional["Console"] = Console()
    _RICH = True
except Exception:  # pragma: no cover - rich is optional
    _console = None
    _RICH = False


# --- output helpers --------------------------------------------------------
def _emit_json(obj: Any) -> None:
    """Print exactly one JSON object to stdout."""
    print(json.dumps(obj, indent=2, default=str))


def _print_json_plain(obj: Any) -> None:
    """Pretty-print a JSON object using rich if present, else stdlib."""
    if _RICH and _console is not None:
        try:
            _console.print_json(data=obj)
            return
        except Exception:  # pragma: no cover - fall through to stdlib
            pass
    print(json.dumps(obj, indent=2, default=str))


# --- subcommand handlers (return process exit code) ------------------------
def cmd_rooms(rm: RoomManager, args: argparse.Namespace) -> int:
    specs = rm.list_tools()
    counts: Dict[str, int] = {}
    for spec in specs:
        counts[spec["room"]] = counts.get(spec["room"], 0) + 1
    rooms = rm.rooms()

    if args.json:
        _emit_json({
            "ok": True,
            "rooms": [{"room": r, "tools": counts.get(r, 0)} for r in rooms],
            "total_rooms": len(rooms),
            "total_tools": len(specs),
        })
        return 0

    if not rooms:
        print("(no rooms discovered)")
        return 0
    if _RICH and _console is not None:
        table = Table(title="SOFI rooms")
        table.add_column("Room", style="cyan", no_wrap=True)
        table.add_column("Tools", justify="right", style="magenta")
        for r in rooms:
            table.add_row(r or "(none)", str(counts.get(r, 0)))
        _console.print(table)
        _console.print(f"{len(rooms)} rooms · {len(specs)} tools")
    else:
        for r in rooms:
            print(f"{(r or '(none)'):16} {counts.get(r, 0)}")
        print(f"{len(rooms)} rooms · {len(specs)} tools")
    return 0


def cmd_list(rm: RoomManager, args: argparse.Namespace) -> int:
    specs = rm.list_tools(args.room)

    if args.json:
        _emit_json({"ok": True, "room": args.room, "count": len(specs), "tools": specs})
        return 0

    if not specs:
        scope = f" in room {args.room!r}" if args.room else ""
        print(f"(no tools discovered{scope})")
        return 0
    if _RICH and _console is not None:
        title = f"Tools in {args.room}" if args.room else "All tools"
        table = Table(title=title)
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Room", style="green", no_wrap=True)
        table.add_column("Summary", style="white")
        for spec in specs:
            table.add_row(spec["name"], spec["room"] or "(none)", spec["summary"] or "")
        _console.print(table)
    else:
        for spec in specs:
            print(f"{spec['name']:28} {spec['room'] or '(none)':10} {spec['summary'] or ''}")
    return 0


def cmd_spec(rm: RoomManager, args: argparse.Namespace) -> int:
    cls = rm.get(args.name)
    if cls is None:
        payload = {"ok": False, "error": f"unknown tool: {args.name}"}
        if args.json:
            _emit_json(payload)
        elif _RICH and _console is not None:
            _console.print(f"[red]unknown tool:[/red] {args.name}")
        else:
            print(f"unknown tool: {args.name}", file=sys.stderr)
        return 1

    spec = cls.spec()
    if args.json:
        _emit_json({"ok": True, "spec": spec})
        return 0
    _print_json_plain(spec)
    return 0


def _load_params(args: argparse.Namespace) -> Dict[str, Any]:
    """Load run params from --params or --params-file.

    Raises ``ValueError`` for bad/missing input (mapped to exit code 2 by caller).
    """
    if args.params is not None:
        text = args.params
        source = "--params"
    else:
        path = Path(args.params_file)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ValueError(f"cannot read params file {args.params_file!r}: {exc}") from exc
        source = f"--params-file {args.params_file}"
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {source}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"params from {source} must be a JSON object, got {type(data).__name__}")
    return data


def cmd_run(rm: RoomManager, args: argparse.Namespace) -> int:
    try:
        params = _load_params(args)
    except ValueError as exc:
        _emit_json({"ok": False, "error": str(exc)}) if args.json else print(
            f"error: {exc}", file=sys.stderr
        )
        return 2

    result = rm.run(args.name, params)
    payload = result.to_dict()
    if args.json:
        _emit_json(payload)
    else:
        _print_json_plain(payload)
    return 0 if result.ok else 1


def cmd_selftest(rm: RoomManager, args: argparse.Namespace) -> int:
    report = rm.selftest()
    if args.json:
        _emit_json(report)
        return 0 if report["ok"] else 1

    status = "PASS" if report["ok"] else "FAIL"
    line = f"selftest {status} — {report['passed']}/{report['total']} passed"
    if _RICH and _console is not None:
        colour = "green" if report["ok"] else "red"
        _console.print(f"[{colour}]{line}[/{colour}]")
        if report["failures"]:
            table = Table(title="Failures")
            table.add_column("Tool", style="cyan", no_wrap=True)
            table.add_column("Error", style="red")
            for fail in report["failures"]:
                table.add_row(fail["name"], fail["error"])
            _console.print(table)
    else:
        print(line)
        for fail in report["failures"]:
            print(f"  FAIL {fail['name']}: {fail['error']}")
    return 0 if report["ok"] else 1


# --- argument parser -------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="emit one JSON object")

    parser = argparse.ArgumentParser(prog="tool_runner", description="SOFI room tools CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_rooms = sub.add_parser("rooms", parents=[common], help="list rooms + tool counts")
    p_rooms.set_defaults(func=cmd_rooms)

    p_list = sub.add_parser("list", parents=[common], help="list tools")
    p_list.add_argument("--room", default=None, help="filter to one room code")
    p_list.set_defaults(func=cmd_list)

    p_spec = sub.add_parser("spec", parents=[common], help="show a tool's full spec")
    p_spec.add_argument("name", help="tool name")
    p_spec.set_defaults(func=cmd_spec)

    p_run = sub.add_parser("run", parents=[common], help="run a tool")
    p_run.add_argument("name", help="tool name")
    g = p_run.add_mutually_exclusive_group(required=True)
    g.add_argument("--params", help="params as a JSON object string")
    g.add_argument("--params-file", help="path to a JSON file of params")
    p_run.set_defaults(func=cmd_run)

    p_self = sub.add_parser("selftest", parents=[common], help="run all tool self-tests")
    p_self.set_defaults(func=cmd_selftest)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    rm = RoomManager()
    code = args.func(rm, args)
    return code if isinstance(code, int) else 0


if __name__ == "__main__":
    try:
        _code = main()
    except SystemExit:
        raise  # argparse usage/exit — already handled, no traceback
    except Exception as exc:  # never leak a traceback
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}))
        sys.exit(2)
    sys.exit(_code)
