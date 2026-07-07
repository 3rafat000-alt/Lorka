#!/usr/bin/env python3
"""
role:    ceo-sofi
purpose: render the RUNBOOK §2 delegation prompt for a project's next open ticket,
         so spawning an agent is one copy-paste that arrives fully oriented.
gate:    all
inputs:  <PRJ-ID> [role]   (role defaults to the open ticket's `to:`)
outputs: the delegation prompt to stdout
exit:    0 ok · 1 no open ticket · 2 no such project
"""
import sys
import pathlib

_p = pathlib.Path(__file__).resolve()
for _up in _p.parents:
    if (_up / "sofi_tools").is_dir():
        sys.path.insert(0, str(_up))
        break
from sofi_tools import paths, tickets, routing  # noqa: E402

SPEC_PATH = {
    "chief-product-strategist": "tier-0-strategy/chief-product-strategist",
    "ux-researcher": "tier-0-strategy/ux-researcher",
    "journey-architect": "tier-0-strategy/journey-architect",
    "ui-ux-designer": "tier-0-strategy/ui-ux-designer",
    "content-strategist": "tier-0-strategy/content-strategist",
    "principal-system-architect": "tier-1-architecture/principal-system-architect",
    "data-schema-engineer": "tier-1-architecture/data-schema-engineer",
    "api-integration-specialist": "tier-1-architecture/api-integration-specialist",
    "security-compliance-architect": "tier-1-architecture/security-compliance-architect",
    "qa-sre-lead": "tier-3-quality/qa-sre-lead",
    "observability-sre": "tier-4-infrastructure/observability-sre",
}


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: dispatch.py <PRJ-ID> [role]", file=sys.stderr)
        return 2
    prj = argv[0]
    if not paths.project_exists(prj):
        print(f"✗ no such project: {prj}", file=sys.stderr)
        return 2
    t = tickets.next_open(prj)
    if t is None:
        print("(no open ticket to dispatch)")
        return 1
    role = argv[1] if len(argv) > 1 else t.to
    spec = SPEC_PATH.get(role, f"<find-spec-for-{role}>")
    try:
        route = routing.format_route(role)
    except KeyError:
        route = "(set per routing.yaml)"
    print(f"""You are sofi-{role}. Project: {prj}.
BEFORE acting, read in order:
  - engine/protocols/00-operating-system.md
  - projects/{prj}/_context/STATE.md
  - projects/{prj}/_context/HANDOFFS.md   (your ticket: {t.id})
  - projects/{prj}/_context/CONTEXT.md
Spec + Operating Prompt: engine/agents/{spec}.md
Route: {route}.
Ticket task: {t.task or '(see ticket)'}
Expected artifact: {t.expected or '(see ticket)'}
Do the work loop. AFTER: write artifact, append CONTEXT, update STATE, write next ticket, mark {t.id} done.""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
