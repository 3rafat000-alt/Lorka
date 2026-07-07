# SOFI v6.1 — Live Observability Dashboard

A flexible multi-tab web console for watching the Company of Rooms in real time. It reads
the **real** v6 / v6.1 data sources (never fabricates) and streams live activity over a WebSocket.

## Run
```bash
dashboard/start.sh            # start  → http://127.0.0.1:8787
dashboard/start.sh status    # is it up?
dashboard/start.sh restart   # bounce it
dashboard/start.sh stop      # stop
```
Backend: `dashboard/server.py` (FastAPI + uvicorn + WebSocket — all pre-installed).
Frontend: `dashboard/index.html`, single self-contained page, design tokens matched to
the root `index.html` landing page. Node graph: vendored `assets/cytoscape.min.js` (offline-safe).

## Clean domain (optional) — `http://dashboard.local`
The Caddy vhost is already written to `.claude/.sofi-run/caddy/sites/dashboard.caddy`
(reverse-proxies `:8787`, WebSocket passes through). Two root steps activate it:
```bash
echo "127.0.0.1 dashboard.local" | sudo tee -a /etc/hosts
sudo systemctl reload caddy
```
Until then, use `http://127.0.0.1:8787` directly (no sudo needed).

## The tabs
1. **🧠 Brain Network** — interactive Cytoscape org graph, **registry-driven** (no hardcoded
   roster — v5 debt #6 paid): 15 room boxes · 105 agents, each room colored, its Lead on top,
   members below; dashed council edges wire `brd-ceo` to every Room Lead. Drag / zoom / pan /
   click a node for its role, model, effort, budget, gate. When an agent goes active (live),
   its node **glows** and its delegation edges **flow**. Room-filter chips top-left.
2. **🛰️ Live Observatory** — live stream (sessions.jsonl + audit.jsonl + per-project runlog),
   the verification gates (`gates.py`: no-skip / artifacts / room-boundary / evidence), and the
   reflection engine's current learning signals (Article 04).
3. **📋 Task Manager** — the ticket queue (HANDOFFS.md) per project: id, gate, from→to, type,
   status, colour-coded (open / done / blocked-escalated).
4. **🎚️ Planning & Budgets** — effort-scaling fan-out table + budgeted-autonomy ceilings,
   per-agent token budget envelopes with danger gauges, and real per-agent activity bars.
5. **🚀 Fleet & Plan** *(v6.1)* — live **fleet telemetry** from every hook (`/api/events`
   → `telemetry.py`): total/source/kind/agent tiles, breakdown bars, and a self-refreshing
   event feed reading the real `.claude/memory/events.jsonl`. Plus the frozen **plan DAG**
   (`/api/plan` → `scheduler.py`): nodes grouped done / ready-now / queued with room·agent·gate·
   deps, ready-set computed client-side to mirror `sofi run`, and the mermaid source.
6. **⌨️ Direct Commands** — whitelisted, read-only-first headless `sofi` / Claude Code runs,
   streamed live. **💬 Live Chat** — a persisted multi-session conversation inside the workspace.

## Data sources (all real, read-only)
`company/nexus/registry.yaml` (rooms + 105 agents, via `/api/registry`) ·
`company/nexus/routing.yaml` (routes · effort_scaling · budgeted_autonomy) ·
`sofi_tools.tickets` (queue + Room Isolation Law) · `sofi_tools.gates` (validators) ·
`reflection_engine.scan()` · `.claude/memory/sessions.jsonl` + `audit.jsonl` +
`projects/*/_context/_runlog.md` (live feed).

## Grounding note (Article 02)
The framework has no token-cost meter, so the dashboard does **not** invent a live-cost number.
Budgets shown are the **configured envelopes** (real, from nexus/routing.yaml); "live activity"
is the **real logged-event count** per agent, labelled `estimated`. Nothing is fabricated — per
the grounding law (`company/constitution/02-grounding.md`).

The dashboard is **read-only**: it never writes to the brain, never touches security/architecture
code, never mutates project state.
