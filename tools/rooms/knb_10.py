"""KNB-10 — Knowledge / documentation room tools.

Numbered ADRs and Diataxis doc skeletons. Artifacts land under
.sofi/artifacts/KNB-10/. Stdlib + tools.tool_base + typing only. No import-time
side effects.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

from tools.tool_base import Tool, ToolResult

ROOM = "KNB-10"

_KEBAB_STRIP = re.compile(r"[^a-z0-9]+")
_KEBAB_DASH = re.compile(r"-+")


def kebab(text: str) -> str:
    """Lowercase, hyphenate, collapse — module-private slug helper."""
    s = _KEBAB_STRIP.sub("-", (text or "").strip().lower())
    s = _KEBAB_DASH.sub("-", s).strip("-")
    return s or "untitled"


# --------------------------------------------------------------------------- #
# ADR                                                                          #
# --------------------------------------------------------------------------- #
class AdrNew(Tool):
    name = "knb.adr_new"
    room = ROOM
    summary = "Generate a numbered Architecture Decision Record (ADR-NNNN)."
    input_schema = {
        "type": "object",
        "required": ["title", "context", "decision"],
        "properties": {
            "title": {"type": "string", "minLength": 1},
            "context": {"type": "string", "minLength": 1},
            "decision": {"type": "string", "minLength": 1},
            "consequences": {"type": "string"},
        },
    }

    def run(self, params: Dict[str, Any]) -> ToolResult:
        title = params["title"]
        context = params["context"]
        decision = params["decision"]
        consequences = params.get("consequences") or "_No consequences recorded yet._"

        adr_dir = self._artifact_dir() / "adr"
        existing = list(adr_dir.glob("ADR-*.md")) if adr_dir.exists() else []
        number = 1 + len(existing)
        num_str = f"{number:04d}"

        md = "\n".join([
            f"# ADR-{num_str}: {title}",
            "",
            "## Status",
            "",
            "Accepted",
            "",
            "## Context",
            "",
            context,
            "",
            "## Decision",
            "",
            decision,
            "",
            "## Consequences",
            "",
            consequences,
            "",
        ])

        relpath = f"adr/ADR-{num_str}-{kebab(title)}.md"
        path = self._write_artifact(relpath, md)
        return ToolResult(
            ok=True,
            output={"path": path, "number": number, "title": title},
            artifacts=[path],
        )


# --------------------------------------------------------------------------- #
# Diataxis doc scaffold                                                        #
# --------------------------------------------------------------------------- #
_DIATAXIS_KINDS = ["tutorial", "how-to", "reference", "explanation"]

# kind -> (one-line intent, [ (section heading, placeholder body) ])
_DIATAXIS: Dict[str, tuple] = {
    "tutorial": (
        "A learning-oriented, hands-on lesson that takes a newcomer end to end.",
        [
            ("Overview", "What you will build and the skill you will gain."),
            ("Prerequisites", "- Tools, accounts, and prior knowledge assumed."),
            ("Steps", "1. First concrete action.\n2. Next action.\n3. Final action."),
            ("What you learned", "Recap the capability the learner now has."),
            ("Next steps", "Point to a related how-to or reference."),
        ],
    ),
    "how-to": (
        "A task-oriented recipe that solves one real problem for someone who already knows the basics.",
        [
            ("Goal", "The single outcome this guide achieves."),
            ("Prerequisites", "- Preconditions that must already be true."),
            ("Steps", "1. Do this.\n2. Then this.\n3. Confirm the result."),
            ("Verify", "How to check the task succeeded."),
            ("Troubleshooting", "Common failure and its fix."),
        ],
    ),
    "reference": (
        "Information-oriented, dry, and exhaustive — a description of the machinery.",
        [
            ("Summary", "One-line description of the thing."),
            ("Synopsis", "```\nsignature or usage line\n```"),
            ("Parameters", "| Name | Type | Required | Description |\n| --- | --- | --- | --- |\n| — | — | — | — |"),
            ("Returns", "What it produces and under which conditions."),
            ("Examples", "```\nminimal example\n```"),
            ("See also", "- Related reference or explanation."),
        ],
    ),
    "explanation": (
        "Understanding-oriented discussion that illuminates the why behind the design.",
        [
            ("Context", "The situation and forces at play."),
            ("Background", "History and prior art relevant to the decision."),
            ("Discussion", "The reasoning, alternatives weighed, and rationale."),
            ("Trade-offs", "- What was gained and what was given up."),
            ("Further reading", "- Deeper sources and related decisions."),
        ],
    ),
}


class DocScaffold(Tool):
    name = "knb.doc_scaffold"
    room = ROOM
    summary = "Generate a Diataxis documentation skeleton (tutorial/how-to/reference/explanation)."
    input_schema = {
        "type": "object",
        "required": ["feature"],
        "properties": {
            "feature": {"type": "string", "minLength": 1},
            "kind": {"type": "string", "enum": _DIATAXIS_KINDS},
        },
    }

    def run(self, params: Dict[str, Any]) -> ToolResult:
        feature = params["feature"]
        kind = params.get("kind") or "how-to"
        intent, sections = _DIATAXIS[kind]

        lines: List[str] = [
            f"# {feature}",
            "",
            f"> **Diataxis type:** {kind} — {intent}",
            "",
        ]
        for heading, body in sections:
            lines.append(f"## {heading}")
            lines.append("")
            lines.append(body)
            lines.append("")

        md = "\n".join(lines)
        relpath = f"docs/{kind}/{kebab(feature)}.md"
        path = self._write_artifact(relpath, md)
        return ToolResult(
            ok=True,
            output={"path": path, "feature": feature, "kind": kind},
            artifacts=[path],
        )


TOOLS: List[type] = [AdrNew, DocScaffold]

SELFTEST_SAMPLES: Dict[str, Dict[str, Any]] = {
    "knb.adr_new": {
        "title": "Adopt PostgreSQL over MySQL",
        "context": "We need JSONB and strong indexing for the analytics workload.",
        "decision": "Standardize on PostgreSQL 16 for all new services.",
        "consequences": "Team must learn PG operational tooling; gains JSONB and CTEs.",
    },
    "knb.doc_scaffold": {"feature": "Configure SSO", "kind": "how-to"},
}
