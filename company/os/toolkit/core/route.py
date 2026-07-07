#!/usr/bin/env python3
"""
role:    ceo-sofi
purpose: print the cheapest clearing route (model·effort·caveman) for a role,
         applying the priority override, so the CEO logs an exact route per turn.
gate:    all
inputs:  <role> [PRIORITY]   e.g. data-schema-engineer CRITICAL
outputs: one route line to stdout
exit:    0 ok · 2 unknown role
"""
import sys
import pathlib

_p = pathlib.Path(__file__).resolve()
for _up in _p.parents:
    if (_up / "sofi_tools").is_dir():
        sys.path.insert(0, str(_up))
        break
from sofi_tools import routing  # noqa: E402


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: route.py <role> [PRIORITY]", file=sys.stderr)
        return 2
    role = argv[0]
    priority = argv[1] if len(argv) > 1 else None
    try:
        r = routing.route_for(role, priority)
    except KeyError as e:
        print(f"✗ {e}", file=sys.stderr)
        return 2
    print(f"route: {r['model']} · {r['effort']} · {r['caveman']}  "
          f"({r['tier']} {r['model_id']} | gate {r['gate']} | budget {r['budget']} | prio {r['priority']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
