#!/usr/bin/env python3
"""
role:    qa-sre-lead
purpose: enforce the >=90% coverage bar — fail the build below it. Accepts a raw
         percentage or a coverage.xml (Cobertura/Clover line-rate).
gate:    5
inputs:  <value-or-coverage.xml> [--min 90]
outputs: pass/fail line
exit:    0 meets bar · 1 below bar · 2 bad input
"""
import re
import sys
import pathlib

_p = pathlib.Path(__file__).resolve()
for _up in _p.parents:
    if (_up / "sofi_tools").is_dir():
        sys.path.insert(0, str(_up))
        break


def _from_xml(path: pathlib.Path) -> float | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r'line-rate="([0-9.]+)"', text)        # Cobertura
    if m:
        return float(m.group(1)) * 100
    cov = re.search(r'coveredstatements="(\d+)"', text)   # Clover
    tot = re.search(r'statements="(\d+)"', text)
    if cov and tot and int(tot.group(1)) > 0:
        return int(cov.group(1)) / int(tot.group(1)) * 100
    return None


def main(argv: list[str]) -> int:
    args = list(argv)
    minimum = 90.0
    if "--min" in args:
        idx = args.index("--min")
        minimum = float(args[idx + 1])
        del args[idx:idx + 2]
    if not args:
        print("usage: coverage_gate.py <pct|coverage.xml> [--min 90]", file=sys.stderr)
        return 2
    arg = args[0]
    p = pathlib.Path(arg)
    if p.exists():
        pct = _from_xml(p)
        if pct is None:
            print(f"✗ could not read coverage from {p}", file=sys.stderr)
            return 2
    else:
        try:
            pct = float(arg.rstrip("%"))
        except ValueError:
            print(f"✗ not a number or file: {arg}", file=sys.stderr)
            return 2
    ok = pct >= minimum
    print(f"coverage {pct:.1f}% vs bar {minimum:.0f}% → {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
