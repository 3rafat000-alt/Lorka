"""UXR-02 — UX Research room tools.

Deterministic capabilities for the UX-research role:
  * uxr.persona          — generate an evidence-shaped persona (Markdown).
  * uxr.survey_scaffold  — generate an unbiased survey scaffold (JSON).

Stdlib-only besides tools.tool_base + typing. No import-time side effects.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from tools.tool_base import Tool, ToolResult

ROOM = "UXR-02"

# A question is kept "open" only when it is a short interrogative; otherwise a
# 1-5 scale item. Threshold is fixed so output is deterministic.
_SHORT_WORD_LIMIT = 12


# -- module-private helpers ---------------------------------------------------
def _kebab(s: str) -> str:
    """lower-case, non-alphanumeric runs -> single hyphen, trimmed."""
    s = re.sub(r"[^0-9a-zA-Z]+", "-", str(s).strip().lower())
    return re.sub(r"-{2,}", "-", s).strip("-") or "untitled"


def _bullets(items: List[str], prefix: str = "- ") -> str:
    return "\n".join(f"{prefix}{str(i).strip()}" for i in items) or f"{prefix}_none_"


def _infer_type(text: str) -> str:
    """Short interrogative -> open; everything else -> scale_1_5."""
    t = text.strip()
    if t.endswith("?") and len(t.split()) <= _SHORT_WORD_LIMIT:
        return "open"
    return "scale_1_5"


# -- tools --------------------------------------------------------------------
class Persona(Tool):
    name = "uxr.persona"
    room = ROOM
    summary = "Generate a UX persona (JTBD, pains, gains, scenario) as Markdown."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": ["name", "jtbd", "pains"],
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "jtbd": {"type": "string", "minLength": 1},
            "pains": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            "gains": {"type": "array", "items": {"type": "string"}},
        },
    }

    def run(self, params: Dict[str, Any]) -> ToolResult:
        name = params["name"].strip()
        jtbd = params["jtbd"].strip()
        pains = [str(p).strip() for p in params["pains"] if str(p).strip()]
        gains = [str(g).strip() for g in (params.get("gains") or []) if str(g).strip()]
        if not pains:
            return ToolResult(ok=False, error="pains must contain at least one non-empty entry")

        first_pain = pains[0]
        scenario = (
            f"{name} sits down to \"{jtbd}\". Today this is blocked by {first_pain.rstrip('.').lower()}. "
            f"When the job is done well, {name} moves on quickly and trusts the product to stay out of the way."
        )

        lines: List[str] = [
            f"# Persona — {name}",
            "",
            f"> Room {self.room} · UX Research",
            "",
            "## Job To Be Done (JTBD)",
            "",
            jtbd,
            "",
            "## Pains",
            "",
            _bullets(pains),
            "",
            "## Gains",
            "",
            _bullets(gains) if gains else "- _none captured yet_",
            "",
            "## Scenario",
            "",
            scenario,
            "",
        ]
        content = "\n".join(lines)
        rel = f"personas/{_kebab(name)}.md"
        path = self._write_artifact(rel, content)

        return ToolResult(
            ok=True,
            output={"path": path, "name": name},
            artifacts=[path],
        )


class SurveyScaffold(Tool):
    name = "uxr.survey_scaffold"
    room = ROOM
    summary = "Generate an unbiased survey scaffold (neutral questions, inferred type) as JSON."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": ["topic", "questions"],
        "properties": {
            "topic": {"type": "string", "minLength": 1},
            "questions": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        },
    }

    def run(self, params: Dict[str, Any]) -> ToolResult:
        topic = params["topic"].strip()
        raw = [str(q).strip() for q in params["questions"] if str(q).strip()]
        if not raw:
            return ToolResult(ok=False, error="questions must contain at least one non-empty entry")

        records = [
            {
                "id": f"q{i + 1}",
                "text": text,
                "type": _infer_type(text),
                "neutral": True,
            }
            for i, text in enumerate(raw)
        ]
        doc = {
            "topic": topic,
            "unbiased": True,
            "scales": {"scale_1_5": ["1", "2", "3", "4", "5"]},
            "questions": records,
        }
        content = json.dumps(doc, indent=2) + "\n"
        rel = f"surveys/{_kebab(topic)}.json"
        path = self._write_artifact(rel, content)

        return ToolResult(
            ok=True,
            output={"path": path, "topic": topic, "questions": len(records)},
            artifacts=[path],
        )


TOOLS: List[type] = [Persona, SurveyScaffold]

SELFTEST_SAMPLES: Dict[str, Dict[str, Any]] = {
    "uxr.persona": {
        "name": "Busy Bea",
        "jtbd": "check in for a flight from her phone in under a minute",
        "pains": ["Slow forms", "Too many steps"],
        "gains": ["Speed", "Confidence it worked"],
    },
    "uxr.survey_scaffold": {
        "topic": "Checkout Experience",
        "questions": [
            "How did that feel?",
            "The checkout process was easy to complete from start to finish without confusion.",
        ],
    },
}
