"""SOFI tools — shared contract every room tool implements.

A Tool is a small, deterministic, typed capability a room agent can call. It
validates its params against an input schema, does one bounded thing, writes any
output as an artifact under .sofi/artifacts/<room>/, and returns a ToolResult.

Room tool modules live in tools/rooms/<room>.py and expose:  TOOLS = [ClassA, ...]
(each a Tool subclass). room_manager discovers them; tool_runner is the CLI.

Stdlib-first. Uses `jsonschema` for param validation when installed, else a
minimal built-in check. Tools may also call the in-session substrate under
.claude/engine/tooling/ via call_substrate() — the two layers compose.
"""
from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Repo root: tools/tool_base.py -> parents[1]. SOFI_HOME overrides (used by tests).
REPO_ROOT: Path = Path(os.environ.get("SOFI_HOME") or Path(__file__).resolve().parents[1])
ARTIFACTS_DIR: Path = REPO_ROOT / ".sofi" / "artifacts"
SUBSTRATE_DIR: Path = REPO_ROOT / ".claude" / "engine" / "tooling"

try:  # optional, present in this env; graceful fallback otherwise
    import jsonschema as _jsonschema  # type: ignore
except Exception:  # pragma: no cover
    _jsonschema = None


@dataclass
class ToolResult:
    """Uniform return shape for every tool."""
    ok: bool
    output: Any = None
    error: Optional[str] = None
    artifacts: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "output": self.output,
            "error": self.error,
            "artifacts": self.artifacts,
        }


def _minimal_validate(schema: Dict[str, Any], data: Any, path: str = "") -> List[str]:
    """Tiny draft-07 subset validator used when jsonschema is unavailable.

    Supports: type, required, properties, items, enum, minLength, minItems.
    Returns a list of human-readable error strings (empty == valid).
    """
    errs: List[str] = []
    t = schema.get("type")
    _PY = {
        "object": dict, "array": list, "string": str,
        "number": (int, float), "integer": int, "boolean": bool, "null": type(None),
    }
    if t:
        types = t if isinstance(t, list) else [t]
        ok = False
        for one in types:
            py = _PY.get(one)
            if py is None:
                ok = True
                break
            if one in ("integer", "number") and isinstance(data, bool):
                continue  # bool is not a number here
            if isinstance(data, py):
                ok = True
                break
        if not ok:
            errs.append(f"{path or 'value'}: expected {t}, got {type(data).__name__}")
            return errs
    if isinstance(data, dict):
        for req in schema.get("required", []):
            if req not in data:
                errs.append(f"{path + '.' if path else ''}{req}: required")
        for key, sub in schema.get("properties", {}).items():
            if key in data:
                errs.extend(_minimal_validate(sub, data[key], f"{path + '.' if path else ''}{key}"))
    if isinstance(data, list):
        if "minItems" in schema and len(data) < schema["minItems"]:
            errs.append(f"{path or 'value'}: needs >= {schema['minItems']} items")
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(data):
                errs.extend(_minimal_validate(item_schema, item, f"{path}[{i}]"))
    if isinstance(data, str):
        if "minLength" in schema and len(data) < schema["minLength"]:
            errs.append(f"{path or 'value'}: shorter than {schema['minLength']}")
    if "enum" in schema and data not in schema["enum"]:
        errs.append(f"{path or 'value'}: must be one of {schema['enum']}")
    return errs


class Tool(ABC):
    """Base class for every room tool."""

    name: str = ""                       # unique dotted id, e.g. "bkd.make_migration"
    room: str = ""                       # room code, e.g. "BKD-05"
    summary: str = ""                    # one-line description
    input_schema: Dict[str, Any] = {}    # JSON-schema (draft-07 subset) for params

    # -- metadata --------------------------------------------------------
    @classmethod
    def spec(cls) -> Dict[str, Any]:
        return {
            "name": cls.name,
            "room": cls.room,
            "summary": cls.summary,
            "input_schema": cls.input_schema,
        }

    # -- validation ------------------------------------------------------
    def validate(self, params: Dict[str, Any]) -> Optional[str]:
        """Return an error string if params are invalid, else None."""
        if not self.input_schema:
            return None
        if _jsonschema is not None:
            try:
                _jsonschema.validate(instance=params, schema=self.input_schema)
                return None
            except _jsonschema.ValidationError as exc:  # type: ignore
                return f"{'/'.join(str(p) for p in exc.path) or 'params'}: {exc.message}"
        errs = _minimal_validate(self.input_schema, params)
        return "; ".join(errs) if errs else None

    # -- execution entry point (validates, then calls run) ---------------
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        err = self.validate(params)
        if err:
            return ToolResult(ok=False, error=f"invalid params: {err}")
        try:
            return self.run(params)
        except Exception as exc:  # never leak a traceback to the caller
            return ToolResult(ok=False, error=f"{type(exc).__name__}: {exc}")

    @abstractmethod
    def run(self, params: Dict[str, Any]) -> ToolResult:
        """Do the one bounded thing. Implemented by each concrete tool."""
        raise NotImplementedError

    # -- helpers ---------------------------------------------------------
    def _artifact_dir(self) -> Path:
        d = ARTIFACTS_DIR / (self.room or "misc")
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _write_artifact(self, relpath: str, content: str) -> str:
        """Write text under .sofi/artifacts/<room>/relpath (atomic). Return abs path."""
        dest = self._artifact_dir() / relpath
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(dest.suffix + ".tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, dest)
        return str(dest)

    @staticmethod
    def _sh(cmd: Any, cwd: Optional[str] = None, timeout: int = 300) -> Tuple[int, str, str]:
        """Run a subprocess (list or string). Return (returncode, stdout, stderr)."""
        args = cmd if isinstance(cmd, list) else shlex.split(cmd)
        try:
            proc = subprocess.run(
                args, cwd=cwd, capture_output=True, text=True, timeout=timeout,
            )
            return proc.returncode, proc.stdout, proc.stderr
        except FileNotFoundError as exc:
            return 127, "", f"command not found: {exc}"
        except subprocess.TimeoutExpired:
            return 124, "", f"timeout after {timeout}s"

    @staticmethod
    def call_substrate(tool: str, args: List[str]) -> Dict[str, Any]:
        """Invoke an in-session substrate tool (.claude/engine/tooling/<tool>.py --json).

        Returns the parsed JSON dict, or {"ok": False, "error": ...} on failure.
        Lets a room tool reuse registry/validate/check/gitflow without duplicating them.
        """
        path = SUBSTRATE_DIR / f"{tool}.py"
        if not path.exists():
            return {"ok": False, "error": f"substrate tool not found: {tool}"}
        rc, out, err = Tool._sh([sys.executable, str(path), *args, "--json"])
        try:
            return json.loads(out) if out.strip() else {"ok": rc == 0, "error": err or None}
        except json.JSONDecodeError:
            return {"ok": rc == 0, "raw": out, "error": err or None}
