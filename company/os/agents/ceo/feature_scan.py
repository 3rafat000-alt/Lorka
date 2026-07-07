#!/usr/bin/env python3
"""
feature_scan — static, token-frugal feature locator + 4-pillar pre-flagger.

Doctrine: *few token do trick*. The LLM should NOT read dozens of files to review a
feature. This tool does the deterministic heavy lifting in pure Python (grep-first,
zero model tokens), then emits ONE compact JSON the reviewer reads instead of the
whole source tree — the token-saving engine behind /sofi-spec-review and /sofi-feature.

What it does
------------
1. Locate — find every file that makes up feature <NAME> across backend + mobile,
   keyed by feature keywords (name + synonyms) matched against paths and content.
2. Group — bucket the file set into the 4 review pillars:
       ① Data & Logic   (migrations, models, controllers, services, routes, api)
       ② Admin & Ops     (admin views/controllers, audit logs, status/state machines)
       ③ UI/UX & Taste   (blade/vue views, css, flutter screens)
       ④ Edge Cases      (jobs, webhooks, validation, error handling)
3. Pre-flag — run cheap static heuristics per pillar and emit suspects with file:line.
   These are HINTS for the reviewer, not verdicts — the LLM confirms/ranks.

Output = compact JSON (default) or a terse markdown skeleton (--md). The reviewer
opens only the flagged file:line spots, not the tree → ~70-90% fewer read tokens.

Pure stdlib. Skips vendor/node_modules/.git/build/storage. Never writes source.

CLI
---
    python feature_scan.py "<feature>" --prj PRJ-SAKK            # JSON
    python feature_scan.py "<feature>" --prj PRJ-SAKK --md       # markdown skeleton
    python feature_scan.py "<feature>" --prj PRJ-SAKK --max 400  # cap files scanned
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ── workspace resolution (reuse sofi_tools when importable; fallback otherwise) ──
try:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tooling"))
    from sofi_tools import paths as _paths  # type: ignore

    def _project_dir(prj: str) -> Path:
        return _paths.project_dir(prj)
except Exception:  # standalone fallback
    def _project_dir(prj: str) -> Path:
        root = Path(__file__).resolve().parents[4]
        return root / "projects" / prj

SKIP_DIRS = {
    ".git", "node_modules", "vendor", "build", "dist", ".dart_tool",
    "storage", "bootstrap", "public", "__pycache__", ".idea", ".fvm",
    "ios/Pods", "coverage", "_scratch",
}
CODE_EXT = {
    ".php", ".dart", ".blade.php", ".vue", ".js", ".ts", ".css", ".scss", ".yaml", ".yml",
}

# ── pillar bucketing by path signal (ORDER MATTERS: strongest signal first) ──
# UI first (file-extension + view-dir is unambiguous), then admin, then edge, then data.
PILLAR_RULES = [
    ("admin_ops",   re.compile(r"(/admin/|dashboard|audit|/enums?/|/policies/|StateMachine|/status)", re.I)),
    ("ui_taste",    re.compile(r"(\.blade\.php$|\.vue$|/views?/|/screens?/|/widgets?/|/pages?/|\.css$|\.scss$|/presentation/)", re.I)),
    ("edge_cases",  re.compile(r"(/jobs?/|webhook|/listeners?/|/events?/|/requests?/|validation|/middleware/|exception|handler)", re.I)),
    ("data_logic",  re.compile(r"(migration|/models?/|/services?/|/controllers?/|/routes?/|/api/|Repository|/Resources?/)", re.I)),
]

# ── cheap static pre-flag heuristics (line-level). (label, regex, pillar, severity) ──
HEURISTICS = [
    # ① data & logic
    ("migration may lack down()/rollback", re.compile(r"function up\("), "data_logic", "orange", "_mig_no_down"),
    ("mass-assign risk: no $fillable/$guarded near model", re.compile(r"class \w+ extends Model"), "data_logic", "yellow", "_model_guard"),
    ("possible N+1: ->get() without ->with()", re.compile(r"->(get|first|all)\(\)"), "data_logic", "yellow", None),
    ("raw query — check injection", re.compile(r"DB::(raw|statement|select)\("), "data_logic", "orange", None),
    # ② admin & ops
    ("status compared as string literal — verify state machine", re.compile(r"status\s*==\s*['\"]"), "admin_ops", "yellow", None),
    # ③ ui/ux & taste
    ("unescaped Blade output {!! !!} — XSS surface", re.compile(r"\{!!"), "ui_taste", "red", None),
    ("missing @csrf near <form> (verify)", re.compile(r"<form\b"), "ui_taste", "orange", "_form_csrf"),
    ("->user->name — User has full_name not name", re.compile(r"->user->name\b"), "ui_taste", "orange", None),
    ("hardcoded hex color — should use design token", re.compile(r"#[0-9a-fA-F]{6}\b"), "ui_taste", "yellow", None),
    # ④ edge cases
    ("swallowed status code — surface real error", re.compile(r"(catch|DioError|Exception).{0,40}(403|500|error)", re.I), "edge_cases", "orange", None),
    ("empty catch — silent failure", re.compile(r"catch\s*\([^)]*\)\s*\{\s*\}"), "edge_cases", "orange", None),
    ("TODO/FIXME/HACK left in feature", re.compile(r"\b(TODO|FIXME|HACK|XXX)\b"), "edge_cases", "yellow", None),
]


def _synonyms(feature: str) -> list[str]:
    f = feature.strip().lower()
    words = [w for w in re.split(r"[\s_\-/]+", f) if len(w) > 2]
    extra = {
        "payment": ["pay", "deposit", "withdraw", "wallet", "transaction", "transfer", "ccpayment", "stripe"],
        "مدفوعات": ["payment", "pay", "deposit", "withdraw", "wallet", "transaction"],
        "kyc": ["verify", "verification", "identity", "selfie", "document"],
        "payroll": ["salary", "company", "employee", "wage"],
        "chat": ["message", "conversation", "support", "ticket"],
        "gold": ["xau", "price", "metal"],
        "invite": ["referral", "ref", "applink"],
        "card": ["virtualcard", "issuing"],
    }
    out = set(words)
    for w in list(words) + [f]:
        out.update(extra.get(w, []))
    return sorted(out)


def _iter_code_files(root: Path, cap: int):
    n = 0
    for p in root.rglob("*"):
        if n >= cap:
            return
        if not p.is_file():
            continue
        rel = str(p)
        if any(f"/{d}/" in rel or rel.endswith(f"/{d}") for d in SKIP_DIRS):
            continue
        if p.name.endswith(".blade.php") or p.suffix in CODE_EXT:
            n += 1
            yield p


def _pillar_for(rel: str) -> str:
    for name, rx in PILLAR_RULES:
        if rx.search(rel):
            return name
    return "data_logic"


def _read_lines(p: Path) -> list[str]:
    try:
        return p.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return []


def scan(feature: str, prj: str, cap: int = 500) -> dict:
    pdir = _project_dir(prj)
    syn = _synonyms(feature)
    syn_rx = re.compile("|".join(re.escape(s) for s in syn), re.I) if syn else None

    files: dict[str, dict] = {}   # rel -> {pillar, hits}
    for p in _iter_code_files(pdir, cap):
        rel = str(p.relative_to(pdir)) if str(p).startswith(str(pdir)) else str(p)
        path_hit = bool(syn_rx and syn_rx.search(rel))
        lines = _read_lines(p)
        content_hit = bool(syn_rx and any(syn_rx.search(l) for l in lines[:400]))
        if not (path_hit or content_hit):
            continue
        files[rel] = {"pillar": _pillar_for(rel), "path_match": path_hit, "lines": lines}

    # pre-flag heuristics only on matched feature files
    findings: list[dict] = []
    for rel, meta in files.items():
        lines = meta["lines"]
        for label, rx, pillar, sev, special in HEURISTICS:
            for i, line in enumerate(lines, 1):
                if not rx.search(line):
                    continue
                if special == "_mig_no_down" and any("function down(" in l for l in lines):
                    continue
                if special == "_model_guard" and any(("$fillable" in l or "$guarded" in l) for l in lines):
                    continue
                if special == "_form_csrf":
                    window = "\n".join(lines[max(0, i - 3):i + 6])
                    if "@csrf" in window or 'method="get"' in line.lower():
                        continue
                findings.append({
                    "pillar": pillar, "sev": sev, "file": rel, "line": i,
                    "hint": label, "code": line.strip()[:120],
                })
                break  # one hit per (file,heuristic) — reviewer opens the spot

    # group file set by pillar (drop line bodies to keep output tiny)
    by_pillar: dict[str, list[str]] = {"data_logic": [], "admin_ops": [], "ui_taste": [], "edge_cases": []}
    for rel, meta in files.items():
        by_pillar.setdefault(meta["pillar"], []).append(rel)

    sev_rank = {"red": 0, "orange": 1, "yellow": 2}
    findings.sort(key=lambda f: (sev_rank.get(f["sev"], 3), f["file"], f["line"]))

    return {
        "feature": feature, "prj": prj, "synonyms": syn,
        "files_matched": len(files), "files_scanned_cap": cap,
        "file_set": by_pillar,
        "preflags": findings,
        "preflag_counts": {
            "red": sum(1 for f in findings if f["sev"] == "red"),
            "orange": sum(1 for f in findings if f["sev"] == "orange"),
            "yellow": sum(1 for f in findings if f["sev"] == "yellow"),
        },
        "note": "preflags are STATIC HINTS, not verdicts. Reviewer opens each file:line, confirms, ranks, and adds semantic findings the heuristics can't see.",
    }


def to_md(r: dict) -> str:
    emo = {"red": "🔴", "orange": "🟠", "yellow": "🟡"}
    out = [f"# feature-scan — {r['feature']} ({r['prj']})",
           f"matched {r['files_matched']} files · preflags "
           f"🔴{r['preflag_counts']['red']} 🟠{r['preflag_counts']['orange']} 🟡{r['preflag_counts']['yellow']}", ""]
    titles = {"data_logic": "① Data & Logic", "admin_ops": "② Admin & Ops",
              "ui_taste": "③ UI/UX & Taste", "edge_cases": "④ Edge Cases"}
    for key, title in titles.items():
        fs = r["file_set"].get(key, [])
        out.append(f"## {title} — {len(fs)} files")
        for f in fs[:40]:
            out.append(f"- {f}")
        pf = [x for x in r["preflags"] if x["pillar"] == key]
        if pf:
            out.append(f"  preflags:")
            for x in pf[:30]:
                out.append(f"  - {emo.get(x['sev'],'⚪')} {x['file']}:{x['line']} — {x['hint']}")
        out.append("")
    out.append("> " + r["note"])
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="static feature locator + 4-pillar pre-flagger (token-frugal)")
    ap.add_argument("feature")
    ap.add_argument("--prj", required=True)
    ap.add_argument("--max", type=int, default=500, help="cap files scanned")
    ap.add_argument("--md", action="store_true", help="markdown skeleton instead of JSON")
    a = ap.parse_args(argv)
    r = scan(a.feature, a.prj, a.max)
    print(to_md(r) if a.md else json.dumps(r, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
