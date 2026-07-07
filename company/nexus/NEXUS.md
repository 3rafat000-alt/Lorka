# 🕸️ THE NEXUS — how everything connects

> **Design is Truth · few token do trick · big brain small mouth.** 🪨
> The Nexus is the connecting layer of the Company of Rooms: 15 rooms (غرف), 105 agents, one bus, one economic grid, nine gates. Law lives in `company/CONSTITUTION.md` and `company/constitution/00..10`; the Nexus **implements** that law as machine truth. Nothing here contradicts the Constitution — a conflict is a defect (Precedence §3), surface it and fix this layer.

The Nexus is four configs, one bus, and one operator room:

| Piece | File | What it is |
|---|---|---|
| **Registry** | `company/nexus/registry.yaml` | ONE machine index — every room, agent, skill, tool, power. One read discovers the whole company. |
| **Routing** | `company/nexus/routing.yaml` | THE economic grid — the model ladder, `routes.<id>` for all 105 agents, effort scaling, budgets. The single source; nothing hardcodes a model. |
| **Gates** | `company/nexus/gates.yaml` | The 9 gates machine-readable — trigger, owner room, entry, artifacts, exit bar, on-fail. |
| **Bus** | `company/nexus/bus/` | `ticket-schema.md` (the TKT block) + `escalation.md` (chains, breaker, veto, arbitration). |
| **Operators** | Room `14-gateway` (`gtw`) | Six agents who run the Nexus — dispatch, route, verify, consult, mediate, budget. |

## 1. The Registry — one read, whole company

`registry.yaml` answers "who exists, where is their spec, what may they touch" in a single read (progressive disclosure, `05-token-economy.md` §3). Per room: `{code, dir, name, emoji, gates, lead, agents}`; per agent: `{id, title, spec, spawnable, model, route, budget, tools}`. Then the 13 `/sofi-*` skills, the OS tooling (library · CLI · scanners), and the vetted superpowers.

Consumers, all mechanical:
- `sofi registry` queries it; `sofi rooms` lists rooms + members; `/sofi-team` renders the who-does-what picker.
- `sofi_tools.tickets.validate_room_boundary()` loads its agent→room map (fail-open on unknown ids) — the Room Isolation Law, wired (v5 debt #4 paid: no more hardcoded role maps).
- `sofi doctor` checks **105 ↔ 105 dual-file parity**: every `agents[].spec` (`company/rooms/<NN-room>/agents/<id>.md`) must have its twin `agents[].spawnable` (`.claude/agents/<id>.md`), and vice versa.
- `guard.assert_net_allowed` derives the web-holding roles from each agent's `tools` list (Article 09).
- The dashboard renders the org graph from it — registry-driven, never hardcoded (v5 debt #6 paid).

Route strings in the registry are convenience mirrors for one-read discovery. On any drift, `routing.yaml` wins and `sofi doctor` flags the mismatch.

## 2. The Bus — tickets in `HANDOFFS.md`

The bus is not middleware. It is **ticket blocks appended to the project brain's `_context/HANDOFFS.md`**, validated mechanically, spine'd by git (Article 08). Every handoff appends one `## TKT-NNN · gate N` block — `from, to, task, consumes, expected, route, status` — schema binding in `bus/ticket-schema.md`.

- Lifecycle: `open → accepted → done | rejected`; escalations flip `blocked → escalated` and file an up-chain ticket carrying `escalated_from:` (traceable).
- `done` requires an **evidence block** — command + exit code, `file:line` proof, or diff/SHA. `sofi_tools.gates.validate_evidence()` rejects bare "done"s, fail-closed (Article 03 V1).
- `sofi handoff <op> <ID>` and `sofi dispatch` operate the queue; `sofi brain-query` filters by the optional `type:`/`mem:` frontmatter.
- A ticket carries no live memory — git does. Producer checkpoints (نقطة) before `done`; receiver `sofi sync`s before `accepted`. Uncommitted work is invisible work.

## 3. Room Isolation Law + verbatim forwarding

A specialist speaks only inside its own room. Cross-room work travels ONE path and returns the same path:

```
specialist → own room's Lead → target room's Lead → target specialist
```

- **Leads forward VERBATIM.** A Lead routes and gates; it never re-authors. Findings cross a boundary with their `file:line` citations and evidence blocks intact. Re-summarizing is the translation tax — it costs tokens AND strips the grounding Article 02 requires. A one-line routing note ("forwarding dat-db-engineer's finding to 04-architecture") is fine; re-narration is not.
- **Only the boardroom (`brd-*`) and the gateway room (`gtw-*`) may address any Lead directly.** No specialist reaches past its Lead — not even "just a quick question."
- **Enforced mechanically:** `validate_room_boundary()` runs inside `sofi gate-check`; a boundary violation fails the gate exactly like a skipped gate. Valid `from:`/`to:` pairs: same room · agent ↔ its own Lead · Lead ↔ Lead · boardroom/gateway ↔ any Lead.

## 4. The gateway room — six operators, and when each acts

Room `14-gateway` (🕸️ `gtw`) is the Nexus made staff. Cross-gate, no product deliverables — they operate the connecting layer itself.

| Operator | Route | Acts WHEN |
|---|---|---|
| **`gtw-dispatcher`** (★ Astrid Lindqvist) | workhorse · high · full | A Work Order enters the org or spans rooms: turns the CEO's/chief-of-staff's intent into bus tickets, addresses the right room Leads (it may address any Lead), sequences multi-room work, runs `sofi dispatch` / `sofi squad`. Every task that isn't already a single in-room ticket passes through the dispatcher first. |
| **`gtw-router`** | mechanical · low · ultra | Before any spawn: looks up `routes.<id>` in `routing.yaml`, applies `priority_override` / `raise_when` / `lower_when`, stamps the route into the ticket and `STATE.md` `last_route`. Cheapest that clears the bar, always logged — an unlogged route is an unauditable expense. Runs `sofi route`. |
| **`gtw-gatekeeper`** | gatekeeper · high · full | A gate wants to advance, or a high-stakes ticket wants `accepted`: fresh-context adversarial verify (Article 03 V2) — sees ONLY the deliverable + the ORIGINAL criteria, never the implementer's reasoning. Verdicts: PASS / FAIL / **UNKNOWN** (valid — routes to `sofi escalate`, never a coin-flip). Runs `sofi gate-check`; `/sofi-gate` invokes it. The implementer never grades itself. |
| **`gtw-external-reviewer`** | workhorse · medium · full | A Teaching-VII decision point, any report worth a second mind, or a money/auth/PII verdict needing a family-diverse judge: runs the oracle desk — `sofi oracle review --prj <PRJ> --json --text "…"` — sanitize → condense → send → capture → parse → ingest digest to `HANDOFFS.md`. Never secrets/PII (Article 07 §3). The desk **advises**; it never approves gates. |
| **`gtw-conflict-resolver`** | workhorse · medium · full | Two rooms deadlock — contested claim in `LOCKS.md`, contradictory frozen artifacts, a rejected ticket bouncing twice: mediates on the evidence, read-only. Unresolved → escalates to `brd-arbiter` with both positions forwarded verbatim. |
| **`gtw-budget-warden`** | mechanical · low · ultra | Weekly, and on demand (`sofi budget`): audits token spend per gate against `routing.yaml` budget bands — unlogged routes, deep-tier on routine work, chat >500 chars that isn't code/security, orphaned report files. Keeps the circuit-breaker ledger (every trip is a reflection signal, Article 04). Findings go to `brd-ceo` as defects — waste is a defect. |

## 5. Escalation — one chain, one breaker

Full mechanics: `bus/escalation.md`. The decision chain (never sideways, never guess):

```
specialist → room Lead → gtw-conflict-resolver → brd-arbiter → brd-ceo
```

- **Reject upward ≠ escalate.** Missing/unfrozen upstream → *reject upward* (blocker ticket, stop). Decision above your authority → *escalate* (`sofi escalate <PRJ> <TKT> <to> "<reason>"`). Article 00 §table.
- **Security spur:** any security finding → `sec-lead` → `brd-cso`. The CSO veto is **absolute below the CEO** (Article 07 §1) — it can freeze any gate, merge, deploy, or tunnel, and lifts only on remediation-with-evidence or a CEO ADR override.
- **Circuit breaker:** 3 self-correction attempts max. The 4th failure = HALT + structured crash-dump JSON + escalation ticket + await an ADR'd decision (Article 00 §circuit-breaker). Never loop a 4th time.
- Escalation may bump the route (`routing.yaml` `escalation.priority_override`: CRITICAL = +1 model / +1 effort, and must be able to reach `gatekeeper`).

## 6. Gate advancement — two layers, then the tag

A gate advances through this flow and no other (`/sofi-gate` runs it end-to-end):

```
producer marks done WITH evidence block          (Article 03 V1 — self-report is not evidence)
        ↓
sofi gate-check — mechanical, fail-closed        (artifacts exist per gates.yaml · validate_evidence ·
        ↓                                          validate_no_skip · validate_room_boundary)
gtw-gatekeeper — fresh-context adversarial       (Article 03 V2 — deliverable + ORIGINAL exit bar from
        ↓                                          gates.yaml, never the implementer's reasoning;
        ↓                                          UNKNOWN → escalate; money/auth/PII → oracle desk judge)
exit bar in gates.yaml clears → sofi gate-tag    (<PRJ>-gate<N>-done — immutable restore point)
```

The oracle desk advises; `gtw-gatekeeper` decides; the boardroom answers for the span (`brd-cpo` 0–2 · `brd-cto` 3–4 · `brd-cqo` 5 · `brd-ceo` all). Room 09-security can veto at any step. Loop-backs are legal and reported (quality bounces build; Gate 8 re-opens Gate 1); skips never are.

## 7. Parallel rooms — only behind a frozen input

Fan-out is legal exactly where `gates.yaml` says a frozen input exists (`sofi squad <PRJ> <gate>` renders the concurrent Work Orders, each in its own worktree — Article 06 §worktrees):

- **Gate 3** — rooms `arc · dat · sec` in parallel behind the frozen Gate-2 prototype.
- **Gate 4** — rooms `bck · fnt · mob` (data room in support) behind the frozen Gate-3 bundle; no engineer waits on another, only the contract must be frozen.
- **Gate 5** — QA dimensions (automation · manual · perf · design-audit) + security (pentest) behind the merged build.

Never fan out the sequential phases of ONE ticket — that pays the coordination tax with no parallelism payoff (`01-work-order.md` §4, `routing.yaml` `effort_scaling.context_boundary`). Leads `gate-merge` worktrees at close, never before. Shared paths are claimed first (`sofi claim` → `LOCKS.md`).

## 8. Budget enforcement — the warden and the bands

Teaching IV, operationalized:

1. Every route in `routing.yaml` carries a **budget band** (1k–3k mechanical … 8k–15k heavy dev; leads/gatekeepers "as-needed" — *as-needed is not unlimited, it is unbudgeted-but-audited*).
2. Every Work Order states its **effort-scaling class + call budget + fail-safe stop** (`01-work-order.md` §4) — no budget, no spawn.
3. The **3-attempt ceiling → circuit breaker** is the fuse on every sub-task (Article 00).
4. **`gtw-budget-warden`** audits weekly and on demand (`sofi budget`); findings land on `brd-ceo`'s desk as defects. The company's median turn should cost mechanical-tier money (the 80%-mechanical rule, `05-token-economy.md` §1).

## 9. Cross-reference map

| Need | Go to |
|---|---|
| Who does X / spawn id / spec path | `registry.yaml` · `/sofi-team` |
| Route for an agent | `routing.yaml` `routes.<id>` · `sofi route` |
| What a gate demands | `gates.yaml` · `constitution/10-lifecycle-gates.md` · `/sofi-gate` |
| Ticket shape | `bus/ticket-schema.md` · Article 08 |
| Escalation / veto / arbitration | `bus/escalation.md` · Article 00 · Article 07 §1 |
| Delegation block | `constitution/01-work-order.md` · `/sofi-delegate` |
| Verification law | `constitution/03-verification.md` |
| Oracle audit dispatch (GitHub issues → agents) | `nexus/gemini-audit-dispatch.yaml` |

Big brain, small mouth: the Nexus carries pointers and verdicts, never essays. 🪨
