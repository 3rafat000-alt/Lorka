#!/usr/bin/env python3
"""
role:    <owning-role-shortname>        # e.g. backend-blade-engineer
purpose: <one line — what this proves or produces>
gate:    <gate number or 'all'>
inputs:  <args this takes>
outputs: <what it prints/writes>
exit:    0 ok · 1 a real failure CI can block on · 2 bad input · 3 governance

Copy this file to  company/os/agents/<family>/<role>/<name>.py , fill the header,
register the row in registry.yaml, and log the promotion in DECISIONS.md.
Rules: GOVERNANCE.md. Writes are sandboxed via guard. No secrets. Deterministic.
"""
import sys
import pathlib

# depth-agnostic bootstrap: find the shared library on the path.
_p = pathlib.Path(__file__).resolve()
for _up in _p.parents:
    if (_up / "sofi_tools").is_dir():
        sys.path.insert(0, str(_up))
        break
from sofi_tools import paths, brain, tickets, routing, gates, guard, runlog  # noqa: E402,F401


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: <name>.py <args>", file=sys.stderr)
        return 2

    # --- do the work here ---
    # Read the brain first (universal contract):
    #     prj = argv[0]; state = brain.read_state(prj)
    # Writes must be sandboxed:
    #     guard.assert_within_project(target, prj)
    # If you mutate state, log it:
    #     runlog.log(prj, role="<role>", action="<what>", when="<date-from-CEO>")

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
