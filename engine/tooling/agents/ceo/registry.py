#!/usr/bin/env python3
"""
registry — the SOFI brain-layer artifact index (token-frugal, 0 model tokens).

Doctrine: *few token do trick* · *big brain, small mouth* (`engine/protocols/04-coordination-registry.md`).
The Registry (`projects/<PRJ>/_context/REGISTRY.md`) is a compact, append-only, one-line-per-
deliverable index the BRAIN LAYER scans to answer "what already exists, is it done, where, what
proves it" WITHOUT re-opening any artifact or re-reading a 154 KB HANDOFFS.md. Leaves never read it.

This tool does the deterministic registry work at 0 model tokens so the model spends tokens only on
judgment — the same standalone pattern as sofi_scan.py / sofi_verify.py.

CLI
---
    # record a deliverable (primary path: paste the leaf's `registry:` line verbatim; upsert by TKT)
    python3 registry.py add --prj PRJ-SAKK --line "TKT-0042 | g4 | backend-blade-engineer | DONE | app/Http/Controllers/API/AuthController.php | b0dbb45 | +214 | POST /auth/login, matches OpenAPI"
    # or build the line from fields
    python3 registry.py add --prj PRJ-SAKK --tkt TKT-0042 --gate 4 --agent backend-blade-engineer \
        --status DONE --path app/Http/Controllers/API/AuthController.php --sha b0dbb45 --delta +214 \
        --headline "POST /auth/login, matches OpenAPI"

    python3 registry.py list  --prj PRJ-SAKK [--status DONE] [--gate 4]   # scan the index (filtered)
    python3 registry.py find  --prj PRJ-SAKK "auth"                        # grep the index
    python3 registry.py verify --prj PRJ-SAKK <artifact-path>              # exists·bytes·words·sha (verify WITHOUT reading)
    python3 registry.py prune --prj PRJ-SAKK                               # report rows whose artifact is gone

Exit codes: 0 ok · 1 missing/verify-failed · 2 usage error. Pure stdlib. Writes only REGISTRY.md.
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

# ── workspace resolution (reuse sofi_tools when importable; fallback otherwise) ──
try:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tooling"))
    from sofi_tools import paths as _paths  # type: ignore

    def _context_dir(prj: str) -> Path:
        return _paths.context_dir(prj)

    def _project_dir(prj: str) -> Path:
        return _paths.project_dir(prj)
except Exception:  # standalone fallback
    def _project_dir(prj: str) -> Path:
        root = Path(__file__).resolve().parents[4]
        return root / "projects" / prj

    def _context_dir(prj: str) -> Path:
        return _project_dir(prj) / "_context"


HEADER = (
    "# REGISTRY — {prj}   (artifact index · brain-layer read only · append via registry.py)\n"
    "# fmt: TKT | gate | agent | status | artifact-path | sha | Δbytes | headline\n"
)
NCOLS = 8


def _registry_path(prj: str) -> Path:
    return _context_dir(prj) / "REGISTRY.md"


def _read(prj: str) -> tuple[list[str], list[str]]:
    """Return (header_comment_lines, data_rows). Auto-seeds a header if absent."""
    p = _registry_path(prj)
    if not p.exists():
        return HEADER.format(prj=prj).splitlines(), []
    header, rows = [], []
    for ln in p.read_text(encoding="utf-8").splitlines():
        s = ln.strip()
        if not s:
            continue
        (header if s.startswith("#") else rows).append(ln.rstrip())
    if not header:
        header = HEADER.format(prj=prj).splitlines()
    return header, rows


def _write(prj: str, header: list[str], rows: list[str]) -> Path:
    p = _registry_path(prj)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join([*header, *rows]) + "\n", encoding="utf-8")
    return p


def _tkt_of(row: str) -> str:
    return row.split("|", 1)[0].strip()


def _norm(line: str) -> str:
    """Normalize a raw registry line to ' TKT | ... ' with single spaces around pipes."""
    parts = [c.strip() for c in line.split("|")]
    if len(parts) < NCOLS:
        parts += [""] * (NCOLS - len(parts))
    elif len(parts) > NCOLS:  # headline may itself contain no pipes, but be defensive
        parts = parts[: NCOLS - 1] + [" | ".join(parts[NCOLS - 1:])]
    return " | ".join(parts)


def cmd_add(a: argparse.Namespace) -> int:
    if a.line:
        line = _norm(a.line)
    else:
        missing = [f for f in ("tkt", "agent", "status", "path") if not getattr(a, f)]
        if missing:
            print(f"add: need --line, or all of --tkt/--agent/--status/--path (missing: {missing})", file=sys.stderr)
            return 2
        gate = f"g{a.gate}" if a.gate and not str(a.gate).startswith("g") else (a.gate or "g?")
        line = _norm(
            f"{a.tkt} | {gate} | {a.agent} | {a.status.upper()} | {a.path} | "
            f"{a.sha or '—'} | {a.delta or '—'} | {a.headline or ''}"
        )
    tkt = _tkt_of(line)
    header, rows = _read(a.prj)
    replaced = False
    for i, r in enumerate(rows):
        if _tkt_of(r) == tkt:  # upsert: one deliverable = one row, updated in place
            rows[i] = line
            replaced = True
            break
    if not replaced:
        rows.insert(0, line)  # newest first
    p = _write(a.prj, header, rows)
    print(f"{'updated' if replaced else 'added'} {tkt} → {p}")
    return 0


def cmd_list(a: argparse.Namespace) -> int:
    header, rows = _read(a.prj)
    out = rows
    if a.status:
        out = [r for r in out if r.split("|")[3].strip().upper() == a.status.upper()] if len(rows) else out
    if a.gate:
        g = f"g{a.gate}".replace("gg", "g")
        out = [r for r in out if r.split("|")[1].strip() == g]
    print("\n".join(header))
    print("\n".join(out) if out else "(no matching rows)")
    return 0


def cmd_find(a: argparse.Namespace) -> int:
    _, rows = _read(a.prj)
    q = a.query.lower()
    hits = [r for r in rows if q in r.lower()]
    print("\n".join(hits) if hits else f"(no rows match '{a.query}')")
    return 0 if hits else 1


def _short_sha(path: Path, prj: str) -> str:
    """git short-sha of the last commit touching the file (in the project's OWN repo);
    fall back to a content hash prefixed '~' when untracked/unavailable."""
    try:
        repo = _paths.project_repo(prj)  # type: ignore[name-defined]
    except Exception:
        repo = _project_dir(prj)
    try:
        r = subprocess.run(
            ["git", "-C", str(repo), "log", "-1", "--format=%h", "--", str(path)],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    try:
        return "~" + hashlib.blake2b(path.read_bytes(), digest_size=4).hexdigest()
    except Exception:
        return "—"


def _resolve(prj: str, raw: str) -> Path:
    p = Path(raw)
    if p.is_absolute():
        return p
    # try project-relative, then context-relative
    cand = _project_dir(prj) / raw
    if cand.exists():
        return cand
    return _context_dir(prj) / raw


def cmd_verify(a: argparse.Namespace) -> int:
    p = _resolve(a.prj, a.path)
    if not p.exists():
        print(f"MISSING  {a.path}  (resolved: {p})")
        return 1
    data = p.read_bytes()
    words = len(p.read_text(encoding="utf-8", errors="replace").split())
    print(f"exists · {len(data)} bytes · {words} words · sha {_short_sha(p, a.prj)}  {p}")
    return 0


def cmd_prune(a: argparse.Namespace) -> int:
    _, rows = _read(a.prj)
    gone = []
    for r in rows:
        cols = r.split("|")
        if len(cols) < 5:
            continue
        path = cols[4].strip()
        if path and path not in ("—", "") and not _resolve(a.prj, path).exists():
            gone.append((_tkt_of(r), path))
    if not gone:
        print("all registry artifacts present")
        return 0
    print(f"{len(gone)} row(s) point at a missing artifact (review — not auto-deleted):")
    for tkt, path in gone:
        print(f"  {tkt} → {path}")
    return 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="registry.py", description="SOFI brain-layer artifact index (0 model tokens).")
    ap.add_argument("--prj", required=True, help="PRJ-ID (e.g. PRJ-SAKK)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("add", help="record/upsert a deliverable row (by TKT id)")
    pa.add_argument("--line", help="a full preformatted registry line (the leaf's `registry:` field) — verbatim")
    pa.add_argument("--tkt"); pa.add_argument("--gate"); pa.add_argument("--agent")
    pa.add_argument("--status"); pa.add_argument("--path"); pa.add_argument("--sha")
    pa.add_argument("--delta"); pa.add_argument("--headline")
    pa.set_defaults(fn=cmd_add)

    pl = sub.add_parser("list", help="scan the index (optionally filtered)")
    pl.add_argument("--status"); pl.add_argument("--gate")
    pl.set_defaults(fn=cmd_list)

    pf = sub.add_parser("find", help="grep the index")
    pf.add_argument("query")
    pf.set_defaults(fn=cmd_find)

    pv = sub.add_parser("verify", help="exists·bytes·words·sha for an artifact (verify WITHOUT reading)")
    pv.add_argument("path")
    pv.set_defaults(fn=cmd_verify)

    pp = sub.add_parser("prune", help="report rows whose artifact no longer exists")
    pp.set_defaults(fn=cmd_prune)

    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
