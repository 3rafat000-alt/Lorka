#!/usr/bin/env python3
"""main.py — SOFI external orchestrator, Central Command.

Converts one casual instruction into a deterministic, state-tracked build
pipeline across specialised "room" agents, for a Laravel + Flutter SaaS. Runs
STANDALONE on an Ubuntu terminal (not inside Claude Code). Agents are invoked as
subprocesses. Fully offline in the default MOCK mode; a real mode uses
``claude -p`` and the project's real validators.

Pipeline
    refine → scan → backend build → flutter build → QA verify → (optional) commit

Usage
    python3 main.py --cmd "add phone_number to users table and show it on the profile screen"
    python3 main.py --cmd "..." --laravel-path ./api --flutter-path ./app --live --commit
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# --------------------------------------------------------------------------- #
# Base dir + import path
# --------------------------------------------------------------------------- #
BASE: Path = Path(os.environ.get("SOFI_HOME") or Path(__file__).resolve().parent)
_SCRIPT_DIR: Path = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from orchestrator.agent_invoker import AgentInvoker  # noqa: E402
from orchestrator.architecture_scanner import ArchitectureScanner  # noqa: E402
from orchestrator.state_db import StateDB, TaskState  # noqa: E402
from orchestrator.translator_gateway import TranslatorGateway  # noqa: E402

GITFLOW: Path = BASE / ".claude" / "engine" / "tooling" / "gitflow.py"


# --------------------------------------------------------------------------- #
# rich console + helpers with graceful fallback
# --------------------------------------------------------------------------- #
_MARKUP_RE = re.compile(r"\[/?[a-zA-Z0-9 #_.,=-]+\]")

try:  # pragma: no cover
    from rich.console import Console as _RichConsole
    from rich.panel import Panel as _Panel
    from rich.table import Table as _Table

    _console = _RichConsole()
    _RICH = True
except Exception:  # pragma: no cover
    _RICH = False

    class _ConsoleShim:
        @staticmethod
        def print(*args: object, **_kwargs: object) -> None:
            print(*[_MARKUP_RE.sub("", str(a)) for a in args])

    _console = _ConsoleShim()  # type: ignore[assignment]


def _banner(step: str, text: str) -> None:
    if _RICH:
        _console.print(_Panel.fit(f"[bold]{text}[/bold]", title=f"[cyan]{step}[/cyan]", border_style="cyan"))
    else:
        _console.print(f"\n=== {step} :: {text} ===")


def _info(text: str) -> None:
    _console.print(f"[blue]•[/blue] {text}")


def _warn(text: str) -> None:
    _console.print(f"[yellow]WARN[/yellow] {text}")


def _err(text: str) -> None:
    _console.print(f"[red]ERROR[/red] {text}")


def _ok(text: str) -> None:
    _console.print(f"[green]✓[/green] {text}")


def _pascal_case(stem: str) -> str:
    parts = re.split(r"[^a-zA-Z0-9]+", stem)
    return "".join(p[:1].upper() + p[1:] for p in parts if p) or "Generated"


# --------------------------------------------------------------------------- #
# Target-file resolution
# --------------------------------------------------------------------------- #
def _backend_target(payload: Dict[str, object], laravel_path: Optional[str]) -> Path:
    muts = payload.get("database_mutations") or []
    table = "changes"
    if muts and isinstance(muts[0], dict) and muts[0].get("table"):
        table = str(muts[0]["table"])
    class_name = f"Update{_pascal_case(table)}Table"
    if laravel_path:
        return Path(laravel_path) / "app" / "Generated" / f"{class_name}.php"
    return BASE / ".sofi" / "generated" / "BKD-05" / f"{class_name}.php"


def _flutter_target(payload: Dict[str, object], flutter_path: Optional[str]) -> Path:
    uis = payload.get("ui_changes") or []
    screen = "profile_screen"
    if uis and isinstance(uis[0], dict) and uis[0].get("screen"):
        screen = str(uis[0]["screen"])
    if not screen.endswith(".dart"):
        file_name = f"{screen}.dart"
    else:
        file_name = screen
    if flutter_path:
        return Path(flutter_path) / "lib" / "generated" / file_name
    return BASE / ".sofi" / "generated" / "MOB-04" / file_name


def _backend_validators(laravel_path: Optional[str]) -> List[Dict[str, object]]:
    # Real commands; when the binary or cwd is missing they are skipped (rc 0),
    # so the pipeline completes offline without MOCK_FAIL_THEN_PASS.
    return [
        {"name": "pint", "cmd": "./vendor/bin/pint --test", "cwd": laravel_path},
        {"name": "phpstan", "cmd": "./vendor/bin/phpstan analyse --no-progress", "cwd": laravel_path},
    ]


def _flutter_validators(flutter_path: Optional[str]) -> List[Dict[str, object]]:
    return [{"name": "flutter_analyze", "cmd": "flutter analyze", "cwd": flutter_path}]


# --------------------------------------------------------------------------- #
# Commit (optional, guarded via gitflow.py)
# --------------------------------------------------------------------------- #
def _run_gitflow(argv: List[str]) -> Dict[str, object]:
    """Run gitflow.py with --json; return {rc, data, raw, err}. Never raises."""
    if not GITFLOW.is_file():
        return {"rc": 127, "data": {}, "raw": "", "err": f"gitflow not found at {GITFLOW}"}
    try:
        proc = subprocess.run(
            [sys.executable, str(GITFLOW), *argv, "--json"],
            cwd=str(BASE),
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"rc": 1, "data": {}, "raw": "", "err": str(exc)}
    data: Dict[str, object] = {}
    if proc.stdout:
        try:
            parsed = json.loads(proc.stdout)
            if isinstance(parsed, dict):
                data = parsed
        except json.JSONDecodeError:
            pass
    return {"rc": proc.returncode, "data": data, "raw": proc.stdout, "err": proc.stderr}


def _handle_commit(commit: bool, task_id: int, files: List[str]) -> str:
    inside_repo: List[str] = []
    for f in files:
        try:
            Path(f).resolve().relative_to(BASE)
            inside_repo.append(f)
        except ValueError:
            continue

    if not commit:
        _info("DRY RUN (no --commit). Would commit these artifacts:")
        for f in files:
            _console.print(f"    - {f}")
        return "dry-run"

    if not inside_repo:
        _warn("no generated artifacts live inside the repo; nothing to commit.")
        return "skipped: no in-repo artifacts"

    cur = _run_gitflow(["current"])
    branch = str(cur["data"].get("branch", "")) if isinstance(cur["data"], dict) else ""
    protected = bool(cur["data"].get("protected")) if isinstance(cur["data"], dict) else False

    if protected or branch in ("main", "master", "prod", "production", ""):
        new_branch = f"prj/orchestrator-task-{task_id}"
        _info(f"on protected/unknown branch '{branch or '?'}' → creating '{new_branch}'")
        br = _run_gitflow(["branch", new_branch])
        if br["rc"] != 0:
            _warn(f"gitflow refused to branch (rc={br['rc']}): {(br['err'] or br['raw']).strip()[:200]}")
            return f"skipped: branch refused (rc={br['rc']})"

    message = f"orchestrator task #{task_id}: generated {len(inside_repo)} artifact(s)"
    cm = _run_gitflow(
        ["commit", "--type", "feat", "--scope", "orchestrator", "--message", message, "--all"]
    )
    if cm["rc"] != 0:
        _warn(f"gitflow refused/failed to commit (rc={cm['rc']}): {(cm['err'] or cm['raw']).strip()[:200]}")
        return f"skipped: commit refused (rc={cm['rc']})"
    _ok("committed generated artifacts via gitflow.")
    return "committed"


# --------------------------------------------------------------------------- #
# Build-stage runner
# --------------------------------------------------------------------------- #
def _run_stage(
    db: StateDB,
    task_id: int,
    invoker: AgentInvoker,
    *,
    room: str,
    processing: TaskState,
    success: TaskState,
    payload: Dict[str, object],
    context: Dict[str, object],
    target: Path,
    validators: List[Dict[str, object]],
    written: List[str],
    heal_counter: Dict[str, int],
) -> bool:
    """Run one build stage; update state; return True on success."""
    _banner(room, f"processing → {target}")
    db.set_state(task_id, processing)
    task_ctx = {
        "intent": payload.get("intent"),
        "command": payload.get("intent"),
        "target_stack": payload.get("target_stack"),
    }
    result = invoker.invoke(room, task_ctx, context, str(target), validators)
    heal_counter[room] = int(result.get("attempts", 1))

    for entry in result.get("log", []):
        rc = entry.get("rc")
        tag = "[green]ok[/green]" if rc == 0 else "[red]fail[/red]"
        _console.print(
            f"    attempt {entry.get('attempt')} · {entry.get('validator')} · rc={rc} {tag}"
        )
        tail = str(entry.get("stderr_tail") or "").strip()
        if tail and rc != 0:
            _console.print(f"      [dim]{tail.splitlines()[-1][:160]}[/dim]")

    if result.get("ok"):
        written.append(result["target_file"])
        db.set_state(task_id, success)
        healed = " (self-healed)" if result.get("healed") else ""
        _ok(f"{room} success in {result.get('attempts')} attempt(s){healed}")
        return True

    db.set_state(task_id, TaskState.FAILED, error=f"{room} build failed after {result.get('attempts')} attempts")
    _err(f"{room} build FAILED after {result.get('attempts')} attempt(s)")
    return False


# --------------------------------------------------------------------------- #
# Pipeline
# --------------------------------------------------------------------------- #
def run_pipeline(args: argparse.Namespace) -> int:
    _banner("SOFI", "External Orchestrator — Central Command")
    _info(f"mode: {'LIVE (claude -p)' if args.live else 'MOCK (offline)'}")
    _info(f"base: {BASE}")

    db = StateDB(db_path=str(BASE / ".sofi" / "orchestrator.db"))
    gateway = TranslatorGateway(live=args.live)
    invoker = AgentInvoker(live=args.live, max_heal=args.max_heal)

    written: List[str] = []
    heal_counter: Dict[str, int] = {}
    task_id = -1

    try:
        # -- 1) Refine ----------------------------------------------------- #
        _banner("Gateway", "refining instruction → strict payload")
        try:
            payload = gateway.refine(args.cmd)
        except ValueError as exc:
            _err(f"refine failed: {exc}")
            return 2
        task_id = db.create_task(args.cmd)
        stack = str(payload.get("target_stack", "Laravel"))
        db.set_state(task_id, TaskState.REFINED, payload=payload, stack=stack)
        _ok(f"task #{task_id} refined · target_stack={stack}")
        _console.print(f"    [dim]{json.dumps(payload)[:400]}[/dim]")

        # -- 2) Scan ------------------------------------------------------- #
        _banner("Scanner", "pruning architecture to relevant context")
        scanner = ArchitectureScanner(args.laravel_path, args.flutter_path)
        context = scanner.scan(payload)
        lv = context["laravel"]
        fl = context["flutter"]
        _info(f"laravel available={lv['available']} tables={len(lv['tables'])} routes={len(lv['routes'])}")
        _info(f"flutter available={fl['available']} widgets={len(fl['widgets'])} models={len(fl['models'])}")

        # -- 3) Backend ---------------------------------------------------- #
        if stack in ("Laravel", "Both"):
            target = _backend_target(payload, args.laravel_path)
            if not _run_stage(
                db, task_id, invoker,
                room="BKD-05", processing=TaskState.BACKEND_PROCESSING,
                success=TaskState.BACKEND_SUCCESS, payload=payload, context=context,
                target=target, validators=_backend_validators(args.laravel_path),
                written=written, heal_counter=heal_counter,
            ):
                _print_summary(db, task_id, written, heal_counter)
                return 1

        # -- 4) Flutter ---------------------------------------------------- #
        if stack in ("Flutter", "Both"):
            target = _flutter_target(payload, args.flutter_path)
            if not _run_stage(
                db, task_id, invoker,
                room="MOB-04", processing=TaskState.FLUTTER_PROCESSING,
                success=TaskState.FLUTTER_SUCCESS, payload=payload, context=context,
                target=target, validators=_flutter_validators(args.flutter_path),
                written=written, heal_counter=heal_counter,
            ):
                _print_summary(db, task_id, written, heal_counter)
                return 1

        # -- 5) QA verify -------------------------------------------------- #
        _banner("QA", "final verification of generated artifacts")
        db.set_state(task_id, TaskState.QA_VERIFYING)
        missing = [f for f in written if not Path(f).is_file()]
        if missing:
            db.set_state(task_id, TaskState.FAILED, error=f"missing artifacts: {missing}")
            _err(f"QA failed — missing artifacts: {missing}")
            _print_summary(db, task_id, written, heal_counter)
            return 1
        if not written:
            _warn("no artifacts were generated (empty stack?)")
        db.set_state(task_id, TaskState.COMPLETED)
        _ok("QA passed — all artifacts present.")

        # -- 6) Commit (optional) ------------------------------------------ #
        _banner("Gitflow", "commit stage")
        commit_status = _handle_commit(args.commit, task_id, written)
        _info(f"commit: {commit_status}")

    except Exception as exc:  # noqa: BLE001 - top-level guard, never leak a traceback
        _err(f"pipeline aborted: {exc}")
        if task_id > 0:
            try:
                cur = db.get(task_id)
                if cur and cur["state"] not in (TaskState.COMPLETED.value, TaskState.FAILED.value):
                    db.set_state(task_id, TaskState.FAILED, error=str(exc))
            except Exception:  # noqa: BLE001
                pass
        _print_summary(db, task_id, written, heal_counter)
        return 1

    _print_summary(db, task_id, written, heal_counter)
    final = db.get(task_id) if task_id > 0 else None
    return 0 if final and final["state"] == TaskState.COMPLETED.value else 1


# --------------------------------------------------------------------------- #
# Summary
# --------------------------------------------------------------------------- #
def _print_summary(
    db: StateDB, task_id: int, written: List[str], heal_counter: Dict[str, int]
) -> None:
    task = db.get(task_id) if task_id > 0 else None
    final_state = task["state"] if task else "UNKNOWN"
    heal_str = ", ".join(f"{r}={n}" for r, n in heal_counter.items()) or "none"

    if _RICH:
        table = _Table(title="Orchestrator Summary", show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        table.add_row("task id", str(task_id))
        state_color = "green" if final_state == TaskState.COMPLETED.value else (
            "red" if final_state == TaskState.FAILED.value else "yellow"
        )
        table.add_row("final state", f"[{state_color}]{final_state}[/{state_color}]")
        table.add_row("files written", str(len(written)))
        for f in written:
            table.add_row("", f)
        table.add_row("heal attempts", heal_str)
        _console.print(table)
    else:
        _console.print("\n----- Orchestrator Summary -----")
        _console.print(f"task id       : {task_id}")
        _console.print(f"final state   : {final_state}")
        _console.print(f"files written : {len(written)}")
        for f in written:
            _console.print(f"    - {f}")
        _console.print(f"heal attempts : {heal_str}")
        _console.print("--------------------------------")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="main.py",
        description="SOFI external multi-agent orchestrator (Laravel + Flutter).",
    )
    p.add_argument("--cmd", required=True, help="the casual human instruction to execute")
    p.add_argument("--live", action="store_true", help="use `claude -p` (default: offline MOCK)")
    p.add_argument("--laravel-path", default=None, help="path to the Laravel backend repo")
    p.add_argument("--flutter-path", default=None, help="path to the Flutter mobile repo")
    p.add_argument("--max-heal", type=int, default=3, help="max self-heal retries per stage")
    p.add_argument("--commit", action="store_true", help="branch + commit artifacts via gitflow (default: dry)")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:  # argparse already printed usage
        return int(exc.code) if isinstance(exc.code, int) else 2
    if args.max_heal < 0:
        args.max_heal = 0
    return run_pipeline(args)


if __name__ == "__main__":
    sys.exit(main())
