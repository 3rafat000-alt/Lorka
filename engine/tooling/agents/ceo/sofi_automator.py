#!/usr/bin/env python3
"""
sofi_automator — the static 7-steel-rules scanner for the spec-review flow.

Project-agnostic: walks any directory, dynamically handles .php / .dart / .sql /
migrations. Each check_* returns a list of Finding dicts; run_all() aggregates a
SEV-first report (🔴 blockers vs 🟡 nits). Zero model tokens — pure Python.

Model routing (economic grid, 2026-07-01 — routing.yaml v4.2):
  Phase 1 (this script + grep sweep + SEV draft) runs under Haiku 4.5 / Sonnet 5
  ("spec-review-scan" route). Phase 2 hands the gathered context to Fable 5, the
  hard gate ("spec-review-gate"): 7-steel-rules match, Tier-A check, final SEV
  report + code approval. Opus 4.8 = last-resort deep debugging only.

Usage (CLI):
    python3 sofi_automator.py <project_dir> [--rule N] [--json]
Usage (library):
    from sofi_automator import run_all, check_422_responses, ...
"""

from __future__ import annotations
import json, os, re, sys
from pathlib import Path

SKIP_DIRS = {"vendor", "node_modules", ".git", "storage", "build", ".dart_tool",
             "bootstrap", "public", ".idea", "coverage", "_scratch"}


def _walk(directory, exts):
    """Yield Path objects under directory matching extensions, skipping vendor trees."""
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if any(f.endswith(e) for e in exts):
                yield Path(root) / f


def _read(p):
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _finding(sev, rule, path, line, msg):
    return {"sev": sev, "rule": rule, "file": str(path), "line": line, "msg": msg}


def _rel(findings, base):
    base = str(base)
    for f in findings:
        if f["file"].startswith(base):
            f["file"] = f["file"][len(base):].lstrip("/")
    return findings


# ── Rule 1 ──────────────────────────────────────────────────────────────────
def check_422_responses(directory):
    """API controllers/FormRequests must yield 422 JSON on validation error, never 302."""
    out = []
    for p in _walk(directory, (".php",)):
        s = _read(p)
        is_api = "/API/" in str(p) or "namespace App\\Http\\Controllers\\API" in s
        for i, line in enumerate(s.splitlines(), 1):
            # redirect on failure inside API surface
            if is_api and re.search(r"redirect\s*\(|back\s*\(\s*\)", line):
                out.append(_finding("RED", 1, p, i, "API surface uses redirect/back() — must return 422 JSON"))
            # catch that returns a redirect anywhere near validation
            if "ValidationException" in line and "render" not in s:
                pass
        # FormRequest overriding failedValidation with redirect
        if "extends FormRequest" in s and "failedValidation" in s and "redirect" in s:
            out.append(_finding("RED", 1, p, 1, "FormRequest failedValidation redirects — breaks JSON 422 for toasts"))
    return _rel(out, directory)


# ── Rule 2 ──────────────────────────────────────────────────────────────────
def check_flutter_swallows(directory):
    """Every Dart network catch must map via ApiException.fromDioError — no silent swallow."""
    out = []
    for p in _walk(directory, (".dart",)):
        if "/test/" in str(p):
            continue
        s = _read(p)
        lines = s.splitlines()
        for i, line in enumerate(lines, 1):
            if re.search(r"catch\s*\(\s*e\b", line) or "on DioException" in line:
                # look ahead 6 lines for the mapper or an empty body
                block = "\n".join(lines[i - 1:i + 6])
                if "fromDioError" in block:
                    continue
                if re.search(r"catch\s*\(\s*_?\s*\)\s*\{\s*\}", block):
                    out.append(_finding("RED", 2, p, i, "empty catch — silent failure"))
                elif "DioException" in block or "dio" in s[:600].lower() or "Dio" in block:
                    out.append(_finding("RED", 2, p, i, "network catch without ApiException.fromDioError"))
                elif re.search(r"statusCode|response\?\.", block):
                    out.append(_finding("YEL", 2, p, i, "catch inspects status manually — prefer ApiException.fromDioError"))
    return _rel(out, directory)


# ── Rule 3 ──────────────────────────────────────────────────────────────────
def verify_admin_gates(directory):
    """/admin/* must sit behind auth middleware and survive 503 maintenance."""
    out = []
    for p in _walk(directory, (".php",)):
        name = p.name
        if name not in ("web.php", "api.php") and "routes" not in str(p):
            continue
        s = _read(p)
        for i, line in enumerate(s.splitlines(), 1):
            if re.search(r"prefix\s*\(\s*['\"]admin", line):
                ctx = s[max(0, s.find(line) - 300): s.find(line) + 300]
                if not re.search(r"middleware\s*\(.*(auth|admin)", ctx):
                    out.append(_finding("RED", 3, p, i, "admin route group without auth/admin middleware nearby"))
        if "PreventRequestsDuringMaintenance" in s and "admin" in s and "except" not in s:
            out.append(_finding("YEL", 3, p, 1, "maintenance middleware present — verify /admin excepted or gated"))
    return _rel(out, directory)


# ── Rule 4 ──────────────────────────────────────────────────────────────────
def check_race_conditions(directory):
    """Unique constraints exist; follow-up migrations don't re-declare existing indexes."""
    out = []
    seen_unique = {}  # (table, index-key) -> first file
    for p in sorted(_walk(directory, (".php",))):
        if "migrations" not in str(p):
            continue
        s = _read(p)
        table = "?"
        for i, line in enumerate(s.splitlines(), 1):
            tm = re.search(r"Schema::(?:create|table)\s*\(\s*['\"]([\w]+)", line)
            if tm:
                table = tm.group(1)
            m = re.search(r"->unique\s*\(\s*(\[[^\]]*\]|'[^']*'|\"[^\"]*\")?", line)
            if m:
                key = (table, (m.group(1) or line.strip())[:80])
                if key in seen_unique:
                    out.append(_finding("RED", 4, p, i,
                        f"unique index re-declared (first in {seen_unique[key]}) — breaks fresh install"))
                else:
                    seen_unique[key] = p.name
        # money-ish create without unique/lock hints
        if re.search(r"create.*(transaction|wallet|payment|order)", s, re.I):
            if "->unique(" not in s and "unique(" not in s:
                out.append(_finding("YEL", 4, p, 1, "money table migration without any unique constraint — verify invariants"))
    # firstOrCreate on money models without surrounding lock
    for p in _walk(directory, (".php",)):
        if "app/" not in str(p).replace("\\", "/"):
            continue
        s = _read(p)
        for i, line in enumerate(s.splitlines(), 1):
            if re.search(r"(Transaction|Wallet|Payment)::firstOrCreate", line) and "lockForUpdate" not in s:
                out.append(_finding("YEL", 4, p, i, "firstOrCreate on money model without lockForUpdate — race window"))
    return _rel(out, directory)


# ── Rule 5 ──────────────────────────────────────────────────────────────────
def verify_financial_logic(directory):
    """buy >= sell enforced; spread vs margin not conflated; no naive float division of money."""
    out = []
    for p in _walk(directory, (".php", ".dart")):
        s = _read(p)
        rel = str(p)
        has_buy_sell = re.search(r"buy_?price|sell_?price", s, re.I)
        if has_buy_sell and p.suffix == ".php" and ("Request" in rel or "Controller" in rel):
            if not re.search(r"gte?:\s*sell|buy_price.*>=|Rule::.*sell|greater", s, re.I):
                out.append(_finding("YEL", 5, p, 1, "buy/sell prices handled without visible buy>=sell validation"))
        for i, line in enumerate(s.splitlines(), 1):
            if re.search(r"(margin|هامش).*(spread|فارق)|(spread|فارق).*(margin|هامش)", line, re.I):
                out.append(_finding("YEL", 5, p, i, "spread & margin on same line — verify fields not conflated"))
            if re.search(r"(amount|balance|price)\s*/\s*100\b", line):
                out.append(_finding("YEL", 5, p, i, "money ÷100 — verify true-scale (SYP no-cents trap)"))
    return _rel(out, directory)


# ── Rule 6 ──────────────────────────────────────────────────────────────────
def verify_api_contracts(directory):
    """Webhook shape handling + null-accessor traps + Flutter payload keys vs PHP rules."""
    out = []
    php_rules, dart_payloads = {}, {}
    for p in _walk(directory, (".php",)):
        s = _read(p)
        for i, line in enumerate(s.splitlines(), 1):
            # null-accessor trap: ->user->name (User has no name column)
            if re.search(r"->user->name\b", line):
                out.append(_finding("RED", 6, p, i, "->user->name — User has first/last_name only, silently null"))
            # webhook handler trusting flat payload without msg unwrap
            if "webhook" in str(p).lower() and re.search(r"\$payload\[['\"]amount", line):
                if "msg" not in s:
                    out.append(_finding("YEL", 6, p, i, "webhook reads flat amount — CCPayment nests under msg + omits amount"))
        for m in re.finditer(r"'([a-z_]{3,})'\s*=>\s*'(required|nullable)[^']*'", s):
            php_rules.setdefault(m.group(1), str(p))
    for p in _walk(directory, (".dart",)):
        s = _read(p)
        for m in re.finditer(r"data:\s*\{([^}]*)\}", s):
            for k in re.findall(r"'([a-z_]{3,})'\s*:", m.group(1)):
                dart_payloads.setdefault(k, str(p))
    # payload keys mobile sends that no PHP rule mentions (heuristic)
    orphans = [k for k in dart_payloads if k not in php_rules and "_" in k]
    for k in orphans[:10]:
        out.append(_finding("YEL", 6, Path(dart_payloads[k]), 1, f"mobile sends '{k}' — no matching PHP validation rule found (verify contract)"))
    return _rel(out, directory)


# ── Rule 7 ──────────────────────────────────────────────────────────────────
TIER_A_HINTS = re.compile(r"wallet|payment|transaction|deposit|withdraw|balance|payroll|salary|gold|card|fee", re.I)

def audit_coverage_gate(directory):
    """Tier-A money files must clear ADR-004 ≥90%.

    Coverage is AUTHORITATIVE from clover.xml when present (per-file %). Only when
    NO coverage report exists do we fall back to a name/token heuristic — and that
    fallback is 🟡 (verify), never 🔴, because a test can exercise a controller via
    its routes without ever naming the class (the PayrollController false-positive).
    """
    out = []
    directory = Path(directory)
    all_files = list(_walk(directory, (".php", ".dart")))

    def _is_test(sp):
        return ("/tests/" in sp or "/test/" in sp
                or sp.endswith("_test.dart") or sp.endswith("Test.php"))

    # ---- Authoritative path: clover.xml per-file coverage ----
    clover = list(directory.rglob("clover.xml"))[:3]
    covered_files = {}          # lowercased basename -> pct (from clover)
    global_reported = False
    for cov in clover:
        s = _read(cov)
        for fm in re.finditer(r'<file[^>]*name="([^"]+)"[^>]*>(.*?)</file>', s, re.S):
            name = Path(fm.group(1)).name.lower()
            mm = re.search(r'<metrics[^>]*statements="(\d+)"[^>]*coveredstatements="(\d+)"', fm.group(2))
            if mm and int(mm.group(1)):
                covered_files[name] = 100 * int(mm.group(2)) / int(mm.group(1))
        gm = re.search(r'<metrics[^>]*statements="(\d+)"[^>]*coveredstatements="(\d+)"', s)
        if gm and int(gm.group(1)):
            global_reported = True

    tierA_src = [p for p in all_files
                 if not _is_test(str(p).replace("\\", "/"))
                 and "migrations" not in str(p) and "seeders" not in str(p)
                 and any(k in str(p).replace("\\", "/") for k in ("app/Services", "app/Http/Controllers", "/repositories/"))
                 and TIER_A_HINTS.search(p.stem)]

    if covered_files:
        # Authoritative: report Tier-A files below the 90% bar.
        for p in tierA_src:
            pct = covered_files.get((p.name).lower())
            if pct is not None and pct < 90:
                out.append(_finding("RED", 7, p, 1,
                    f"Tier-A '{p.stem}' coverage {pct:.0f}% < 90% (clover) — ADR-004"))
        return _rel(out, directory)

    # ---- Fallback heuristic (no coverage report): token/name match, 🟡 only ----
    test_blob = ""
    test_paths = ""
    for p in all_files:
        sp = str(p).replace("\\", "/")
        if _is_test(sp):
            test_blob += p.stem.lower() + "\n" + _read(p).lower() + "\n"   # FULL file, not [:2000]
            test_paths += sp.lower() + "\n"
    for p in tierA_src:
        stem = p.stem.lower()
        tok_m = TIER_A_HINTS.search(p.stem)
        tok = tok_m.group(0).lower() if tok_m else ""
        # Covered if the class is named in any test, OR a test dir/file PATH is
        # scoped to this file's Tier-A token (e.g. tests/Feature/Payroll covers
        # Payroll*). Body-token matching is deliberately NOT used — "payment" etc.
        # appear in unrelated test bodies and would mask genuinely untested files.
        covered = stem in test_blob or (tok and f"/{tok}" in test_paths)
        if not covered:
            out.append(_finding("YEL", 7, p, 1,
                f"Tier-A '{p.stem}' — no test clearly references it (heuristic; run --coverage to confirm) — ADR-004"))
    return _rel(out, directory)


# ── Aggregate ───────────────────────────────────────────────────────────────
CHECKS = [check_422_responses, check_flutter_swallows, verify_admin_gates,
          check_race_conditions, verify_financial_logic, verify_api_contracts,
          audit_coverage_gate]

def run_all(directory, rules=None):
    findings = []
    for idx, fn in enumerate(CHECKS, 1):
        if rules and idx not in rules:
            continue
        findings.extend(fn(directory))
    findings.sort(key=lambda f: (f["sev"] != "RED", f["rule"], f["file"]))
    return findings


def report(findings):
    red = [f for f in findings if f["sev"] == "RED"]
    yel = [f for f in findings if f["sev"] == "YEL"]
    lines = [f"# SEV report — {len(red)} 🔴 blockers · {len(yel)} 🟡 nits", ""]
    if red:
        lines.append("## 🔴 Blockers (steel-rule breaches)")
        lines += [f"- R{f['rule']} · `{f['file']}:{f['line']}` — {f['msg']}" for f in red]
        lines.append("")
    if yel:
        lines.append("## 🟡 Nits / verify")
        lines += [f"- R{f['rule']} · `{f['file']}:{f['line']}` — {f['msg']}" for f in yel]
    if not findings:
        lines.append("clean — no static breaches (semantic review still required)")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: sofi_automator.py <project_dir> [--rule N] [--json]")
    target = sys.argv[1]
    rules = None
    if "--rule" in sys.argv:
        rules = {int(sys.argv[sys.argv.index("--rule") + 1])}
    fs = run_all(target, rules)
    if "--json" in sys.argv:
        print(json.dumps(fs, ensure_ascii=False, indent=1))
    else:
        print(report(fs))
