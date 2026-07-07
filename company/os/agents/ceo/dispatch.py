#!/usr/bin/env python3
"""
role:    brd-ceo (operated by gtw-dispatcher)
purpose: render the RUNBOOK §2 delegation prompt for a project's next open ticket,
         so spawning an agent is one copy-paste that arrives fully oriented.
gate:    all
inputs:  <PRJ-ID> [agent-id]   (defaults to the open ticket's `to:`)
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
from sofi_tools import paths, tickets, routing, registry  # noqa: E402


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: dispatch.py <PRJ-ID> [agent-id]", file=sys.stderr)
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
    # Spec path comes from the org index — no hardcoded roster (v6).
    spec = registry.spec_path(role) or f"<find-spec-for-{role} via `sofi registry {role}`>"
    try:
        route = routing.format_route(role)
    except KeyError:
        route = "(set per company/nexus/routing.yaml)"
    print(f"""You are {role}. Project: {prj}.
BEFORE acting, read in order:
  - company/constitution/00-operating-system.md
  - projects/{prj}/_context/STATE.md
  - projects/{prj}/_context/HANDOFFS.md   (your ticket: {t.id})
  - projects/{prj}/_context/CONTEXT.md
Spec + Operating Prompt: {spec}
Route: {route}.
Ticket task: {t.task or '(see ticket)'}
Expected artifact: {t.expected or '(see ticket)'}
Do the work loop. AFTER: write artifact, append CONTEXT, update STATE, write next ticket, mark {t.id} done.""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
