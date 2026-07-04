#!/usr/bin/env python3
"""
role:    security-compliance-architect
purpose: generate a STRIDE threat-model skeleton for a feature so no surface is
         skipped; security author fills the mitigations. Writes inside the project
         (sandboxed) or to stdout.
gate:    3
inputs:  <feature-name> [--prj PRJ-ID] [--out docs/<file>.md]
outputs: a STRIDE markdown skeleton (stdout, or a file inside the project)
exit:    0 ok · 2 bad args · 3 governance (write outside project)
"""
import sys
import pathlib

_p = pathlib.Path(__file__).resolve()
for _up in _p.parents:
    if (_up / "sofi_tools").is_dir():
        sys.path.insert(0, str(_up))
        break
from sofi_tools import paths, guard  # noqa: E402

_STRIDE = [
    ("Spoofing", "identity — can an actor pretend to be someone else?"),
    ("Tampering", "integrity — can data/requests be modified in transit or at rest?"),
    ("Repudiation", "non-repudiation — can an action be denied? are events logged?"),
    ("Information Disclosure", "confidentiality — can data leak (enumeration, errors, PII)?"),
    ("Denial of Service", "availability — can the surface be exhausted or flooded?"),
    ("Elevation of Privilege", "authorization — can a low-priv actor gain higher rights?"),
]


def render(feature: str) -> str:
    lines = [
        f"# Threat Model — {feature} (STRIDE)",
        "Route: opus · max (security never compressed). Fill each mitigation; no row left blank.",
        "",
        "## Assets",
        "- (list the data/endpoints/secrets this feature touches)",
        "",
        "## STRIDE findings",
    ]
    for name, q in _STRIDE:
        lines += [f"### {name}", f"- question: {q}",
                  "- threat: (describe)", "- mitigation: (REQUIRED — design the control)",
                  "- severity: (low/med/high)", ""]
    lines += [
        "## PII / compliance",
        "- data classified: (none / list). retention + consent if PII present.",
        "",
        "## Pen-test scope",
        "- (enumerate the highest-severity controls to test)",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    args = list(argv)
    out = prj = None
    feature_parts = []
    i = 0
    while i < len(args):
        if args[i] == "--prj":
            prj = args[i + 1]; i += 2
        elif args[i] == "--out":
            out = args[i + 1]; i += 2
        else:
            feature_parts.append(args[i]); i += 1
    if not feature_parts:
        print("usage: stride_scaffold.py <feature-name> [--prj PRJ-ID] [--out docs/<file>.md]",
              file=sys.stderr)
        return 2
    feature = " ".join(feature_parts)
    text = render(feature)

    if out:
        if not prj:
            print("✗ --out requires --prj (writes are sandboxed to a project)", file=sys.stderr)
            return 2
        target = paths.project_dir(prj) / out
        try:
            guard.assert_within_project(target, prj)
        except guard.GovernanceError as e:
            print(f"✗ GOVERNANCE: {e}", file=sys.stderr)
            return 3
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        print(f"✓ wrote {target.relative_to(paths.repo_root())}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
