"""DAT-07 — Data / Behavioral Analytics room tools.

Two capabilities:
  * dat.event_schema — emit a tracking-event schema (Mixpanel/GA4-style).
  * dat.funnel_spec  — emit a funnel definition (ordered steps + window).

Stdlib + tools.tool_base only. No import-time side effects.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from tools.tool_base import Tool, ToolResult


# --- module-private slug helpers -------------------------------------------
def _slug(text: str, sep: str) -> str:
    """Lowercase slug: split camelCase, collapse non-alnum runs to `sep`."""
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", text or "")
    parts = re.findall(r"[0-9A-Za-z]+", text)
    return sep.join(p.lower() for p in parts)


def kebab(text: str) -> str:
    return _slug(text, "-")


def snake(text: str) -> str:
    return _slug(text, "_")


# --- dat.event_schema ------------------------------------------------------
class EventSchemaTool(Tool):
    name = "dat.event_schema"
    room = "DAT-07"
    summary = "Generate a tracking-event schema (Mixpanel/GA4-style) with typed properties."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": ["event", "props"],
        "properties": {
            "event": {"type": "string", "minLength": 1},
            "props": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["name", "type"],
                    "properties": {
                        "name": {"type": "string", "minLength": 1},
                        "type": {"type": "string", "minLength": 1},
                    },
                },
            },
        },
    }

    def run(self, params: Dict[str, Any]) -> ToolResult:
        event = params["event"]
        props = params["props"]

        seen: set = set()
        properties: List[Dict[str, Any]] = []
        for p in props:
            pname = str(p["name"]).strip()
            if not pname:
                return ToolResult(ok=False, error="property with empty name")
            if pname in seen:
                return ToolResult(ok=False, error=f"duplicate property: {pname}")
            seen.add(pname)
            properties.append({"name": pname, "type": str(p["type"]), "required": True})

        schema = {"event": event, "properties": properties, "version": 1}
        content = json.dumps(schema, indent=2, ensure_ascii=False) + "\n"
        base = snake(event) or "event"
        path = self._write_artifact(f"events/{base}.json", content)
        return ToolResult(
            ok=True,
            output={"path": path, "event": event, "props": len(properties)},
            artifacts=[path],
        )


# --- dat.funnel_spec -------------------------------------------------------
class FunnelSpecTool(Tool):
    name = "dat.funnel_spec"
    room = "DAT-07"
    summary = "Generate a funnel definition (ordered steps + conversion window)."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": ["name", "steps"],
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "steps": {
                "type": "array",
                "minItems": 1,
                "items": {"type": "string", "minLength": 1},
            },
        },
    }

    def run(self, params: Dict[str, Any]) -> ToolResult:
        name = params["name"]
        raw_steps = params["steps"]

        steps: List[Dict[str, Any]] = []
        for i, step in enumerate(raw_steps, start=1):
            event = str(step).strip()
            if not event:
                return ToolResult(ok=False, error=f"empty step at position {i}")
            steps.append({"order": i, "event": event})

        if not steps:
            return ToolResult(ok=False, error="funnel needs at least one step")

        funnel = {"name": name, "steps": steps, "window_days": 7}
        content = json.dumps(funnel, indent=2, ensure_ascii=False) + "\n"
        base = kebab(name) or "funnel"
        path = self._write_artifact(f"funnels/{base}.json", content)
        return ToolResult(
            ok=True,
            output={"path": path, "name": name, "steps": len(steps)},
            artifacts=[path],
        )


TOOLS: List[type] = [EventSchemaTool, FunnelSpecTool]

SELFTEST_SAMPLES: Dict[str, Dict[str, Any]] = {
    "dat.event_schema": {
        "event": "Order Completed",
        "props": [
            {"name": "order_id", "type": "string"},
            {"name": "total", "type": "number"},
        ],
    },
    "dat.funnel_spec": {
        "name": "Checkout Funnel",
        "steps": ["view_cart", "begin_checkout", "purchase"],
    },
}
