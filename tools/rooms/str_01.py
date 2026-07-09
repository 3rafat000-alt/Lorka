"""STR-01 — Strategy / Product room tools.

Deterministic capabilities for the strategy role:
  * str.draft_prd   — generate a PRD (Markdown).
  * str.define_okr  — generate an OKR block (Markdown + parallel JSON).

Stdlib-only besides tools.tool_base + typing. No import-time side effects.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from tools.tool_base import Tool, ToolResult

ROOM = "STR-01"


# -- module-private helpers ---------------------------------------------------
def _kebab(s: str) -> str:
    """lower-case, non-alphanumeric runs -> single hyphen, trimmed."""
    s = re.sub(r"[^0-9a-zA-Z]+", "-", str(s).strip().lower())
    return re.sub(r"-{2,}", "-", s).strip("-") or "untitled"


def _bullets(items: List[str], prefix: str = "- ") -> str:
    return "\n".join(f"{prefix}{str(i).strip()}" for i in items) or f"{prefix}_none_"


# -- tools --------------------------------------------------------------------
class DraftPrd(Tool):
    name = "str.draft_prd"
    room = ROOM
    summary = "Draft a Product Requirements Document (problem, goals, scope, metrics, open questions)."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": ["feature", "problem", "goals"],
        "properties": {
            "feature": {"type": "string", "minLength": 1},
            "problem": {"type": "string", "minLength": 1},
            "goals": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        },
    }

    def run(self, params: Dict[str, Any]) -> ToolResult:
        feature = params["feature"].strip()
        problem = params["problem"].strip()
        goals = [str(g).strip() for g in params["goals"] if str(g).strip()]
        if not goals:
            return ToolResult(ok=False, error="goals must contain at least one non-empty entry")

        metrics = [f"Progress toward: {g}" for g in goals]
        scope_out = [
            "Anything not explicitly listed under Scope — In.",
            "Adjacent features scheduled for a later milestone.",
            "Migrations of unrelated legacy data.",
        ]
        open_questions = [
            "Who is the primary persona and which journey stage does this serve?",
            "What is the rollout strategy (fast-track vs deep-audit)?",
            "What are the hard constraints (budget, deadline, compliance)?",
            "What is explicitly out of scope for v1?",
        ]

        lines: List[str] = [
            f"# PRD — {feature}",
            "",
            f"> Room {self.room} · Strategy / Product",
            "",
            "## Problem Statement",
            "",
            problem,
            "",
            "## Goals",
            "",
            _bullets(goals),
            "",
            "## Scope",
            "",
            "### In",
            "",
            _bullets(goals),
            "",
            "### Out",
            "",
            _bullets(scope_out),
            "",
            "## Success Metrics",
            "",
            _bullets(metrics),
            "",
            "## Open Questions",
            "",
            _bullets(open_questions),
            "",
        ]
        content = "\n".join(lines)
        rel = f"prd/{_kebab(feature)}.md"
        path = self._write_artifact(rel, content)

        return ToolResult(
            ok=True,
            output={"path": path, "feature": feature, "goals": len(goals)},
            artifacts=[path],
        )


class DefineOkr(Tool):
    name = "str.define_okr"
    room = ROOM
    summary = "Define an OKR (objective + key results) as parallel Markdown and JSON artifacts."
    input_schema: Dict[str, Any] = {
        "type": "object",
        "required": ["objective", "key_results"],
        "properties": {
            "objective": {"type": "string", "minLength": 1},
            "key_results": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        },
    }

    def run(self, params: Dict[str, Any]) -> ToolResult:
        objective = params["objective"].strip()
        krs = [str(k).strip() for k in params["key_results"] if str(k).strip()]
        if not krs:
            return ToolResult(ok=False, error="key_results must contain at least one non-empty entry")

        kr_records = [
            {"id": f"KR{i + 1}", "text": text, "progress": 0, "confidence": "medium"}
            for i, text in enumerate(krs)
        ]

        # Markdown artifact.
        md_lines: List[str] = [
            f"# OKR — {objective}",
            "",
            f"> Room {self.room} · Strategy / Product",
            "",
            "## Objective",
            "",
            objective,
            "",
            "## Key Results",
            "",
        ]
        for rec in kr_records:
            md_lines.append(f"- **{rec['id']}** — {rec['text']} _(progress: {rec['progress']}%)_")
        md_lines.append("")
        md_content = "\n".join(md_lines)

        # JSON artifact (parallel structured form).
        json_doc = {
            "objective": objective,
            "key_results": kr_records,
            "grading_scale": "0.0-1.0",
        }
        json_content = json.dumps(json_doc, indent=2) + "\n"

        slug = _kebab(objective)
        md_path = self._write_artifact(f"okr/{slug}.md", md_content)
        json_path = self._write_artifact(f"okr/{slug}.json", json_content)

        return ToolResult(
            ok=True,
            output={
                "objective": objective,
                "key_results": len(kr_records),
                "paths": [md_path, json_path],
            },
            artifacts=[md_path, json_path],
        )


TOOLS: List[type] = [DraftPrd, DefineOkr]

SELFTEST_SAMPLES: Dict[str, Dict[str, Any]] = {
    "str.draft_prd": {
        "feature": "Passwordless Login",
        "problem": "Users abandon signup because password creation adds friction.",
        "goals": ["Cut signup drop-off by 20%", "Support magic-link auth"],
    },
    "str.define_okr": {
        "objective": "Make onboarding effortless",
        "key_results": [
            "Reduce time-to-first-value to under 2 minutes",
            "Reach 60% activation within 7 days",
        ],
    },
}
