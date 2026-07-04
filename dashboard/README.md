# SOFI v5 — Live Observability Dashboard

A flexible multi-tab web console for watching the agent org in real time. It reads the
**real** v5 data sources (never fabricates) and streams live activity over a WebSocket.

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

## The four tabs
1. **🧠 Brain Network** — interactive Cytoscape node graph. 30 agents (CEO center → 5 Advisors
   → 24 specialists, colored by tier). Drag / zoom / pan / click a node for its role, model,
   effort, budget, gate. Edges are the legal tier-isolation handoff channels. When an agent goes
   active (live), its node **glows** and its handoff edges **flow**. Tier-filter chips top-left.
2. **🛰️ Live Observatory** — live stream (sessions.jsonl + audit.jsonl + per-project runlog),
   the verification gates (`gates.py` C4: no-skip / artifacts / tier-boundary / evidence), and the
   reflection engine's current learning signals (C2).
3. **📋 Task Manager** — the ticket queue (HANDOFFS.md) per project: id, gate, from→to, type,
   status, colour-coded (open / done / blocked-escalated).
4. **🎚️ Planning & Budgets** — effort-scaling fan-out table + budgeted-autonomy ceilings (C5),
   per-role token budget envelopes with danger gauges, and real per-agent activity bars.

## Data sources (all real, read-only)
`engine/routing/routing.yaml` · `sofi_tools.tickets` (roster + tiers + tickets) ·
`sofi_tools.gates` (validators) · `reflection_engine.scan()` (C2) ·
`.claude/memory/sessions.jsonl` + `audit.jsonl` + `projects/*/_context/_runlog.md` (live feed).

## Grounding note (v5 C1)
The framework has no token-cost meter, so the dashboard does **not** invent a live-cost number.
Budgets shown are the **configured envelopes** (real, from routing.yaml); "live activity" is the
**real logged-event count** per agent, labelled `estimated`. Nothing is fabricated — per the v5
grounding doctrine (`engine/protocols/grounding.md`).

The dashboard is **read-only**: it never writes to the brain, never touches security/architecture
code, never mutates project state.
