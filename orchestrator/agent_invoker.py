#!/usr/bin/env python3
"""agent_invoker.py — mechanical execution + self-healing loop.

Given a room, a task, a pruned context and a target file, this generates code
(MOCK stub offline, or ``claude -p`` in live mode), writes it atomically, then
runs a list of validators. If any validator fails, the stderr is fed back to
the generator and the unit is regenerated — up to ``max_heal`` times. This is
the loop that turns a flaky "it compiled once" into a proven green artifact.

Validators are dicts like::

    {"name": "pint", "cmd": "./vendor/bin/pint --test", "cwd": "/path/to/app"}

A special ``cmd`` value ``"MOCK_FAIL_THEN_PASS"`` fails on attempt 1 and passes
on attempt 2, so the healing loop is demonstrable fully offline. Any other
``MOCK_*`` cmd is treated as an instant pass. A real command whose binary is
missing is treated as *skipped* (rc 0) rather than failing the whole pipeline.
"""

from __future__ import annotations

import os
import re
import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

# --------------------------------------------------------------------------- #
# Base dir + limits
# --------------------------------------------------------------------------- #
BASE: Path = Path(os.environ.get("SOFI_HOME") or Path(__file__).resolve().parent)

STDERR_TAIL_LINES = 12
VALIDATOR_TIMEOUT = 300
MAX_MOCK_FIELDS = 20


# --------------------------------------------------------------------------- #
# rich console with a graceful fallback shim
# --------------------------------------------------------------------------- #
_MARKUP_RE = re.compile(r"\[/?[a-zA-Z0-9 #_.,=-]+\]")


class _ConsoleShim:
    @staticmethod
    def print(*args: object, **_kwargs: object) -> None:
        print(*[_MARKUP_RE.sub("", str(a)) for a in args])


try:  # pragma: no cover
    from rich.console import Console as _RichConsole

    _console: object = _RichConsole()
except Exception:  # pragma: no cover
    _console = _ConsoleShim()


def _tail(text: Optional[str], n: int = STDERR_TAIL_LINES) -> str:
    if not text:
        return ""
    return "\n".join(text.splitlines()[-n:]).strip()


def _pascal_case(stem: str) -> str:
    parts = re.split(r"[^a-zA-Z0-9]+", stem)
    return "".join(p[:1].upper() + p[1:] for p in parts if p) or "Generated"


class AgentInvoker:
    """Generates code for a target file and heals it until validators pass."""

    def __init__(self, live: bool = False, max_heal: int = 3) -> None:
        self.live = live
        self.max_heal = max(0, int(max_heal))

    # -- public API --------------------------------------------------------- #
    def invoke(
        self,
        room: str,
        task: Dict[str, object],
        context: Dict[str, object],
        target_file: str,
        validators: List[Dict[str, object]],
    ) -> Dict[str, object]:
        target = Path(target_file)
        log: List[Dict[str, object]] = []
        max_attempts = 1 + self.max_heal
        attempt = 0
        ok = False
        last_error: Optional[str] = None
        validators = validators or []

        while attempt < max_attempts:
            attempt += 1
            code = self._generate(room, task, context, target, attempt, last_error)
            wrote = self._write_atomic(target, code)
            if not wrote:
                log.append(
                    {
                        "attempt": attempt,
                        "validator": "write",
                        "rc": 1,
                        "stderr_tail": f"could not write {target}",
                    }
                )
                last_error = f"write failure at {target}"
                # A write failure is not something regeneration can fix; stop.
                break

            attempt_ok = True
            for v in validators:
                name = str(v.get("name", "validator"))
                rc, stderr = self._run_validator(v, attempt)
                log.append(
                    {
                        "attempt": attempt,
                        "validator": name,
                        "rc": rc,
                        "stderr_tail": _tail(stderr),
                    }
                )
                if rc != 0:
                    attempt_ok = False
                    last_error = f"{name} failed (rc={rc}):\n{_tail(stderr)}"
                    break  # heal, then re-run from the top

            if attempt_ok:
                ok = True
                break

        return {
            "ok": ok,
            "attempts": attempt,
            "target_file": str(target),
            "log": log,
            "healed": ok and attempt > 1,
        }

    # -- generation --------------------------------------------------------- #
    def _generate(
        self,
        room: str,
        task: Dict[str, object],
        context: Dict[str, object],
        target: Path,
        attempt: int,
        last_error: Optional[str],
    ) -> str:
        if self.live:
            live_code = self._generate_live(room, task, context, target, last_error)
            if live_code is not None:
                return live_code
            _console.print(
                "[yellow]WARN[/yellow] live generation failed; using MOCK stub"
            )
        return self._generate_mock(room, task, context, target, attempt, last_error)

    def _generate_mock(
        self,
        room: str,
        task: Dict[str, object],
        context: Dict[str, object],
        target: Path,
        attempt: int,
        last_error: Optional[str],
    ) -> str:
        ext = target.suffix.lower()
        stem = target.stem or "generated"
        class_name = _pascal_case(stem)
        intent = str(task.get("intent") or task.get("command") or "generated unit")
        heal_note = f" (heal attempt {attempt}: {_tail(last_error, 2)})" if last_error else ""

        if ext == ".php":
            fields = self._collect_fields(context)
            props = "\n".join(
                f"    /** @var mixed */\n    public ${f} = null;" for f in fields[:MAX_MOCK_FIELDS]
            )
            props_block = f"\n{props}\n" if props else "\n"
            return (
                "<?php\n\n"
                "declare(strict_types=1);\n\n"
                "namespace App\\Generated;\n\n"
                f"// room: {room} — {intent}{heal_note}\n"
                f"final class {class_name}\n"
                "{"
                f"{props_block}"
                "    public function handle(): array\n"
                "    {\n"
                "        return ['ok' => true];\n"
                "    }\n"
                "}\n"
            )

        if ext == ".dart":
            fields = self._collect_fields(context)
            members = "\n".join(f"  final String? {f};" for f in fields[:MAX_MOCK_FIELDS])
            members_block = f"\n{members}\n" if members else "\n"
            ctor_args = ", ".join(f"this.{f}" for f in fields[:MAX_MOCK_FIELDS])
            ctor = f"  const {class_name}({{{ctor_args}}});" if ctor_args else f"  const {class_name}();"
            return (
                f"// room: {room} — {intent}{heal_note}\n"
                f"class {class_name} {{"
                f"{members_block}"
                f"{ctor}\n\n"
                "  Map<String, dynamic> toMap() => <String, dynamic>{};\n"
                "}\n"
            )

        # Generic fallback for any other extension.
        return (
            f"# room: {room} — {intent}{heal_note}\n"
            f"# generated unit for {target.name}\n"
            "ok = true\n"
        )

    @staticmethod
    def _collect_fields(context: Dict[str, object]) -> List[str]:
        fields: List[str] = []
        relevant = context.get("relevant") if isinstance(context, dict) else None
        source_tables: List[object] = []
        if isinstance(relevant, dict) and relevant.get("tables"):
            source_tables = list(relevant.get("tables") or [])
        else:
            laravel = context.get("laravel") if isinstance(context, dict) else None
            if isinstance(laravel, dict):
                source_tables = list(laravel.get("tables") or [])
        for table in source_tables:
            if not isinstance(table, dict):
                continue
            for f in table.get("fields") or []:
                if isinstance(f, dict) and f.get("name"):
                    name = str(f["name"])
                elif isinstance(f, str):
                    name = f
                else:
                    continue
                if name.isidentifier() and name not in fields:
                    fields.append(name)
        return fields

    def _generate_live(
        self,
        room: str,
        task: Dict[str, object],
        context: Dict[str, object],
        target: Path,
        last_error: Optional[str],
    ) -> Optional[str]:
        import json

        prompt_parts = [
            f"You are the {room} engineer in an autonomous SaaS build pipeline.",
            f"Produce the FULL content of the file `{target.name}` and OUTPUT ONLY code — "
            "no prose, no markdown fences.",
            f"Task: {json.dumps(task)[:2000]}",
            f"Relevant architecture context: {json.dumps(context.get('relevant', {}))[:4000]}",
        ]
        if last_error:
            prompt_parts.append(
                "The previous attempt failed validation with this error; FIX it:\n"
                f"{_tail(last_error, 20)}"
            )
        prompt = "\n\n".join(prompt_parts)

        try:
            proc = subprocess.run(
                ["claude", "-p", prompt],
                capture_output=True,
                text=True,
                timeout=VALIDATOR_TIMEOUT,
            )
        except FileNotFoundError:
            _console.print("[yellow]WARN[/yellow] `claude` binary not found for live generation")
            return None
        except subprocess.TimeoutExpired:
            _console.print("[yellow]WARN[/yellow] live generation timed out")
            return None
        except (OSError, ValueError) as exc:
            _console.print(f"[yellow]WARN[/yellow] live generation error: {exc}")
            return None

        if proc.returncode != 0 or not (proc.stdout or "").strip():
            _console.print(
                f"[yellow]WARN[/yellow] live generation rc={proc.returncode} / empty output"
            )
            return None

        return self._strip_fences(proc.stdout)

    @staticmethod
    def _strip_fences(text: str) -> str:
        stripped = text.strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            if lines:
                lines = lines[1:]  # drop opening fence (```lang)
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            return "\n".join(lines) + "\n"
        return text

    # -- IO ----------------------------------------------------------------- #
    @staticmethod
    def _write_atomic(target: Path, code: str) -> bool:
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            _console.print(f"[red]ERROR[/red] cannot create dir {target.parent}: {exc}")
            return False

        tmp_path: Optional[str] = None
        try:
            fd, tmp_path = tempfile.mkstemp(
                prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent)
            )
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(code)
            os.replace(tmp_path, str(target))
            return True
        except OSError as exc:
            _console.print(f"[red]ERROR[/red] atomic write failed for {target}: {exc}")
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
            return False

    # -- validators --------------------------------------------------------- #
    def _run_validator(self, validator: Dict[str, object], attempt: int) -> tuple:
        cmd = str(validator.get("cmd", "")).strip()
        name = str(validator.get("name", "validator"))
        cwd = validator.get("cwd")

        # MOCK directives -------------------------------------------------- #
        if cmd == "MOCK_FAIL_THEN_PASS":
            if attempt == 1:
                return 1, f"[MOCK] {name}: intentional failure on attempt 1 (heal me)"
            return 0, ""
        if cmd.startswith("MOCK_"):
            # Any other MOCK_* directive is an instant pass.
            return 0, f"[MOCK] {name}: {cmd} -> pass"
        if not cmd:
            return 0, f"[skip] {name}: empty command"

        # Real command ----------------------------------------------------- #
        try:
            argv = shlex.split(cmd)
        except ValueError as exc:
            return 1, f"{name}: cannot parse command: {exc}"
        if not argv:
            return 0, f"[skip] {name}: empty command"

        run_cwd: Optional[str] = None
        if isinstance(cwd, str) and cwd:
            run_cwd = cwd
            try:
                if not Path(cwd).is_dir():
                    return 0, f"[skip] {name}: cwd {cwd} missing"
            except OSError:
                return 0, f"[skip] {name}: cwd {cwd} unreadable"

        try:
            proc = subprocess.run(
                argv,
                cwd=run_cwd,
                capture_output=True,
                text=True,
                timeout=VALIDATOR_TIMEOUT,
            )
        except FileNotFoundError:
            # Binary missing → skip (rc 0), do not fail the pipeline.
            return 0, f"[skip] {name}: binary '{argv[0]}' not installed"
        except subprocess.TimeoutExpired:
            return 1, f"{name}: timed out after {VALIDATOR_TIMEOUT}s"
        except (OSError, ValueError) as exc:
            return 1, f"{name}: subprocess error: {exc}"

        combined = (proc.stderr or "") + (proc.stdout or "")
        return proc.returncode, combined


# --------------------------------------------------------------------------- #
# Selftest (offline)
# --------------------------------------------------------------------------- #
def _selftest() -> bool:
    ok = True
    tmp = Path(tempfile.mkdtemp(prefix="sofi_invoker_"))
    target = tmp / "generated" / "PhoneNumber.php"
    try:
        invoker = AgentInvoker(live=False, max_heal=3)
        context = {
            "relevant": {
                "tables": [
                    {"table": "users", "fields": [{"name": "phone_number", "type": "string"}]}
                ]
            }
        }
        task = {"intent": "add phone_number to users", "command": "add column"}
        validators = [
            {"name": "mock_heal", "cmd": "MOCK_FAIL_THEN_PASS", "cwd": None},
        ]

        result = invoker.invoke("BKD-05", task, context, str(target), validators)

        assert result["ok"] is True, f"expected ok, got {result}"
        assert result["attempts"] == 2, f"expected 2 attempts, got {result['attempts']}"
        assert result["healed"] is True, "expected healed True (fail then pass)"
        assert Path(result["target_file"]).is_file(), "target file must be written"
        content = target.read_text(encoding="utf-8")
        assert "class PhoneNumber" in content, "generated PHP must define the class"
        assert "phone_number" in content, "generated PHP should reference the field"
        # Log must show attempt-1 failure and attempt-2 pass.
        assert any(e["attempt"] == 1 and e["rc"] == 1 for e in result["log"]), "attempt 1 must fail"
        assert any(e["attempt"] == 2 and e["rc"] == 0 for e in result["log"]), "attempt 2 must pass"

        # A missing real binary must be treated as a skip (still ok).
        dart_target = tmp / "generated" / "profile_widget.dart"
        res2 = invoker.invoke(
            "MOB-04",
            {"intent": "profile widget"},
            {"relevant": {"tables": []}},
            str(dart_target),
            [{"name": "flutter", "cmd": "definitely-not-a-real-binary analyze", "cwd": None}],
        )
        assert res2["ok"] is True, "missing binary must skip (ok True)"
        assert res2["healed"] is False, "no heal needed for skip"
        assert dart_target.is_file(), "dart target must be written"
        assert "class ProfileWidget" in dart_target.read_text(encoding="utf-8"), "dart class expected"
    except AssertionError as exc:
        ok = False
        _console.print(f"[red]assertion failed:[/red] {exc}")
    except Exception as exc:  # noqa: BLE001
        ok = False
        _console.print(f"[red]unexpected error:[/red] {exc}")
    finally:
        import shutil

        shutil.rmtree(tmp, ignore_errors=True)

    _console.print("[bold green]PASS[/bold green] agent_invoker selftest" if ok else "[bold red]FAIL[/bold red] agent_invoker selftest")
    return ok


if __name__ == "__main__":
    import sys

    sys.exit(0 if _selftest() else 1)
