#!/usr/bin/env python3
"""
sofi_scan — the SOFI team's unified static analysis engine (token-frugal, 0 model tokens).

Doctrine: *few token do trick* · *big brain, small mouth*. Every command and every agent
leans on THIS Python engine to do the heavy, deterministic thinking — locate, pre-flag,
map — so the model spends its (expensive) tokens only on judgment, never on reading the tree.

One engine, many modes (each backs one `/sofi-*` command):

    search    → ranked code locator (backs /sofi-audit, general "where is X")
    feature   → feature file-set + 4-pillar pre-flags (backs /sofi-spec-review, /sofi-feature)
    design    → UI/UX & taste static audit: tokens, motion, density, a11y, RTL (backs /sofi-design-taste)
    flow      → UserFlow map: routes → views, orphan/dead-end views (UX journey, backs /sofi-audit ui)
    security  → OWASP static pre-flags: XSS, SQLi, mass-assign, secrets, IDOR (backs /sofi-secure scan)
    wiring    → interconnection: route↔controller↔view, env/config reads, dead includes (backs /sofi-audit integration)
    taint     → source→sink taint trace: user input reaching a sink unsanitized (backs /sofi-secure, deeper than 'security')
    taste     → value↔token cross-check: literal that duplicates an existing :root design token (backs /sofi-design-taste)
    all       → run the analytical modes and merge

Shares one file-walker (skips vendor/node_modules/.git/build/storage). Pure stdlib.
NEVER writes source. Emits compact JSON (default) or terse markdown (--md).

CLI
---
    python sofi_scan.py <mode> [query] --prj PRJ-SAKK [--md] [--max 900]
        search "payment"     feature "KYC"     design ""     flow ""     security ""    wiring ""
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# reuse the feature_scan primitives (single source of truth for walker + synonyms)
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from feature_scan import (  # type: ignore
        _iter_code_files, _synonyms, _read_lines, _project_dir,
        _pillar_for, scan as _feature_scan,
    )
except Exception as e:  # pragma: no cover
    print(f"sofi_scan: cannot import feature_scan ({e})", file=sys.stderr)
    raise

EMO = {"red": "🔴", "orange": "🟠", "yellow": "🟡", "info": "⚪"}
SEV_RANK = {"red": 0, "orange": 1, "yellow": 2, "info": 3}


# ─────────────────────────── heuristic packs ───────────────────────────
# (label, compiled-regex, severity, optional special-guard-key)
SECURITY_PACK = [
    # {!! !!} only flags RAW interpolation; safe formatters (Money::format &lrm;, icon SVG map, @svg) excluded via _xss_safe
    ("unescaped Blade {!! !!} — XSS surface", re.compile(r"\{!!"), "red", "_xss_safe"),
    # SQLi requires a $var INSIDE the quoted SQL string (not a ?-bound param passed after)
    ("raw SQL with interpolation — SQLi", re.compile(r"DB::(raw|statement|select|unprepared)\(\s*[\"'][^\"']*\$"), "red", None),
    ("mass-assign: create/update with request->all()", re.compile(r"->(create|update|fill)\(\s*\$request->all\(\)"), "red", None),
    # hardcoded secret: value must look like a credential, NOT a URL path (excludes '/auth/pin' route constants)
    ("possible hardcoded secret/key", re.compile(r"(api[_-]?key|secret|password|token)\s*=\s*['\"](?![/.])[A-Za-z0-9+_\-]{12,}", re.I), "red", "_env_ok"),
    ("IDOR: find($id) — verify ownership/authorization", re.compile(r"::find(OrFail)?\(\s*\$(id|request)"), "orange", "_idor_check"),
    ("eval/unserialize — RCE surface", re.compile(r"\b(eval|unserialize)\s*\("), "red", None),
    ("insecure http:// endpoint", re.compile(r"http://(?!127|localhost|.*\.local)"), "yellow", None),
    ("missing auth — route/controller w/o middleware (verify)", re.compile(r"Route::(get|post|put|patch|delete)\("), "yellow", "_auth_hint"),
    # weak-rand: skip comment lines + cache-key uniqid (not a security token)
    ("weak randomness for security token", re.compile(r"\b(rand|mt_rand|uniqid)\s*\("), "orange", "_weakrand"),
    ("CSRF: <form> without @csrf nearby", re.compile(r"<form\b"), "orange", "_form_csrf"),
]

DESIGN_PACK = [
    ("hardcoded hex — use design token / :root var", re.compile(r"#[0-9a-fA-F]{6}\b"), "yellow", None),
    ("hardcoded px font-size — use scale/rem", re.compile(r"font-size:\s*\d+px"), "yellow", None),
    ("!important — specificity war, brittle", re.compile(r"!important"), "yellow", None),
    ("fixed px width — not responsive", re.compile(r"width:\s*\d{3,}px"), "yellow", None),
    ("<img> without alt — a11y/SEO", re.compile(r"<img(?![^>]*\balt=)[^>]*>"), "orange", None),
    ("icon/interactive without aria-label", re.compile(r"<(button|a)\b(?![^>]*aria-)[^>]*>\s*<(i|svg)\b"), "orange", None),
    ("div/span as button — not keyboard-accessible", re.compile(r"<(div|span)[^>]*\@click|<(div|span)[^>]*onclick", re.I), "orange", None),
    ("no reduced-motion guard around animation", re.compile(r"(animation:|transition:)"), "info", "_motion"),
    ("RTL: bare directional Blade output — needs &lrm; / dir", re.compile(r"\{\{\s*.*(price|amount|symbol|balance).*\}\}", re.I), "yellow", None),
    ("generic centered hero (AI-UI smell)", re.compile(r"text-center.*(hero|jumbotron)|mx-auto.*text-center", re.I), "info", None),
]

WIRING_PACK = [
    ("env() outside config — cache breaks it", re.compile(r"(?<!//)\benv\(['\"]"), "orange", "_is_config"),
    ("hardcoded URL — should be config/route()", re.compile(r"['\"]https?://[^'\"]+['\"]"), "yellow", "_local_ok"),
    ("@include of a partial — verify it exists", re.compile(r"@include\(['\"]([^'\"]+)"), "info", None),
    ("dd()/dump()/var_dump left in code", re.compile(r"\b(dd|dump|var_dump)\s*\("), "orange", None),
    ("TODO/FIXME wiring gap", re.compile(r"\b(TODO|FIXME|HACK|XXX)\b"), "yellow", None),
    ("direct Http/curl call — wrap in a service", re.compile(r"(Http::|curl_exec|file_get_contents\(\s*['\"]http)"), "info", None),
]


# ─────────────────────── taint trace (source → sink) ───────────────────────
# Pragmatic PHP/Blade taint pass — the "AST path-tracing" the architect doctrine asks for,
# done with intra-file var-flow (no external parser, pure stdlib). Tracks user-controlled
# input into dangerous sinks and clears it when a sanitizer touches it. Findings are HINTS.
_TAINT_SRC = re.compile(
    r"\$(\w+)\s*=\s*[^;]*?(\$request->|request\(\)|Input::|\$_(GET|POST|REQUEST|COOKIE)\b|->input\(|->query\()")
_TAINT_SINKS = [
    ("SQLi", re.compile(r"DB::(raw|statement|select|unprepared)\(")),
    ("XSS (raw Blade)", re.compile(r"\{!!")),
    ("XSS (echo)", re.compile(r"\becho\b|\bprint\b")),
    ("RCE (exec)", re.compile(r"\b(exec|shell_exec|system|passthru|proc_open|popen|eval)\s*\(")),
    ("Path traversal", re.compile(r"(file_get_contents|fopen|require|include|unlink|readfile)\s*\(")),
    ("Open redirect", re.compile(r"redirect\(\s*\$")),
]
_TAINT_SANITIZE = re.compile(
    r"\b(e|htmlspecialchars|htmlentities|intval|floatval|\(int\)|\(float\)|validated|validate|"
    r"escapeshellarg|escapeshellcmd|basename|Str::|Purifier|filter_var|abs|bindValue)\b|->validate\(")
# an uploaded-file's own realpath/pathname is a framework-generated tmp path, NOT a user-typed
# path string — reading it is not traversal. Assignments through these don't taint.
_TAINT_UPLOAD = re.compile(r"->file\(|->getRealPath\(|->getPathname\(|->store\(|UploadedFile")


def mode_taint(prj, query, cap):
    _, files, syn = _collect(prj, cap, query)
    findings = []
    for rel, lines in files.items():
        tainted: dict[str, int] = {}          # var -> line first seen tainted
        for i, line in enumerate(lines, 1):
            m = _TAINT_SRC.search(line)
            if m and not _TAINT_UPLOAD.search(line):
                tainted[m.group(1)] = i
            # a sanitizer assignment clears taint: $x = e($x)
            if _TAINT_SANITIZE.search(line):
                for v in list(tainted):
                    if re.search(rf"\${v}\b", line):
                        tainted.pop(v, None)
            if not tainted:
                continue
            for sink_name, srx in _TAINT_SINKS:
                if not srx.search(line):
                    continue
                for v, src_ln in tainted.items():
                    if re.search(rf"\${v}\b", line):
                        findings.append({
                            "file": rel, "line": i, "sev": "red",
                            "hint": f"{sink_name}: tainted ${v} (from line {src_ln}) reaches sink unsanitized",
                            "code": line.strip()[:120]})
                        break
    findings.sort(key=lambda f: (f["file"], f["line"]))
    return {"mode": "taint", "query": query or "(whole project)", "files_scanned": len(files),
            "counts": {"red": len(findings)}, "findings": findings[:120],
            "note": "intra-file taint HINTS: user input → sink with no sanitizer between. "
                    "Confirm cross-function flow + framework auto-escaping (Blade {{ }} auto-escapes) manually."}


# ─────────────────────── taste cross-check (value ↔ token) ───────────────────────
# The 'sofi-taste' compliance the doctrine wants: not "hex is bad" but "this exact hex
# already has a design token IN SCOPE — use it". Precision-first (hardened after a batch
# of false positives): only fires when BOTH hold —
#   1. SCOPE — the token is defined in the SAME file's :root (guarantees var() resolves;
#      no cross-file table pollution, no undefined-var breakage on standalone pages).
#   2. CSS CONTEXT — the literal sits in a CSS *property* declaration (`prop: …#hex`),
#      not a JS object, PHP array, Tailwind colors:{}, or an SVG presentation attribute
#      (fill="#.."/stroke="#.."), where var() does not apply.
_TOKEN_DEF = re.compile(r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{3,8})\b")
_HEX_LIT = re.compile(r"#[0-9a-fA-F]{3,8}\b")
# a CSS declaration: `identifier : … #hex`  (colon-assigned, not `=`-assigned XML attr)
_CSS_DECL = re.compile(r"[\w-]+\s*:\s*[^;{}=]*#[0-9a-fA-F]{3,8}\b")
# SVG/XML presentation attribute or JS/PHP string/array literal around the hex → not CSS
_NON_CSS_CTX = re.compile(r"""(fill|stroke|stop-color|color|bgcolor)\s*=|['"]#[0-9a-fA-F]{3,8}['"]|=>\s*['"]#""")


def mode_taste(prj, query, cap):
    _, files, _ = _collect(prj, cap, None)
    findings = []
    for rel, lines in files.items():
        # 1. build a PER-FILE token table (scope guarantee) — only tokens THIS file defines
        val2tok: dict[str, str] = {}
        for line in lines:
            for m in _TOKEN_DEF.finditer(line):
                val2tok.setdefault(m.group(2).lower(), m.group(1))
        if not val2tok:
            continue  # no local tokens → any var() swap would be out-of-scope; skip file
        for i, line in enumerate(lines, 1):
            if _TOKEN_DEF.search(line) or "var(--" in line:
                continue  # the declaration itself, or already a var
            if not _CSS_DECL.search(line) or _NON_CSS_CTX.search(line):
                continue  # not a CSS property assignment, or an SVG-attr / string literal
            for hm in _HEX_LIT.finditer(line):
                tok = val2tok.get(hm.group(0).lower())
                if tok:
                    findings.append({"file": rel, "line": i, "sev": "orange",
                                     "hint": f"literal {hm.group(0)} duplicates in-scope token {tok} — use var({tok})",
                                     "code": line.strip()[:120]})
                    break
    findings.sort(key=lambda f: (f["file"], f["line"]))
    return {"mode": "taste", "query": query or "(whole project)", "files_scanned": len(files),
            "counts": {"orange": len(findings)}, "findings": findings[:120],
            "note": "taste cross-check (precision-first): literal duplicates a token defined in the SAME file's "
                    ":root, in a CSS property context. Cross-file / JS / SVG-attr cases intentionally not flagged."}


def _run_pack(files: dict[str, list[str]], pack) -> list[dict]:
    out = []
    for rel, lines in files.items():
        joined_lower = None
        for label, rx, sev, special in pack:
            for i, line in enumerate(lines, 1):
                if not rx.search(line):
                    continue
                if special == "_form_csrf":
                    window = "\n".join(lines[max(0, i - 3):i + 6])
                    if "@csrf" in window or 'method="get"' in line.lower():
                        continue
                if special == "_xss_safe":
                    # trusted, non-user output inside {!! !!}: currency helper (&lrm;), icon SVG map, blade @svg
                    if re.search(r"Money::format|\$icons\[|@svg|->toHtml\(|Blade::|svg\(", line):
                        continue
                if special == "_weakrand":
                    stripped = line.lstrip()
                    if stripped.startswith(("//", "*", "#", "/*")):
                        continue
                    if "uniqid" in line and re.search(r"(cache|health|_key|tmp|temp)", line, re.I):
                        continue
                    # cosmetic rand (chart height/width/style/opacity) is not a security token
                    if re.search(r"(height|width|style|opacity|:\s*rand|%|deg|left|top)", line, re.I):
                        continue
                if special == "_idor_check":
                    # ownership verified within the next few lines → not IDOR
                    window = "\n".join(lines[i:i + 6])
                    if re.search(r"user_id\s*!==|->user\b|Auth::id|authorize\(|->user->id", window):
                        continue
                if special == "_env_ok" and (".env" in rel or "config/" in rel):
                    continue
                if special == "_is_config" and "/config/" in rel:
                    continue
                if special == "_local_ok" and re.search(r"\.local|127\.0\.0\.1|localhost", line):
                    continue
                if special == "_motion":
                    if joined_lower is None:
                        joined_lower = "\n".join(lines).lower()
                    if "prefers-reduced-motion" in joined_lower:
                        continue
                if special == "_auth_hint":
                    if joined_lower is None:
                        joined_lower = "\n".join(lines).lower()
                    if "middleware" in joined_lower or "auth" in joined_lower:
                        continue
                out.append({"file": rel, "line": i, "hint": label, "sev": sev,
                            "code": line.strip()[:120]})
                break
    out.sort(key=lambda f: (SEV_RANK.get(f["sev"], 9), f["file"], f["line"]))
    return out


# ─────────────────────────── file collection ───────────────────────────
def _collect(prj: str, cap: int, query: str | None):
    """Return {rel: lines}. If query given, keep only files matching its synonyms."""
    pdir = _project_dir(prj)
    syn = _synonyms(query) if query else []
    syn_rx = re.compile("|".join(re.escape(s) for s in syn), re.I) if syn else None
    files: dict[str, list[str]] = {}
    for p in _iter_code_files(pdir, cap):
        rel = str(p.relative_to(pdir)) if str(p).startswith(str(pdir)) else str(p)
        lines = _read_lines(p)
        if syn_rx and not (syn_rx.search(rel) or any(syn_rx.search(l) for l in lines[:400])):
            continue
        files[rel] = lines
    return pdir, files, syn


# ─────────────────────────── modes ───────────────────────────
def mode_search(prj, query, cap):
    pdir, files, syn = _collect(prj, cap, query)
    ranked = []
    syn_rx = re.compile("|".join(re.escape(s) for s in syn), re.I) if syn else None
    for rel, lines in files.items():
        hits = sum(len(syn_rx.findall(l)) for l in lines) if syn_rx else 0
        path_hit = bool(syn_rx and syn_rx.search(rel))
        ranked.append({"file": rel, "score": hits + (5 if path_hit else 0),
                       "pillar": _pillar_for(rel)})
    ranked.sort(key=lambda r: -r["score"])
    return {"mode": "search", "query": query, "synonyms": syn,
            "matched": len(ranked), "results": ranked[:60]}


def mode_pack(prj, query, cap, name, pack):
    _, files, syn = _collect(prj, cap, query)
    findings = _run_pack(files, pack)
    counts = {s: sum(1 for f in findings if f["sev"] == s) for s in ("red", "orange", "yellow", "info")}
    return {"mode": name, "query": query or "(whole project)", "files_scanned": len(files),
            "counts": counts, "findings": findings[:120],
            "note": "static HINTS, not verdicts — reviewer opens each file:line, confirms, ranks."}


def mode_flow(prj, query, cap):
    """UserFlow map: routes → views + orphan views (never rendered/included)."""
    pdir, _files, _ = _collect(prj, cap, None)  # walk all
    route_rx = re.compile(r"Route::(get|post|put|patch|delete)\(\s*['\"]([^'\"]+)['\"].*?(?:->name\(\s*['\"]([^'\"]+)['\"])?", re.S)
    view_ref_rx = re.compile(r"(?:view\(|@extends\(|@include\()\s*['\"]([^'\"]+)['\"]")
    routes, referenced = [], set()
    blade_views = set()
    src = pdir / "backend"
    for p in _iter_code_files(src, cap) if src.exists() else _iter_code_files(pdir, cap):
        rel = str(p.relative_to(pdir))
        text = "\n".join(_read_lines(p))
        if rel.endswith(".blade.php"):
            # view name = path under resources/views without .blade.php, dotted
            m = re.search(r"resources/views/(.+)\.blade\.php$", rel)
            if m:
                blade_views.add(m.group(1).replace("/", "."))
        if "/routes/" in rel:
            for mo in route_rx.finditer(text):
                routes.append({"method": mo.group(1), "uri": mo.group(2), "name": mo.group(3) or ""})
        for mo in view_ref_rx.finditer(text):
            referenced.add(mo.group(1))
    def _is_partial(v: str) -> bool:
        # private partials (_name) and .partials. dirs are included, not routed — never orphans
        return "partials" in v or any(seg.startswith("_") for seg in v.split("."))
    orphans = sorted(v for v in blade_views
                     if v not in referenced
                     and not _is_partial(v)
                     and not any(v.startswith(p) for p in ("components.", "layouts.", "installer.", "emails.", "vendor.", "errors.")))
    return {"mode": "flow", "routes": len(routes), "views": len(blade_views),
            "route_map": routes[:80],
            "orphan_views": orphans[:60],
            "note": "orphan_views = blade files no route/@include/@extends references (dead-end or missing wiring). components/layouts/emails excluded."}


def run(mode, prj, query, cap):
    if mode == "search":
        return mode_search(prj, query, cap)
    if mode == "feature":
        return _feature_scan(query or "", prj, cap)
    if mode == "design":
        return mode_pack(prj, query, cap, "design", DESIGN_PACK)
    if mode == "security":
        return mode_pack(prj, query, cap, "security", SECURITY_PACK)
    if mode == "wiring":
        return mode_pack(prj, query, cap, "wiring", WIRING_PACK)
    if mode == "taint":
        return mode_taint(prj, query, cap)
    if mode == "taste":
        return mode_taste(prj, query, max(cap, 2000))  # tokens may live far from usage
    if mode == "flow":
        return mode_flow(prj, query, max(cap, 4000))  # flow needs the whole tree to resolve references
    if mode == "all":
        return {"design": mode_pack(prj, query, cap, "design", DESIGN_PACK),
                "security": mode_pack(prj, query, cap, "security", SECURITY_PACK),
                "wiring": mode_pack(prj, query, cap, "wiring", WIRING_PACK),
                "flow": mode_flow(prj, query, cap)}
    raise SystemExit(f"unknown mode: {mode}")


def to_md(r: dict) -> str:
    if "mode" not in r and "design" in r:  # 'all'
        return "\n\n".join(to_md(r[k]) for k in ("security", "design", "wiring", "flow"))
    m = r.get("mode")
    if m == "search":
        out = [f"# search — {r['query']} ({r['matched']} files)"]
        out += [f"- {x['score']:>3} · {x['file']}" for x in r["results"][:40]]
        return "\n".join(out)
    if m == "flow":
        out = [f"# UserFlow — {r['routes']} routes · {r['views']} views · {len(r['orphan_views'])} orphans"]
        out.append("## routes")
        out += [f"- {x['method'].upper():6} {x['uri']}  {('('+x['name']+')') if x['name'] else ''}" for x in r["route_map"][:50]]
        out.append("## orphan views (dead-end / unwired)")
        out += [f"- 🟠 {v}" for v in r["orphan_views"]]
        return "\n".join(out)
    if m == "feature":
        # reuse feature_scan's md via its own function if present
        try:
            from feature_scan import to_md as f_md  # type: ignore
            return f_md(r)
        except Exception:
            return json.dumps(r, ensure_ascii=False, indent=1)
    # pack modes
    c = r["counts"]
    out = [f"# {m} — {r['query']} · {r['files_scanned']} files · "
           f"🔴{c.get('red',0)} 🟠{c.get('orange',0)} 🟡{c.get('yellow',0)} ⚪{c.get('info',0)}"]
    for f in r["findings"][:60]:
        out.append(f"- {EMO.get(f['sev'],'⚪')} {f['file']}:{f['line']} — {f['hint']}")
    out.append(f"> {r['note']}")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="SOFI unified static analysis engine (token-frugal)")
    ap.add_argument("mode", choices=["search", "feature", "design", "flow", "security", "wiring", "taint", "taste", "all"])
    ap.add_argument("query", nargs="?", default="")
    ap.add_argument("--prj", required=True)
    ap.add_argument("--max", type=int, default=900)
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args(argv)
    r = run(a.mode, a.prj, a.query or None, a.max)
    print(to_md(r) if a.md else json.dumps(r, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
