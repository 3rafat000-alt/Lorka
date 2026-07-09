#!/usr/bin/env python3
"""translator_gateway.py — Semantic Gateway / Input Refiner.

Turns one casual human instruction into a STRICT, schema-validated payload the
rest of the pipeline can execute deterministically. It has two modes:

* MOCK (default, offline): a deterministic keyword heuristic. No network, no
  external binary. Given the same input it always returns the same payload.
* LIVE: shells out to ``claude -p`` and extracts the first JSON object from the
  model's stdout. Any failure falls back to MOCK and logs a warning so the
  pipeline never dies at the gateway.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

# --------------------------------------------------------------------------- #
# Base dir resolution
# --------------------------------------------------------------------------- #
BASE: Path = Path(os.environ.get("SOFI_HOME") or Path(__file__).resolve().parent)


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


# --------------------------------------------------------------------------- #
# jsonschema (hard dependency, but degrade to a lightweight validator if absent)
# --------------------------------------------------------------------------- #
try:
    from jsonschema import Draft7Validator  # type: ignore
    from jsonschema import ValidationError as _JSValidationError  # type: ignore

    _HAVE_JSONSCHEMA = True
except Exception:  # pragma: no cover - defensive fallback
    Draft7Validator = None  # type: ignore
    _JSValidationError = Exception  # type: ignore
    _HAVE_JSONSCHEMA = False


PAYLOAD_SCHEMA: Dict[str, object] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["intent", "target_stack", "database_mutations", "ui_changes"],
    "properties": {
        "intent": {"type": "string", "minLength": 1},
        "target_stack": {"enum": ["Laravel", "Flutter", "Both"]},
        "database_mutations": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["table", "fields"],
                "properties": {
                    "table": {"type": "string", "minLength": 1},
                    "fields": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["name", "type"],
                            "properties": {
                                "name": {"type": "string", "minLength": 1},
                                "type": {"type": "string", "minLength": 1},
                                "nullable": {"type": "boolean"},
                            },
                        },
                    },
                },
            },
        },
        "ui_changes": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["screen", "widgets"],
                "properties": {
                    "screen": {"type": "string", "minLength": 1},
                    "widgets": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
    },
}


# Keyword cues → stack.
_LARAVEL_CUES = ("db", "table", "migration", "laravel", "backend", "api", "database", "column", "endpoint", "model")
_FLUTTER_CUES = ("screen", "ui", "widget", "flutter", "mobile", "form", "page", "app", "view", "button")

# Common field-name cues → (column type, nullable).
_FIELD_CUES: Dict[str, Dict[str, object]] = {
    "phone_number": {"name": "phone_number", "type": "string", "nullable": True},
    "phone": {"name": "phone", "type": "string", "nullable": True},
    "email": {"name": "email", "type": "string", "nullable": False},
    "password": {"name": "password", "type": "string", "nullable": False},
    "name": {"name": "name", "type": "string", "nullable": True},
    "avatar": {"name": "avatar", "type": "string", "nullable": True},
    "address": {"name": "address", "type": "string", "nullable": True},
    "age": {"name": "age", "type": "integer", "nullable": True},
    "is_active": {"name": "is_active", "type": "boolean", "nullable": False},
    "bio": {"name": "bio", "type": "text", "nullable": True},
}


def _extract_first_json(text: str) -> Optional[Dict[str, object]]:
    """Return the first balanced JSON object found in ``text``, or None."""
    if not text:
        return None
    depth = 0
    start = -1
    in_string = False
    escape = False
    for i, ch in enumerate(text):
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and start != -1:
                    candidate = text[start : i + 1]
                    try:
                        obj = json.loads(candidate)
                    except json.JSONDecodeError:
                        start = -1
                        continue
                    if isinstance(obj, dict):
                        return obj
    return None


class TranslatorGateway:
    """Refines a raw human instruction into a strict, validated payload."""

    def __init__(self, live: bool = False) -> None:
        self.live = live

    # -- public API --------------------------------------------------------- #
    def refine(self, raw_input: str) -> Dict[str, object]:
        """Return a schema-valid payload for ``raw_input``."""
        payload: Optional[Dict[str, object]] = None

        if self.live:
            payload = self._refine_live(raw_input)
            if payload is None:
                _console.print(
                    "[yellow]WARN[/yellow] live refine failed; falling back to MOCK heuristic"
                )

        if payload is None:
            payload = self._refine_mock(raw_input)

        self._validate(payload)
        return payload

    # -- validation --------------------------------------------------------- #
    @staticmethod
    def _validate(payload: Dict[str, object]) -> None:
        if _HAVE_JSONSCHEMA and Draft7Validator is not None:
            validator = Draft7Validator(PAYLOAD_SCHEMA)
            errors = sorted(validator.iter_errors(payload), key=lambda e: list(e.path))
            if errors:
                first = errors[0]
                loc = "/".join(str(p) for p in first.path) or "<root>"
                raise ValueError(
                    f"refine produced invalid payload: {loc}: {first.message}"
                )
        else:  # pragma: no cover - minimal structural fallback
            if not isinstance(payload, dict):
                raise ValueError("refine produced invalid payload: not an object")
            if payload.get("target_stack") not in ("Laravel", "Flutter", "Both"):
                raise ValueError("refine produced invalid payload: bad target_stack")
            for key in ("database_mutations", "ui_changes"):
                if not isinstance(payload.get(key), list):
                    raise ValueError(f"refine produced invalid payload: {key} not a list")

    # -- MOCK heuristic ----------------------------------------------------- #
    def _refine_mock(self, raw_input: str) -> Dict[str, object]:
        text = (raw_input or "").lower()

        wants_backend = any(cue in text for cue in _LARAVEL_CUES)
        wants_frontend = any(cue in text for cue in _FLUTTER_CUES)

        if wants_backend and wants_frontend:
            target_stack = "Both"
        elif wants_frontend and not wants_backend:
            target_stack = "Flutter"
        else:
            # Default to Laravel — never leave target_stack empty.
            target_stack = "Laravel"

        # Detect field names (longest cue first so phone_number wins over phone).
        detected_fields: List[Dict[str, object]] = []
        seen: set = set()
        for cue in sorted(_FIELD_CUES, key=len, reverse=True):
            if re.search(r"\b" + re.escape(cue) + r"\b", text) and cue not in seen:
                # Avoid double-counting phone when phone_number already matched.
                if cue == "phone" and "phone_number" in seen:
                    continue
                detected_fields.append(dict(_FIELD_CUES[cue]))
                seen.add(cue)

        # Pick a target table (best-effort noun scan; default "users").
        table = self._guess_table(text)

        database_mutations: List[Dict[str, object]] = []
        if target_stack in ("Laravel", "Both"):
            fields = detected_fields or [
                {"name": "updated_field", "type": "string", "nullable": True}
            ]
            database_mutations.append({"table": table, "fields": fields})

        ui_changes: List[Dict[str, object]] = []
        if target_stack in ("Flutter", "Both"):
            screen = self._guess_screen(text)
            widgets = [f["name"] + "_field" for f in detected_fields] or ["content_widget"]
            ui_changes.append({"screen": screen, "widgets": widgets})

        intent = (raw_input or "").strip() or "no-op instruction"
        # Keep intent bounded to avoid token bloat downstream.
        if len(intent) > 240:
            intent = intent[:237] + "..."

        return {
            "intent": intent,
            "target_stack": target_stack,
            "database_mutations": database_mutations,
            "ui_changes": ui_changes,
        }

    @staticmethod
    def _guess_table(text: str) -> str:
        # "<word> table" pattern, else known nouns, else users.
        m = re.search(r"\b([a-z_][a-z0-9_]*)\s+table\b", text)
        if m:
            return m.group(1)
        for noun in ("users", "profiles", "orders", "products", "posts", "accounts"):
            if noun in text:
                return noun
        return "users"

    @staticmethod
    def _guess_screen(text: str) -> str:
        m = re.search(r"\b([a-z_][a-z0-9_]*)\s+(?:screen|page|view)\b", text)
        if m:
            return f"{m.group(1)}_screen"
        for noun in ("profile", "login", "settings", "home", "signup", "checkout"):
            if noun in text:
                return f"{noun}_screen"
        return "profile_screen"

    # -- LIVE (claude -p) --------------------------------------------------- #
    def _refine_live(self, raw_input: str) -> Optional[Dict[str, object]]:
        prompt = self._build_prompt(raw_input)
        try:
            proc = subprocess.run(
                ["claude", "-p", prompt],
                capture_output=True,
                text=True,
                timeout=120,
            )
        except FileNotFoundError:
            _console.print("[yellow]WARN[/yellow] `claude` binary not found for live refine")
            return None
        except subprocess.TimeoutExpired:
            _console.print("[yellow]WARN[/yellow] live refine timed out")
            return None
        except (OSError, ValueError) as exc:
            _console.print(f"[yellow]WARN[/yellow] live refine subprocess error: {exc}")
            return None

        if proc.returncode != 0:
            _console.print(
                f"[yellow]WARN[/yellow] live refine rc={proc.returncode}: "
                f"{(proc.stderr or '').strip()[:200]}"
            )
            return None

        obj = _extract_first_json(proc.stdout or "")
        if obj is None:
            _console.print("[yellow]WARN[/yellow] live refine produced no JSON object")
            return None
        try:
            self._validate(obj)
        except ValueError as exc:
            _console.print(f"[yellow]WARN[/yellow] live payload invalid: {exc}")
            return None
        return obj

    @staticmethod
    def _build_prompt(raw_input: str) -> str:
        schema_str = json.dumps(PAYLOAD_SCHEMA, indent=2)
        return (
            "You are a semantic gateway for a Laravel + Flutter SaaS orchestrator.\n"
            "Convert the human instruction into a SINGLE JSON object and OUTPUT ONLY "
            "that JSON object — no prose, no markdown fences.\n"
            "It MUST conform to this JSON Schema:\n"
            f"{schema_str}\n\n"
            "Rules: target_stack is exactly one of Laravel, Flutter, Both. "
            "database_mutations lists tables and their column changes "
            "(field type is a Laravel/DB type like string, integer, boolean, text). "
            "ui_changes lists affected Flutter screens and their widgets.\n\n"
            f"Human instruction:\n{raw_input}\n"
        )


# --------------------------------------------------------------------------- #
# Selftest (offline)
# --------------------------------------------------------------------------- #
def _selftest() -> bool:
    ok = True
    try:
        gw = TranslatorGateway(live=False)
        payload = gw.refine(
            "add phone_number to users table and show it on the profile screen"
        )

        assert payload["target_stack"] == "Both", f"expected Both, got {payload['target_stack']}"

        muts = payload["database_mutations"]
        assert isinstance(muts, list) and muts, "expected at least one database mutation"
        users_mut = next((m for m in muts if m["table"] == "users"), None)
        assert users_mut is not None, "expected a users-table mutation"
        field_names = {f["name"] for f in users_mut["fields"]}
        assert "phone_number" in field_names, f"expected phone_number field, got {field_names}"

        ui = payload["ui_changes"]
        assert isinstance(ui, list) and ui, "expected at least one ui_change"
        assert ui[0]["screen"] == "profile_screen", f"expected profile_screen, got {ui[0]['screen']}"

        # Determinism: same input → identical payload.
        again = gw.refine(
            "add phone_number to users table and show it on the profile screen"
        )
        assert again == payload, "MOCK refine must be deterministic"

        # A pure-backend instruction must not be Flutter.
        backend_only = gw.refine("create a migration to add an index on the orders table")
        assert backend_only["target_stack"] == "Laravel", "backend-only must be Laravel"

        # Invalid payloads must be rejected by the validator.
        raised = False
        try:
            TranslatorGateway._validate({"intent": "x", "target_stack": "Nope",
                                         "database_mutations": [], "ui_changes": []})
        except ValueError:
            raised = True
        assert raised, "validator must reject a bad target_stack"
    except AssertionError as exc:
        ok = False
        _console.print(f"[red]assertion failed:[/red] {exc}")
    except Exception as exc:  # noqa: BLE001
        ok = False
        _console.print(f"[red]unexpected error:[/red] {exc}")

    _console.print("[bold green]PASS[/bold green] translator_gateway selftest" if ok else "[bold red]FAIL[/bold red] translator_gateway selftest")
    return ok


if __name__ == "__main__":
    import sys

    sys.exit(0 if _selftest() else 1)
