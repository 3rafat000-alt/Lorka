#!/usr/bin/env python3
"""
role:    performance-load-analyst
purpose: enforce the performance budget — fail when TTI>=2s or a Core Web Vital
         breaches threshold. Accepts metrics as flags or a JSON file.
gate:    5
inputs:  [--tti MS] [--lcp MS] [--inp MS] [--cls N] | <metrics.json>
outputs: per-metric pass/fail table
exit:    0 within budget · 1 budget breached · 2 bad input
"""
import json
import sys
import pathlib

_p = pathlib.Path(__file__).resolve()
for _up in _p.parents:
    if (_up / "sofi_tools").is_dir():
        sys.path.insert(0, str(_up))
        break

# Budget: (threshold, comparison "<" means lower is better, unit)
BUDGET = {
    "tti": (2000, "ms", "Time To Interactive"),
    "lcp": (2500, "ms", "Largest Contentful Paint"),
    "inp": (200,  "ms", "Interaction to Next Paint"),
    "cls": (0.1,  "",   "Cumulative Layout Shift"),
}


def parse(argv: list[str]) -> dict[str, float]:
    metrics: dict[str, float] = {}
    args = list(argv)
    # JSON file form
    if len(args) == 1 and pathlib.Path(args[0]).exists():
        data = json.loads(pathlib.Path(args[0]).read_text(encoding="utf-8"))
        for k in BUDGET:
            if k in data:
                metrics[k] = float(data[k])
        return metrics
    # flag form
    i = 0
    while i < len(args):
        key = args[i].lstrip("-").lower()
        if key in BUDGET and i + 1 < len(args):
            metrics[key] = float(args[i + 1]); i += 2
        else:
            i += 1
    return metrics


def main(argv: list[str]) -> int:
    metrics = parse(argv)
    if not metrics:
        print("usage: perf_budget.py [--tti MS --lcp MS --inp MS --cls N] | <metrics.json>",
              file=sys.stderr)
        return 2
    breached = 0
    for key, val in metrics.items():
        thr, unit, name = BUDGET[key]
        ok = val < thr
        if not ok:
            breached += 1
        print(f"  {'✓' if ok else '✗'} {name:28} {val}{unit} (budget <{thr}{unit})")
    print(f"VERDICT: {'PASS' if not breached else f'FAIL — {breached} metric(s) over budget'}")
    return 0 if not breached else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
