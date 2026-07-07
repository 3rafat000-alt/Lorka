#!/usr/bin/env python3
"""
role:    principal-system-architect
purpose: turn a small SOFI topology spec into an importable FossFLOW / Isoflow
         isometric-diagram model — so the architecture diagram is generated,
         version-controlled, and traceable to the stack (Design is Truth).
gate:    3
inputs:  <topology.json | ->   spec with {title, nodes[], connectors[]}; '-' = stdin
         [outfile.json]        optional; default prints model JSON to stdout
outputs: a FossFLOW model JSON (import via the app's "Open / Import")
exit:    0 ok · 2 bad input/spec

Topology spec shape:
  {
    "title": "PRJ-0001 Architecture",
    "nodes": [ {"id":"api","label":"Laravel API","type":"server"}, ... ],
    "connectors": [ {"from":"web","to":"api","label":"HTTPS/JSON"}, ... ]
  }
node.type ∈ client|server|database|cache|queue|service|user|external|block (default block)

Rules: GOVERNANCE.md — stdlib only, deterministic, no secrets, no network.
"""
from __future__ import annotations

import json
import math
import sys
import pathlib

_p = pathlib.Path(__file__).resolve()
for _up in _p.parents:
    if (_up / "sofi_tools").is_dir():
        sys.path.insert(0, str(_up))
        break

# node type → (isoflow icon id, SOFI/Google-palette color id)
_TYPE = {
    "client":   ("browser",  "blue"),
    "web":      ("browser",  "blue"),
    "frontend": ("browser",  "blue"),
    "server":   ("server",   "blue"),
    "api":      ("server",   "blue"),
    "backend":  ("server",   "blue"),
    "service":  ("server",   "blue"),
    "database": ("storage",  "green"),
    "db":       ("storage",  "green"),
    "cache":    ("block",    "yellow"),
    "queue":    ("block",    "red"),
    "broker":   ("block",    "red"),
    "user":     ("user",     "green"),
    "external": ("cloud",    "yellow"),
    "block":    ("block",    "blue"),
}
_COLORS = [
    {"id": "blue",   "value": "#4285f4"},
    {"id": "red",    "value": "#ea4335"},
    {"id": "green",  "value": "#34a853"},
    {"id": "yellow", "value": "#fbbc05"},
]


def _fail(msg: str) -> int:
    print(f"✗ {msg}", file=sys.stderr)
    return 2


def build_model(spec: dict) -> dict:
    nodes = spec.get("nodes") or []
    conns = spec.get("connectors") or []
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("spec.nodes must be a non-empty list")

    ids = {n.get("id") for n in nodes}
    used_icons: dict[str, str] = {}
    items, placed = [], []
    cols = max(1, math.ceil(math.sqrt(len(nodes))))

    for i, n in enumerate(nodes):
        nid = n.get("id")
        if not nid:
            raise ValueError(f"node #{i} missing 'id'")
        icon, _color = _TYPE.get((n.get("type") or "block").lower(), _TYPE["block"])
        used_icons[icon] = icon
        items.append({
            "id": nid,
            "name": n.get("label", nid),
            "icon": icon,
            "description": n.get("description", ""),
        })
        placed.append({
            "id": nid,
            "tile": {"x": (i % cols) - cols // 2, "y": (i // cols)},
        })

    connectors = []
    for j, c in enumerate(conns):
        a, b = c.get("from"), c.get("to")
        if a not in ids or b not in ids:
            raise ValueError(f"connector #{j} references unknown node: {a!r}→{b!r}")
        connectors.append({
            "id": f"c{j+1}",
            "color": "blue",
            "width": 10,
            "description": c.get("label", ""),
            "anchors": [
                {"id": f"c{j+1}a1", "ref": {"item": a}},
                {"id": f"c{j+1}a2", "ref": {"item": b}},
            ],
        })

    return {
        "version": "1.0",
        "title": spec.get("title", "SOFI Architecture"),
        "icons": [{"id": k, "name": k, "collection": "isoflow"} for k in sorted(used_icons)],
        "colors": _COLORS,
        "items": items,
        "views": [{
            "id": "view-main",
            "name": "Main",
            "items": placed,
            "connectors": connectors,
            "rectangles": [],
            "textBoxes": [],
        }],
    }


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: fossflow_export.py <topology.json|-> [outfile.json]", file=sys.stderr)
        return 2
    src = argv[0]
    try:
        raw = sys.stdin.read() if src == "-" else pathlib.Path(src).read_text(encoding="utf-8")
    except OSError as e:
        return _fail(f"cannot read {src}: {e}")
    try:
        spec = json.loads(raw)
    except json.JSONDecodeError as e:
        return _fail(f"invalid JSON in topology: {e}")
    try:
        model = build_model(spec)
    except (ValueError, AttributeError, TypeError) as e:
        return _fail(f"bad spec: {e}")

    out = json.dumps(model, ensure_ascii=False, indent=2)
    if len(argv) > 1:
        dest = pathlib.Path(argv[1])
        dest.write_text(out + "\n", encoding="utf-8")
        print(f"✓ {len(model['items'])} nodes · {len(model['views'][0]['connectors'])} "
              f"connectors → {dest}  (import in FossFLOW)")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
