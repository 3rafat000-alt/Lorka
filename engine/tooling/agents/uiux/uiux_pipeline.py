#!/usr/bin/env python3
"""
uiux_pipeline — Tier-2 Advisor's UI/UX & Design Systems console.

The runtime engine behind `engine/agents/advisors/tier-2-advisor.md`. It turns a raw
"clean up this view / audit this design" request into a single Python-backed,
token-frugal, GATED pipeline — the model spends its expensive tokens only on
judgment, never on locating inline styles, hardcoded hex, or missing &lrm;.

Doctrine: *Design is Truth · few token do trick · big brain small mouth.*
A11y (WCAG 2.2 AA) always outranks any taste dial. Code/commits stay normal prose.

Stages (each GATES the loop — a red drops the pipeline with exit 1):
    1. taste   → literal that duplicates an in-scope :root design token (sofi_scan --taste)
    2. design  → tokens/motion/density/a11y/RTL static pack        (sofi_scan --design)
    3. rtl     → currency amount echoed without the &lrm; RTL prefix (this file)
    4. verify  → mechanical gate: blade compile · view:cache · lint  (sofi_verify)

Then it emits paste-ready RCCF spawn stubs routing each finding class to
the cheapest specialist that clears the bar (frontend-react-engineer · backend-blade-engineer · ui-ux-designer).

CLI
---
    python3 uiux_pipeline.py scan   --prj PRJ-SAKK [--query admin/profile] [--md]
    python3 uiux_pipeline.py rtl    --prj PRJ-SAKK [--query admin]        [--md]
    python3 uiux_pipeline.py gate   --prj PRJ-SAKK [--query <feature>]    # full pipeline, exit-gated
    python3 uiux_pipeline.py brief  --prj PRJ-SAKK [--query <feature>]    # emit RCCF delegation stubs

Exit: 0 = clean/pass · 1 = a gate found a blocking (red) finding or verify failed · 2 = nothing to scan.
Pure stdlib. NEVER writes source. Flexible across any PRJ-{id}.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ── reuse the CEO engine (same-repo import) ──
_CEO = Path(__file__).resolve().parents[1] / "ceo"
sys.path.insert(0, str(_CEO))
try:
    import sofi_scan  # type: ignore
    from feature_scan import _project_dir, _iter_code_files  # type: ignore
    import sofi_verify  # type: ignore
except Exception as e:  # fail-loud: the console is worthless without the engine
    print(json.dumps({"error": f"cannot load CEO engine: {e}"}))
    raise SystemExit(2)


# ── RTL currency hygiene (the missing check-ltr-currency contract, as a mode) ──
# SAKK law (memory: sakk-currency-symbol-left): a currency symbol ALWAYS prefixes the
# amount, and in RTL Blade the amount echo MUST carry a Left-to-Right Mark so the digits
# don't get mirrored next to Arabic text. Accepted markers: &lrm;  ·  the LRM char (U+200E)
# ·  the App\Support\Money helper (which injects it)  ·  the money_formatter (mobile).
# precision-first: a currency GLYPH/code sitting within ~40 chars of a Blade echo of an
# amount — not bare `%` or generic value words (those over-flag; doctrine: no swarm noise).
# NOTE: `$` only as currency when NOT followed by a letter/underscore — else it's a
# PHP/Blade variable sigil (`{{ $error }}`) and every echo would false-positive.
# dot is MANDATORY on the Arabic symbols — bare `رس` matches ordinary words like الرسوم.
_CURRENCY = re.compile(r"(ل\.\s?س|ر\.\s?س|\bSYP\b|\bUSD\b|(?<!\$)\$(?![A-Za-z_{$])|€|£)")
_AMOUNT_ECHO = re.compile(r"\{\{(?!--)|\{!!")      # a Blade echo of a value (not a {{-- comment --}})
# OK markers: &lrm; entity · LRM (U+200E) · FSI/LRI isolates (U+2066/U+2068) · money helpers
# OK markers: &lrm; · LRM/FSI/LRI chars · \u escapes · explicit dir=ltr wrapper · money helpers
_LRM_OK = re.compile(r"""&lrm;|‎|⁦|⁨|\\u\{?20(0e|66|68)|dir=['"]ltr|Money::|money_formatter|@money|formatMoney""", re.I)


def mode_rtl(prj: str, query: str | None, cap: int = 4000) -> dict:
    """Flag Blade lines that echo a currency amount without an RTL prefix."""
    root = _project_dir(prj)
    if not root.exists():
        return {"mode": "rtl", "error": f"project dir not found: {root}", "findings": []}
    q = (query or "").lower().strip()
    findings, scanned = [], 0
    for p in _iter_code_files(root, cap):
        if not p.name.endswith(".blade.php"):
            continue
        rel = str(p)
        if q and q not in rel.lower():
            continue
        scanned += 1
        try:
            for i, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
                if not _AMOUNT_ECHO.search(line):
                    continue
                # precision-first: require a real currency glyph/code on the line
                # (word-based "fee/total" heuristics over-flag — dropped deliberately)
                if not _CURRENCY.search(line):
                    continue
                if _LRM_OK.search(line):
                    continue
                findings.append({
                    "sev": "yellow",
                    "file": rel.split(f"/{prj}/")[-1],
                    "line": i,
                    "hint": "currency/amount echo without &lrm; RTL prefix — wrap via {!! !!} + &lrm; "
                            "or route through App\\Support\\Money (money_formatter on mobile)",
                })
        except Exception:
            continue
    return {"mode": "rtl", "query": query or "(whole project)", "files_scanned": scanned,
            "counts": {"yellow": len(findings)}, "findings": findings,
            "note": "RTL currency-direction gate: amount/currency Blade echoes missing an LRM marker."}


# ── pipeline orchestration ──
STAGES = ["taste", "design", "rtl"]


def _scope(r: dict, query: str | None) -> dict:
    """Path-scope a pack result to the requested view/dir — the shared sofi_scan
    packs keyword-search, not path-filter, so brief/gate stay laser-tight here.
    Filters findings whose file path contains the query; recounts by severity."""
    q = (query or "").lower().strip()
    if not q or "findings" not in r:
        return r
    kept = [f for f in r["findings"] if q in f.get("file", "").lower()]
    counts = {}
    for f in kept:
        counts[f["sev"]] = counts.get(f["sev"], 0) + 1
    r = dict(r)
    r["findings"], r["counts"] = kept, counts
    r["scoped_to"] = query
    return r


def _run_scan(mode: str, prj: str, query: str | None) -> dict:
    if mode == "rtl":
        return mode_rtl(prj, query)  # already path-scoped internally
    # packs (taste/design) walk wide, so post-filter to the query path
    return _scope(sofi_scan.run(mode, prj, query or None, 2000), query)


def _counts(r: dict) -> dict:
    return r.get("counts", {}) or {}


def run_gate(prj: str, query: str | None) -> tuple[int, list[dict]]:
    """Run every static stage + the mechanical verify. Exit 1 on any red or verify fail."""
    reports, worst = [], 0
    for m in STAGES:
        r = _run_scan(m, prj, query)
        reports.append(r)
        if _counts(r).get("red", 0):
            worst = 1
    # mechanical gate last (compiles templates, view:cache lint)
    try:
        argv = ["--prj", prj]
        vrc = sofi_verify.main(argv)
    except SystemExit as e:  # verify raises SystemExit(code)
        vrc = int(e.code or 0)
    except Exception as e:
        vrc = 1
        reports.append({"mode": "verify", "error": str(e)})
    if vrc == 1:
        worst = 1
    reports.append({"mode": "verify", "exit": vrc})
    return worst, reports


# ── RCCF delegation stubs: finding class → cheapest specialist that clears the bar ──
_ROUTE = {
    "taste":  ("sofi-frontend-react-engineer", "sonnet · medium · ultra",
               "Refactor literals to in-scope :root design tokens (zero raw hex/px). A11y AA wins."),
    "design": ("sofi-frontend-react-engineer", "sonnet · medium · ultra",
               "Close WCAG 2.2 AA gaps: focus-visible, aria-describedby, labels, contrast, no color-only status."),
    "rtl":    ("sofi-backend-blade-engineer", "sonnet · medium · ultra",
               "Wrap currency/amount echoes with &lrm; or App\\Support\\Money; verify RTL direction."),
}


def emit_briefs(prj: str, query: str | None) -> str:
    out = [f"# Division 4 — RCCF delegation briefs · {prj} · scope: {query or '(whole project)'}", ""]
    for m in STAGES:
        r = _run_scan(m, prj, query)
        n = sum(_counts(r).values())
        if not n:
            out.append(f"## {m}: ✅ clean — no delegation\n")
            continue
        agent, route, cmd = _ROUTE[m]
        sample = r.get("findings", [])[:6]
        out += [
            f"## {m}: 🔧 {n} finding(s) → `{agent}`",
            f"```",
            f"spawn {agent} — [{prj}] {m}-pass on {query or 'active views'}  (build the RCCF block per engine/protocols/01-delegation-rccf.md)",
            f"🎭 Role   {agent}  ({route})",
            f"📂 Context STATE.md head_sha · frozen sakk-tokens.css · WCAG 2.2 AA matrix",
            f"🎯 Command {cmd}",
            f"📐 Format  fix each site below, checkpoint per view, gate-bar = AA pass + tokens-only + view:cache clean",
            f"   sites:",
        ]
        out += [f"     - {f['file']}:{f['line']} — {f['hint']}" for f in sample]
        if n > len(sample):
            out.append(f"     … +{n - len(sample)} more (run `scan --md` for the full list)")
        out += ["```", ""]
    return "\n".join(out)


def _to_md(r: dict) -> str:
    if r.get("mode") == "rtl":
        c = r.get("counts", {})
        head = f"# rtl — {r.get('query')} · {r.get('files_scanned',0)} blade files · 🟡{c.get('yellow',0)}"
        body = [f"- 🟡 {f['file']}:{f['line']} — {f['hint']}" for f in r.get("findings", [])[:60]]
        return "\n".join([head] + body + [f"> {r.get('note','')}"])
    return sofi_scan.to_md(r)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Division 4 (UI/UX & Design) console")
    ap.add_argument("cmd", choices=["scan", "rtl", "gate", "brief"])
    ap.add_argument("--prj", required=True)
    ap.add_argument("--query", default="")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args(argv)
    q = a.query or None

    if a.cmd == "rtl":
        r = mode_rtl(a.prj, q)
        print(_to_md(r) if a.md else json.dumps(r, ensure_ascii=False, indent=1))
        return 1 if r.get("counts", {}).get("red") else 0

    if a.cmd == "scan":
        blocks = [_run_scan(m, a.prj, q) for m in STAGES]
        if a.md:
            print("\n\n".join(_to_md(b) for b in blocks))
        else:
            print(json.dumps({"scan": blocks}, ensure_ascii=False, indent=1))
        return 1 if any(b.get("counts", {}).get("red") for b in blocks) else 0

    if a.cmd == "brief":
        print(emit_briefs(a.prj, q))
        return 0

    # gate
    rc, reports = run_gate(a.prj, q)
    if a.md:
        print("\n\n".join(_to_md(r) if r.get("mode") in ("taste", "design", "rtl") else
                           f"# {r.get('mode')} → exit {r.get('exit', r.get('error'))}" for r in reports))
    else:
        print(json.dumps({"gate": reports, "exit": rc}, ensure_ascii=False, indent=1))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
