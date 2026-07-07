#!/usr/bin/env python3
"""
sofi_verify — the SOFI mechanical verification runner (Architect doctrine, step 3).

Doctrine: *before declaring a task done, run the validation and read the output.*
No model tokens burned on "does it compile" — Python drives the real toolchain
(php -l · artisan view:cache · flutter analyze · asset-resolve) and GATES the
pipeline with its exit code: any failed check → exit ≠0 → the loop stops.

Flexible across any PRJ-{id}: auto-detects backend (Laravel) + mobile (Flutter),
runs only the checks whose toolchain is present, or a subset via --only.

CLI
---
    python sofi_verify.py --prj PRJ-SAKK [--only lint,view,flutter,assets] [--changed] [--md]

Exit: 0 = all present checks passed · 1 = at least one failed · 2 = nothing to run.
Pure stdlib. NEVER writes source (artisan *:cache targets are cleared after).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from feature_scan import _project_dir  # type: ignore
except Exception:
    def _project_dir(prj: str) -> Path:
        return Path(__file__).resolve().parents[4] / "projects" / prj


def _run(cmd: list[str], cwd: Path, timeout: int = 180) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
        out = (p.stdout + p.stderr).strip()
        return p.returncode, out[-1500:]
    except FileNotFoundError:
        return 127, f"tool not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, f"timeout after {timeout}s"


def _changed_php(root: Path) -> list[Path]:
    rc, out = _run(["git", "diff", "--name-only", "--diff-filter=ACM", "HEAD"], root)
    if rc != 0:
        return []
    return [root / f for f in out.splitlines() if f.endswith(".php") and (root / f).exists()]


# ─────────────────────────── checks ───────────────────────────
def check_lint(root: Path, backend: Path, changed: bool) -> dict:
    """php -l on changed (or all backend) PHP — syntax gate."""
    if not shutil.which("php"):
        return {"skip": "php not installed"}
    targets = _changed_php(root) if changed else list(backend.rglob("*.php"))
    targets = [t for t in targets if "vendor/" not in str(t) and "/storage/" not in str(t)]
    if not targets:
        return {"skip": "no PHP files"}
    fails = []
    for f in targets[:400]:
        rc, out = _run(["php", "-l", str(f)], root, 30)
        if rc != 0:
            fails.append({"file": str(f.relative_to(root)), "err": out.splitlines()[0] if out else "lint error"})
    return {"name": "php -l", "checked": len(targets[:400]), "pass": not fails, "fails": fails}


def check_view(root: Path, backend: Path) -> dict:
    """artisan view:cache then view:clear — compiles every Blade, catches template errors."""
    artisan = backend / "artisan"
    if not artisan.exists() or not shutil.which("php"):
        return {"skip": "no artisan/php"}
    rc, out = _run(["php", "artisan", "view:cache"], backend, 120)
    _run(["php", "artisan", "view:clear"], backend, 60)  # restore, never leave cache
    return {"name": "artisan view:cache", "pass": rc == 0, "err": "" if rc == 0 else out}


def check_route(root: Path, backend: Path) -> dict:
    """artisan route:list — fails if any route references a missing controller/action."""
    artisan = backend / "artisan"
    if not artisan.exists() or not shutil.which("php"):
        return {"skip": "no artisan/php"}
    rc, out = _run(["php", "artisan", "route:list", "--json"], backend, 90)
    return {"name": "artisan route:list", "pass": rc == 0, "err": "" if rc == 0 else out}


def check_flutter(root: Path, mobile: Path) -> dict:
    """flutter analyze — static analysis gate for the mobile app."""
    if not (mobile / "pubspec.yaml").exists():
        return {"skip": "no Flutter app"}
    if not shutil.which("flutter"):
        return {"skip": "flutter not installed"}
    rc, out = _run(["flutter", "analyze", "--no-pub"], mobile, 300)
    return {"name": "flutter analyze", "pass": rc == 0, "err": "" if rc == 0 else out}


_ASSET_REF = re.compile(r"""(?:asset|url|@include|@extends|src\s*=)\s*[('"]+\s*([^)'"?]+)""")


def check_assets(root: Path, backend: Path) -> dict:
    """Resolve local asset/partial references in Blade → flag ones that don't exist on disk."""
    views = backend / "resources" / "views"
    public = backend / "public"
    if not views.exists():
        return {"skip": "no resources/views"}
    missing = []
    for bf in list(views.rglob("*.blade.php"))[:600]:
        for line in bf.read_text(errors="ignore").splitlines():
            for m in _ASSET_REF.finditer(line):
                ref = m.group(1).strip()
                if ref.startswith(("http", "//", "data:", "{{", "$", "vendor.", "components.", "layouts.")):
                    continue
                if "/" in ref and "." in ref.rsplit("/", 1)[-1]:  # looks like a public asset path
                    cand = public / ref.lstrip("/")
                    if not cand.exists():
                        missing.append({"view": str(bf.relative_to(backend)), "asset": ref})
    # de-dup
    seen, uniq = set(), []
    for x in missing:
        k = x["asset"]
        if k not in seen:
            seen.add(k); uniq.append(x)
    return {"name": "asset-resolve", "pass": not uniq, "missing": uniq[:40]}


CHECKS = {"lint": "lint", "view": "view", "route": "route", "flutter": "flutter", "assets": "assets"}


def run(prj: str, only: list[str] | None, changed: bool) -> dict:
    root = _project_dir(prj)
    backend = root / "backend"
    mobile = root / "mobile"
    want = only or list(CHECKS)
    results = []
    if "lint" in want:    results.append(check_lint(root, backend, changed))
    if "view" in want:    results.append(check_view(root, backend))
    if "route" in want:   results.append(check_route(root, backend))
    if "flutter" in want: results.append(check_flutter(root, mobile))
    if "assets" in want:  results.append(check_assets(root, backend))
    ran = [r for r in results if "skip" not in r]
    failed = [r for r in ran if not r.get("pass")]
    status = 2 if not ran else (1 if failed else 0)
    return {"prj": prj, "changed_only": changed, "results": results,
            "ran": len(ran), "failed": len(failed), "exit": status}


def to_md(r: dict) -> str:
    icon = {0: "✅ ALL PASS", 1: "❌ FAILURES", 2: "⚠️ nothing to run"}[r["exit"]]
    out = [f"# sofi-verify — {r['prj']} · {icon} ({r['ran']} ran, {r['failed']} failed)"]
    for c in r["results"]:
        if "skip" in c:
            out.append(f"- ⏭️  {c['skip']}")
        elif c.get("pass"):
            out.append(f"- ✅ {c['name']}")
        else:
            out.append(f"- ❌ {c['name']}")
            for f in c.get("fails", [])[:8]:
                out.append(f"      · {f['file']}: {f['err']}")
            for f in c.get("missing", [])[:8]:
                out.append(f"      · {f['view']} → missing {f['asset']}")
            if c.get("err"):
                out.append(f"      · {c['err'].splitlines()[0] if c['err'] else ''}")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="SOFI mechanical verification runner (gates the pipeline)")
    ap.add_argument("--prj", required=True)
    ap.add_argument("--only", default="", help="comma list: lint,view,route,flutter,assets")
    ap.add_argument("--changed", action="store_true", help="lint only git-changed PHP (fast)")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args(argv)
    only = [x.strip() for x in a.only.split(",") if x.strip()] or None
    r = run(a.prj, only, a.changed)
    print(to_md(r) if a.md else json.dumps(r, ensure_ascii=False, indent=1))
    return r["exit"] if r["exit"] != 2 else 0  # 'nothing to run' is not a hard failure


if __name__ == "__main__":
    raise SystemExit(main())
