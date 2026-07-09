"""DSN-03 — Design System room tools.

Deterministic capabilities for the design-system role:
  * dsn.emit_token      — upsert a design token into a merged tokens.json store.
  * dsn.component_spec  — generate an all-states component spec (Markdown).

Stdlib-only besides tools.tool_base + typing. No import-time side effects.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from tools.tool_base import Tool, ToolResult

ROOM = "DSN-03"


# -- module-private helpers ---------------------------------------------------
def _kebab(s: str) -> str:
    """lower-case, non-alphanumeric runs -> single hyphen, trimmed."""
    s = re.sub(r"[^0-9a-zA-Z]+", "-", str(s).strip().lower())
    return re.sub(r"-{2,}", "-", s).strip("-") or "untitled"


# Default state palette when the caller does not name states explicitly.
_DEFAULT_STATES: List[str] = [
    "default", "hover", "focus", "active",
    "disabled", "loading", "error", "empty",
]

# Sensible appearance/behavior defaults per known state.
_STATE_DEFAULTS: Dict[str, Dict[str, str]] = {
    "default": {
        "appearance": "Resting appearance built from base tokens "
                      "(color.surface, type.body, space.md, radius.md).",
        "behavior": "Idle and ready; no interaction in progress.",
    },
    "hover": {
        "appearance": "Pointer-over treatment: shift background one step, cursor: pointer.",
        "behavior": "Entered on mouse-enter, reverts on mouse-leave; no-op on touch/keyboard.",
    },
    "focus": {
        "appearance": "Visible focus ring (2px, >=3:1 contrast) around the interactive bounds.",
        "behavior": "Entered via Tab or programmatic focus; the ring is never suppressed.",
    },
    "active": {
        "appearance": "Pressed treatment: inset shadow / darken one step to signal contact.",
        "behavior": "Held while pointer or Space/Enter is down; releases to hover or default.",
    },
    "disabled": {
        "appearance": "Muted, reduced-opacity surface, no shadow, cursor: not-allowed.",
        "behavior": "Non-interactive: aria-disabled=true, out of tab order, no events fire.",
    },
    "loading": {
        "appearance": "Spinner/skeleton replaces content; dimensions preserved (no layout shift).",
        "behavior": "Blocks further input and announces busy via aria-busy=true.",
    },
    "error": {
        "appearance": "Danger accent border/text (color.danger) plus an inline message slot.",
        "behavior": "Shown after a failed action/validation; message states what failed and how to fix it.",
    },
    "empty": {
        "appearance": "Empty-state illustration/copy with a primary call-to-action.",
        "behavior": "Shown when no data exists; offers the next step to populate content.",
    },
}


def _state_block(state: str) -> str:
    d = _STATE_DEFAULTS.get(
        state,
        {
            "appearance": f"Appearance for the '{state}' state, derived from base tokens "
                          f"with a distinct visual signal.",
            "behavior": f"Behavior for the '{state}' state; define entry/exit triggers "
                        f"and side effects.",
        },
    )
    return (
        f"### {state}\n\n"
        f"- **Appearance:** {d['appearance']}\n"
        f"- **Behavior:** {d['behavior']}\n"
    )


# -- tools --------------------------------------------------------------------
class EmitToken(Tool):
    name = "dsn.emit_token"
    room = ROOM
    summary = "Upsert a design token (category/name/value) into a merged tokens.json store."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": ["name", "value", "category"],
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "value": {"type": "string", "minLength": 1},
            "category": {
                "type": "string",
                "enum": ["color", "space", "type", "radius", "shadow", "motion"],
            },
        },
    }

    def run(self, params: Dict[str, Any]) -> ToolResult:
        name = params["name"]
        value = params["value"]
        category = params["category"]

        # Read the merged store if it already exists (json), else start fresh.
        store_path = self._artifact_dir() / "tokens.json"
        tokens: Dict[str, Dict[str, str]] = {}
        if store_path.exists():
            try:
                doc = json.loads(store_path.read_text(encoding="utf-8"))
                if isinstance(doc, dict) and isinstance(doc.get("tokens"), dict):
                    tokens = {
                        k: dict(v) for k, v in doc["tokens"].items() if isinstance(v, dict)
                    }
            except (json.JSONDecodeError, OSError):
                tokens = {}

        # Upsert tokens[category][name] = value.
        tokens.setdefault(category, {})
        tokens[category][name] = value
        total = sum(len(v) for v in tokens.values())

        doc = {"tokens": tokens, "total_tokens": total}
        path = self._write_artifact("tokens.json", json.dumps(doc, indent=2, sort_keys=True) + "\n")

        return ToolResult(
            ok=True,
            output={
                "category": category,
                "name": name,
                "value": value,
                "total_tokens": total,
            },
            artifacts=[path],
        )


class ComponentSpec(Tool):
    name = "dsn.component_spec"
    room = ROOM
    summary = "Generate an all-states Markdown component spec (appearance + behavior per state)."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": ["component"],
        "properties": {
            "component": {"type": "string", "minLength": 1},
            "states": {"type": "array", "items": {"type": "string"}},
        },
    }

    def run(self, params: Dict[str, Any]) -> ToolResult:
        component = params["component"].strip()
        states = params.get("states") or list(_DEFAULT_STATES)
        # Preserve order, drop empties/dupes deterministically.
        seen: set = set()
        clean_states: List[str] = []
        for s in states:
            key = str(s).strip()
            if key and key.lower() not in seen:
                seen.add(key.lower())
                clean_states.append(key)
        if not clean_states:
            clean_states = list(_DEFAULT_STATES)

        lines: List[str] = [
            f"# Component Spec — {component}",
            "",
            f"> Room {self.room} · Design System · covers **{len(clean_states)}** states.",
            "",
            "## Overview",
            "",
            f"`{component}` is a design-system component. Every state below is a first-class "
            "deliverable — no state may ship undefined. Values reference design tokens "
            "(color/space/type/radius/shadow/motion) from `tokens.json`.",
            "",
            "## States",
            "",
        ]
        for state in clean_states:
            lines.append(_state_block(state))

        lines += [
            "## Accessibility",
            "",
            "- Focus is always visible and never trapped.",
            "- Interactive targets are >=44x44px and keyboard-operable.",
            "- Error and loading states are announced to assistive tech.",
            "",
            "## Tokens referenced",
            "",
            "- color.* · space.* · type.* · radius.* · shadow.* · motion.*",
            "",
        ]
        content = "\n".join(lines)
        rel = f"components/{_kebab(component)}.md"
        path = self._write_artifact(rel, content)

        return ToolResult(
            ok=True,
            output={"path": path, "component": component, "states": len(clean_states)},
            artifacts=[path],
        )


TOOLS: List[type] = [EmitToken, ComponentSpec]

SELFTEST_SAMPLES: Dict[str, Dict[str, Any]] = {
    "dsn.emit_token": {"name": "primary", "value": "#3B5BFF", "category": "color"},
    "dsn.component_spec": {"component": "Primary Button", "states": ["default", "hover", "disabled"]},
}
