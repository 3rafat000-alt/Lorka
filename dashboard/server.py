#!/usr/bin/env python3
"""
SOFI v5 — Live Observability Dashboard backend.

Reads the REAL v5 data sources (never fabricates) and serves them over HTTP + a
WebSocket live stream:
  - node graph      : the 30-agent roster + tier-isolation edges (sofi_tools.tickets)
  - budgets         : engine/routing/routing.yaml (routes · effort_scaling · budgeted_autonomy)
  - tasks           : the ticket queue per project (HANDOFFS.md via sofi_tools.tickets)
  - gates           : sofi_tools.gates validators (no-skip · artifacts · tier · evidence)
  - reflection      : reflection_engine.scan() (C2 dreaming candidates)
  - live activity   : tails .claude/memory/sessions.jsonl + audit.jsonl + per-PRJ _runlog.md

Grounding (C1): we surface configured budget ENVELOPES (real, from routing.yaml) and real
activity EVENT COUNTS (from logs) — we do NOT invent a live token-cost meter the system
does not actually measure. Anything derived is labelled `estimated`.

Run:  python3 dashboard/server.py [--port 8787]
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import pathlib
import re
import shutil
import sys
import time
import uuid
from collections import deque

# ── wire in sofi_tools (the real data layer) ─────────────────────────────────
_HERE = pathlib.Path(__file__).resolve().parent
_ROOT = _HERE.parent                                   # /home/es3dlll/Desktop/Lorka
_TOOLING = _ROOT / "engine" / "tooling"
sys.path.insert(0, str(_TOOLING))
sys.path.insert(0, str(_ROOT / "engine" / "tooling" / "agents" / "ceo"))

try:
    from sofi_tools import tickets, gates, brain, paths  # noqa: E402
    _HAVE_TOOLS = True
except Exception as e:  # degrade gracefully; the UI shows the error rather than lying
    print(f"[warn] sofi_tools import failed: {e}", file=sys.stderr)
    _HAVE_TOOLS = False

try:
    import reflection_engine  # noqa: E402
    _HAVE_REFLECT = True
except Exception:
    _HAVE_REFLECT = False

sys.path.insert(0, str(_HERE))
try:
    import project_reader  # noqa: E402  — rich per-project real-brain reader
    _HAVE_READER = True
except Exception as e:
    print(f"[warn] project_reader import failed: {e}", file=sys.stderr)
    _HAVE_READER = False

import yaml  # noqa: E402
from fastapi import FastAPI, WebSocket, WebSocketDisconnect  # noqa: E402
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

ROUTING = _ROOT / "engine" / "routing" / "routing.yaml"
ROSTER = _ROOT / "engine" / "ROSTER.md"
MEM = _ROOT / ".claude" / "memory"
SESSIONS = MEM / "sessions.jsonl"
AUDIT = MEM / "audit.jsonl"

# Human-readable tier labels for the graph.
TIER_LABEL = {
    "ceo": "Executive", "0": "Strategy", "1": "Architecture",
    "2": "Development", "3": "Quality", "4": "Infrastructure",
}
TIER_COLOR = {  # matches index.html accent spectrum
    "ceo": "#f472b6", "advisor": "#fbbf24", "0": "#07c4a7", "1": "#34d399",
    "2": "#06b89d", "3": "#22d3ee", "4": "#a78bfa",
}

app = FastAPI(title="SOFI v5 Observability")


# ── data builders ────────────────────────────────────────────────────────────
def load_routing() -> dict:
    if not ROUTING.exists():
        return {}
    try:
        return yaml.safe_load(ROUTING.read_text(encoding="utf-8")) or {}
    except Exception as e:
        return {"_error": str(e)}


def _budget_range(b: str) -> tuple[int | None, int | None]:
    """'8k-15k' -> (8000,15000); 'as-needed'/'per-diff' -> (None,None)."""
    m = re.findall(r"(\d+)\s*([kK]?)", b or "")
    vals = [int(n) * (1000 if k.lower() == "k" else 1) for n, k in m]
    if not vals:
        return (None, None)
    return (vals[0], vals[-1] if len(vals) > 1 else vals[0])


def build_graph() -> dict:
    """Nodes = 30 agents (tier·role·route·budget·gate). Edges = legal tier-isolation
    handoff channels (intra-tier direct + specialist↔own-advisor + advisor↔advisor + CEO)."""
    rt = load_routing()
    routes = rt.get("routes", {})
    models = rt.get("models", {})
    if not _HAVE_TOOLS:
        return {"nodes": [], "edges": [], "error": "sofi_tools unavailable"}

    role_tier = tickets.ROLE_TIER            # slug -> "0".."4"/"ceo"
    advisor_tier = tickets.ADVISOR_TIER      # advisor slug -> gated tier

    nodes = []

    def add(slug, kind, tier):
        r = routes.get(slug, {})
        lo, hi = _budget_range(r.get("budget", ""))
        mdl = r.get("model", "")
        nodes.append({
            "data": {
                "id": slug, "label": slug.replace("-", " "), "slug": slug,
                "kind": kind, "tier": tier, "tierLabel": TIER_LABEL.get(tier, tier),
                "color": TIER_COLOR.get("advisor" if kind == "advisor" else tier, "#07c4a7"),
                "model": mdl, "modelId": models.get(mdl, {}).get("id", ""),
                "effort": r.get("effort", ""), "caveman": r.get("caveman", ""),
                "gate": str(r.get("gate", "")), "budget": r.get("budget", ""),
                "budgetLo": lo, "budgetHi": hi,
            }
        })

    add("ceo-sofi", "ceo", "ceo")
    for slug, tier in advisor_tier.items():
        add(slug, "advisor", tier)
    for slug, tier in role_tier.items():
        if slug == "ceo-sofi":
            continue
        add(slug, "specialist", tier)

    # Edges: the LEGAL handoff channels the tier-isolation rule permits.
    edges = []
    specialists_by_tier: dict[str, list[str]] = {}
    for slug, tier in role_tier.items():
        if slug == "ceo-sofi":
            continue
        specialists_by_tier.setdefault(tier, []).append(slug)

    adv_of = {tier: slug for slug, tier in advisor_tier.items()}

    # CEO <-> every advisor (council)
    for slug in advisor_tier:
        edges.append({"data": {"id": f"ceo-{slug}", "source": "ceo-sofi",
                                "target": slug, "kind": "council"}})
    # advisor <-> advisor (cross-tier gateway chain, tier order 0..4)
    order = [adv_of[t] for t in ["0", "1", "2", "3", "4"] if t in adv_of]
    for a, b in zip(order, order[1:]):
        edges.append({"data": {"id": f"{a}-{b}", "source": a, "target": b, "kind": "gateway"}})
    # specialist <-> own tier advisor
    for tier, specs in specialists_by_tier.items():
        adv = adv_of.get(tier)
        if not adv:
            continue
        for s in specs:
            edges.append({"data": {"id": f"{adv}-{s}", "source": adv, "target": s, "kind": "assign"}})
    return {"nodes": nodes, "edges": edges,
            "tiers": TIER_LABEL, "colors": TIER_COLOR}


def build_budgets() -> dict:
    rt = load_routing()
    routes = rt.get("routes", {})
    out = []
    for slug, r in routes.items():
        lo, hi = _budget_range(r.get("budget", ""))
        out.append({"slug": slug, "model": r.get("model", ""), "effort": r.get("effort", ""),
                    "caveman": r.get("caveman", ""), "gate": str(r.get("gate", "")),
                    "budget": r.get("budget", ""), "lo": lo, "hi": hi})
    return {
        "version": rt.get("version"),
        "models": rt.get("models", {}),
        "routes": out,
        "effort_scaling": rt.get("effort_scaling", {}),
        "budgeted_autonomy": rt.get("budgeted_autonomy", {}),
        "activity": activity_counts(),   # real event counts (proxy for live usage; labelled estimated in UI)
    }


def list_projects() -> list[str]:
    if not _HAVE_TOOLS:
        return []
    try:
        return paths.list_projects()
    except Exception:
        pd = _ROOT / "projects"
        return sorted(p.name for p in pd.iterdir()
                      if p.is_dir() and (p / "_context").is_dir()) if pd.exists() else []


def build_tasks(prj: str) -> dict:
    """v5.1: parse HANDOFFS in ALL real formats (TKT blocks + freeform dispatch tables +
    Blocker entries) via project_reader, so the Task Manager reflects what the team is
    actually doing — not just the rigid TKT format most projects don't use."""
    if _HAVE_READER:
        try:
            rows = project_reader.handoff_tasks(prj)
            return {"tickets": rows, "count": len(rows),
                    "done": sum(1 for r in rows if r.get("marker") == "done"),
                    "open": sum(1 for r in rows if r.get("marker") in ("open", "info")),
                    "blocked": sum(1 for r in rows if r.get("marker") == "warn")}
        except Exception as e:
            return {"tickets": [], "error": str(e)}
    if not _HAVE_TOOLS:
        return {"tickets": [], "error": "sofi_tools unavailable"}
    try:
        ts = tickets.parse(prj)
    except Exception as e:
        return {"tickets": [], "error": str(e)}
    rows = [{"id": t.id, "gate": t.gate, "agent": t.to, "title": t.task,
             "status": t.status, "type": t.field("type"),
             "marker": "done" if t.is_done else "open"} for t in ts]
    return {"tickets": rows, "count": len(rows)}


def build_observatory(prj: str) -> dict:
    if not _HAVE_READER:
        return {"error": "project_reader unavailable"}
    try:
        return project_reader.observatory(prj)
    except Exception as e:
        return {"error": str(e)}


def build_gates(prj: str) -> dict:
    if not _HAVE_TOOLS:
        return {"error": "sofi_tools unavailable"}
    try:
        return {
            "no_skip": gates.validate_no_skip(prj),
            "artifacts": gates.validate_artifacts(prj),
            "tier_boundary": gates.validate_tier_boundary(prj),
            "evidence": gates.validate_evidence(prj),
            "gate_roles": gates.GATE_ROLES,
        }
    except Exception as e:
        return {"error": str(e)}


def build_reflection(prj: str) -> dict:
    if not (_HAVE_TOOLS and _HAVE_REFLECT):
        return {"candidates": [], "error": "reflection engine unavailable"}
    try:
        return {"candidates": reflection_engine.scan(prj)}
    except Exception as e:
        return {"candidates": [], "error": str(e)}


def build_state(prj: str) -> dict:
    if not _HAVE_TOOLS:
        return {}
    try:
        return brain.read_state(prj)
    except Exception:
        return {}


def activity_counts() -> dict:
    """Real per-agent + per-project event counts from sessions.jsonl. This is the honest
    proxy for 'live usage' — the framework has no token meter, so we count actual logged
    activity rather than fabricate cost numbers (grounding C1)."""
    by_agent: dict[str, int] = {}
    by_project: dict[str, int] = {}
    total = 0
    if SESSIONS.exists():
        for line in SESSIONS.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except Exception:
                continue
            total += 1
            a = e.get("active_agent") or e.get("agent") or "unknown"
            p = e.get("project") or e.get("prj") or "unknown"
            by_agent[a] = by_agent.get(a, 0) + 1
            by_project[p] = by_project.get(p, 0) + 1
    return {"total_events": total, "by_agent": by_agent, "by_project": by_project}


# ── HTTP endpoints ───────────────────────────────────────────────────────────
@app.get("/api/graph")
def api_graph():
    return JSONResponse(build_graph())


@app.get("/api/budgets")
def api_budgets():
    return JSONResponse(build_budgets())


@app.get("/api/projects")
def api_projects():
    return JSONResponse({"projects": list_projects()})


@app.get("/api/tasks")
def api_tasks(prj: str):
    return JSONResponse(build_tasks(prj))


@app.get("/api/observatory")
def api_observatory(prj: str):
    return JSONResponse(build_observatory(prj))


@app.get("/api/gates")
def api_gates(prj: str):
    return JSONResponse(build_gates(prj))


@app.get("/api/reflection")
def api_reflection(prj: str):
    return JSONResponse(build_reflection(prj))


@app.get("/api/state")
def api_state(prj: str):
    return JSONResponse(build_state(prj))


@app.get("/api/snapshot")
def api_snapshot(prj: str | None = None):
    """One call the UI hits on load: graph + budgets + projects + (per-project brain)."""
    projects = list_projects()
    prj = prj or (projects[0] if projects else None)
    snap = {"graph": build_graph(), "budgets": build_budgets(),
            "projects": projects, "active_project": prj, "server_time": time.time()}
    if prj:
        snap.update({"tasks": build_tasks(prj), "gates": build_gates(prj),
                     "reflection": build_reflection(prj), "state": build_state(prj),
                     "observatory": build_observatory(prj)})
    return JSONResponse(snap)


# ── safe diagnostics runner ──────────────────────────────────────────────────
SOFI_BIN = _TOOLING / "bin" / "sofi"
# Whitelist ONLY — read-only diagnostics. Never arbitrary exec: the action key
# selects a fixed argv, and prj is validated against the real project list.
DIAG_ACTIONS = {"doctor": False, "git-check": True, "gate-check": True}  # value = needs prj


@app.post("/api/diag/{action}")
async def api_diag(action: str, prj: str | None = None):
    if action not in DIAG_ACTIONS:
        return JSONResponse({"ok": False, "error": f"unknown action: {action}"}, status_code=400)
    argv = [str(SOFI_BIN), action]
    if DIAG_ACTIONS[action]:
        if not prj or prj not in list_projects():
            return JSONResponse({"ok": False, "error": f"invalid prj: {prj}"}, status_code=400)
        argv.append(prj)
    t0 = time.time()
    proc = None
    try:
        proc = await asyncio.create_subprocess_exec(
            *argv, cwd=str(_ROOT),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=90)
        text = out.decode("utf-8", errors="ignore")
    except asyncio.TimeoutError:
        if proc:
            proc.kill()
        return JSONResponse({"ok": False, "error": "timeout (90s)"}, status_code=504)
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
    return JSONResponse({"ok": proc.returncode == 0, "exit": proc.returncode,
                         "action": action, "prj": prj, "output": text,
                         "took": round(time.time() - t0, 2)})


# ── Claude Code command palette runner (headless, whitelisted) ──────────────
# Executes /sofi-* skills directly via `claude -p` and streams the run live to
# the dashboard. Safety model: (1) whitelist of command slugs — never arbitrary
# prompts; (2) argv exec, no shell; (3) args validated per-policy; (4) server
# binds 127.0.0.1 only; (5) SOFI PreToolUse guard hooks stay active inside the
# headless session (dangerous commands, secrets, bad commits stay blocked).
CLAUDE_BIN = shutil.which("claude") or str(pathlib.Path.home() / ".local" / "bin" / "claude")

PALETTE: dict[str, dict] = {
    "sofi-boot":        {"arg": "none",   "icon": "🚀", "label_ar": "إقلاع وتوجيه"},
    "sofi-team":        {"arg": "none",   "icon": "👥", "label_ar": "الفريق — من يفعل ماذا"},
    "sofi-gate":        {"arg": "none",   "icon": "⛩",  "label_ar": "فحص البوابة والتقدّم"},
    "sofi-audit":       {"arg": "choice", "icon": "🔍", "label_ar": "تدقيق طبقة",
                         "choices": ["all", "ui", "blade", "css", "js", "db", "api", "integration", "agents"]},
    "sofi-secure":      {"arg": "choice", "icon": "🛡",  "label_ar": "الفرقة الأمنية",
                         "choices": ["scan", "threat", "pentest", "verify"]},
    "sofi-report":      {"arg": "choice", "icon": "📋", "label_ar": "تقرير موثّق",
                         "choices": ["audit", "security", "status"]},
    "sofi-fix":         {"arg": "text",   "icon": "🔧", "label_ar": "إصلاح الملاحظات", "hint": "الهدف — طبقة أو تقرير"},
    "sofi-feature":     {"arg": "text",   "icon": "⚙",  "label_ar": "الحلقة الكاملة على ميزة", "hint": "اسم الميزة"},
    "sofi-spec-review": {"arg": "text",   "icon": "🏛",  "label_ar": "مراجعة معمارية 4 أركان", "hint": "اسم الميزة"},
    "sofi-delegate":    {"arg": "text",   "icon": "📨", "label_ar": "بناء تفويض RCCF", "hint": "<agent> <task>"},
    "sofi-reflect":     {"arg": "none",   "icon": "🌙", "label_ar": "التأمّل واستخلاص الدروس"},
    "sofi-handoff":     {"arg": "none",   "icon": "🤝", "label_ar": "تسليم منضبط"},
}
# free-text args: word chars + Arabic + space/-/./:  · no leading dash (no flag smuggling)
_ARG_OK = re.compile(r"^[\w؀-ۿ][\w؀-ۿ\s\-./:]{0,119}$")

RUNS: dict[str, dict] = {}      # run_id -> {cmd,arg,prompt,status,t0,lines,proc,exit}
RUN_LOCK = asyncio.Lock()
WS_QUEUES: set[asyncio.Queue] = set()
MAX_LINES = 3000
RUN_TIMEOUT = 1800              # 30 min hard kill


def _broadcast(ev: dict) -> None:
    for q in list(WS_QUEUES):
        try:
            q.put_nowait(ev)
        except Exception:
            pass


def _condense(ev: dict) -> list[dict]:
    """stream-json event -> 0..n compact UI events."""
    t = ev.get("type")
    if t == "system" and ev.get("subtype") == "init":
        return [{"kind": "init", "model": ev.get("model", "")}]
    if t == "assistant":
        out = []
        for b in (ev.get("message") or {}).get("content") or []:
            if b.get("type") == "text" and (b.get("text") or "").strip():
                out.append({"kind": "text", "text": b["text"][:4000]})
            elif b.get("type") == "tool_use":
                inp = json.dumps(b.get("input") or {}, ensure_ascii=False)[:160]
                out.append({"kind": "tool", "name": b.get("name", "?"), "input": inp})
        return out
    if t == "result":
        return [{"kind": "result", "ok": not ev.get("is_error"),
                 "result": (ev.get("result") or "")[:6000],
                 "turns": ev.get("num_turns"),
                 "secs": round((ev.get("duration_ms") or 0) / 1000, 1)}]
    return []


async def _watchdog(run_id: str) -> None:
    await asyncio.sleep(RUN_TIMEOUT)
    r = RUNS.get(run_id)
    if r and r["status"] == "running":
        try:
            r["proc"].kill()
        except Exception:
            pass
        r["status"] = "timeout"


async def _pump(run_id: str) -> None:
    r = RUNS[run_id]
    proc = r["proc"]
    try:
        while True:
            raw = await proc.stdout.readline()
            if not raw:
                break
            line = raw.decode("utf-8", errors="ignore").strip()
            if not line:
                continue
            try:
                items = _condense(json.loads(line))
            except Exception:
                # non-JSON (CLI error text merged from stderr) — surface it raw
                items = [{"kind": "text", "text": line[:500]}]
            for it in items:
                it = {"type": "claude", "run": run_id, "cmd": r["cmd"], **it, "ts": time.time()}
                r["lines"].append(it)
                _broadcast(it)
                if it["kind"] == "result":
                    r["status"] = "done" if it["ok"] else "error"
        rc = await proc.wait()
        r["exit"] = rc
        if r["status"] == "running":
            r["status"] = "done" if rc == 0 else "error"
    except Exception as e:
        r["status"] = "error"
        err = {"type": "claude", "run": run_id, "cmd": r["cmd"],
               "kind": "text", "text": f"[runner error] {e}", "ts": time.time()}
        r["lines"].append(err)
        _broadcast(err)
    finally:
        fin = {"type": "claude", "run": run_id, "cmd": r["cmd"], "kind": "status",
               "status": r["status"], "exit": r.get("exit"),
               "took": round(time.time() - r["t0"], 1), "ts": time.time()}
        r["lines"].append(fin)
        _broadcast(fin)


@app.get("/api/palette")
def api_palette():
    return JSONResponse({"commands": PALETTE,
                         "claude": pathlib.Path(CLAUDE_BIN).exists()})


@app.post("/api/claude/run")
async def api_claude_run(payload: dict):
    cmd = (payload or {}).get("cmd", "")
    arg = ((payload or {}).get("arg") or "").strip()
    spec = PALETTE.get(cmd)
    if not spec:
        return JSONResponse({"ok": False, "error": f"unknown command: {cmd}"}, status_code=400)
    if spec["arg"] == "none":
        arg = ""
    elif spec["arg"] == "choice":
        if arg not in spec["choices"]:
            return JSONResponse({"ok": False, "error": f"arg must be one of {spec['choices']}"},
                                status_code=400)
    else:  # text
        if not arg or not _ARG_OK.match(arg):
            return JSONResponse({"ok": False,
                                 "error": "arg required — letters/digits/spaces, max 120, no leading dash"},
                                status_code=400)
    if not pathlib.Path(CLAUDE_BIN).exists():
        return JSONResponse({"ok": False, "error": "claude CLI not found on server"}, status_code=500)
    async with RUN_LOCK:
        if any(r["status"] == "running" for r in RUNS.values()):
            return JSONResponse({"ok": False, "error": "run already in progress — one at a time"},
                                status_code=409)
        prompt = f"/{cmd} {arg}".strip()
        run_id = uuid.uuid4().hex[:10]
        proc = await asyncio.create_subprocess_exec(
            CLAUDE_BIN, "-p", prompt, "--output-format", "stream-json", "--verbose",
            "--permission-mode", "bypassPermissions",
            cwd=str(_ROOT),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
            env={**os.environ, "SOFI_DASH_RUN": run_id})
        RUNS[run_id] = {"cmd": cmd, "arg": arg, "prompt": prompt, "status": "running",
                        "t0": time.time(), "lines": deque(maxlen=MAX_LINES),
                        "proc": proc, "exit": None}
        asyncio.create_task(_pump(run_id))
        asyncio.create_task(_watchdog(run_id))
    started = {"type": "claude", "run": run_id, "cmd": cmd, "kind": "started",
               "prompt": prompt, "ts": time.time()}
    RUNS[run_id]["lines"].append(started)
    _broadcast(started)
    return JSONResponse({"ok": True, "run": run_id, "prompt": prompt})


@app.post("/api/claude/stop")
async def api_claude_stop(payload: dict):
    run_id = (payload or {}).get("run", "")
    r = RUNS.get(run_id)
    if not r:
        return JSONResponse({"ok": False, "error": "unknown run"}, status_code=404)
    if r["status"] == "running" and r["proc"]:
        try:
            r["proc"].kill()
        except ProcessLookupError:
            pass
        r["status"] = "stopped"
    return JSONResponse({"ok": True, "run": run_id, "status": r["status"]})


@app.get("/api/claude/runs")
def api_claude_runs():
    return JSONResponse({"runs": [
        {"run": k, "cmd": r["cmd"], "arg": r["arg"], "status": r["status"],
         "t0": r["t0"], "exit": r["exit"], "n": len(r["lines"])}
        for k, r in sorted(RUNS.items(), key=lambda kv: -kv[1]["t0"])][:20]})


@app.get("/api/claude/log")
def api_claude_log(run: str):
    r = RUNS.get(run)
    if not r:
        return JSONResponse({"ok": False, "error": "unknown run"}, status_code=404)
    return JSONResponse({"ok": True, "run": run, "status": r["status"], "lines": list(r["lines"])})


# ── WebSocket live stream ────────────────────────────────────────────────────
def _tail_new(path: pathlib.Path, pos: int) -> tuple[list[str], int]:
    if not path.exists():
        return [], pos
    size = path.stat().st_size
    if size < pos:      # rotated/truncated
        pos = 0
    if size == pos:
        return [], pos
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        f.seek(pos)
        chunk = f.read()
        return [l for l in chunk.splitlines() if l.strip()], f.tell()


def _runlogs() -> list[pathlib.Path]:
    out = []
    pd = _ROOT / "projects"
    if pd.exists():
        for p in pd.iterdir():
            rl = p / "_context" / "_runlog.md"
            if rl.exists():
                out.append(rl)
    return out


@app.websocket("/ws")
async def ws(sock: WebSocket):
    await sock.accept()
    # per-client queue for claude-run events (pushed by _broadcast)
    claude_q: asyncio.Queue = asyncio.Queue(maxsize=500)
    WS_QUEUES.add(claude_q)
    # seek to current end so we stream only NEW events
    pos = {SESSIONS: SESSIONS.stat().st_size if SESSIONS.exists() else 0,
           AUDIT: AUDIT.stat().st_size if AUDIT.exists() else 0}
    runlog_pos = {rl: rl.stat().st_size for rl in _runlogs()}
    await sock.send_json({"type": "hello", "server_time": time.time(),
                          "sources": {"sessions": SESSIONS.exists(), "audit": AUDIT.exists(),
                                      "runlogs": len(runlog_pos)}})
    try:
        while True:
            events = []
            # claude command-palette stream — drain whatever arrived
            while True:
                try:
                    events.append(claude_q.get_nowait())
                except asyncio.QueueEmpty:
                    break
            # sessions.jsonl — the primary activity feed
            lines, pos[SESSIONS] = _tail_new(SESSIONS, pos[SESSIONS])
            for l in lines:
                try:
                    e = json.loads(l)
                    events.append({"type": "activity", "src": "session",
                                   "agent": e.get("active_agent") or "unknown",
                                   "project": e.get("project"), "gate": e.get("gate"),
                                   "event": e.get("event"), "raw": e, "ts": time.time()})
                except Exception:
                    pass
            # audit.jsonl — security/guard blocks
            lines, pos[AUDIT] = _tail_new(AUDIT, pos[AUDIT])
            for l in lines:
                try:
                    e = json.loads(l)
                    events.append({"type": "security", "src": "audit",
                                   "agent": e.get("agent"), "action": e.get("action"),
                                   "summary": e.get("summary"), "priority": e.get("priority"),
                                   "raw": e, "ts": time.time()})
                except Exception:
                    pass
            # per-project runlogs — real tool-run trace ("- when [role] action")
            for rl in _runlogs():
                p0 = runlog_pos.get(rl, 0)
                lines, runlog_pos[rl] = _tail_new(rl, p0)
                for l in lines:
                    m = re.match(r"-\s*(.+?)\s*\[(.+?)\]\s*(.+)", l.strip())
                    if m:
                        events.append({"type": "activity", "src": "runlog",
                                       "project": rl.parent.parent.name,
                                       "agent": m.group(2), "action": m.group(3),
                                       "when": m.group(1), "ts": time.time()})
            for ev in events:
                await sock.send_json(ev)
            # heartbeat so the client knows the stream is alive even when idle
            await sock.send_json({"type": "tick", "ts": time.time()})
            await asyncio.sleep(1.5)
    except WebSocketDisconnect:
        return
    except Exception:
        return
    finally:
        WS_QUEUES.discard(claude_q)


# ── static: the dashboard itself ─────────────────────────────────────────────
@app.get("/")
def index():
    return FileResponse(str(_HERE / "index.html"))


app.mount("/assets", StaticFiles(directory=str(_HERE / "assets")), name="assets")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--host", default="127.0.0.1")
    a = ap.parse_args()
    import uvicorn
    print(f"SOFI v5 dashboard → http://{a.host}:{a.port}  "
          f"(tools={_HAVE_TOOLS} reflect={_HAVE_REFLECT})")
    uvicorn.run(app, host=a.host, port=a.port, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
