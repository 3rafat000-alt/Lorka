# 🎮 SOFI AI — Client Guide (how to ask the team · v6)

Your guide to running the enterprise with the best context and the fewest tokens. Read it once, then keep `COMMANDS.md` as a quick card.

> Golden rule: **Talk to the CEO (Magnus Holt · `brd-ceo`), not the individuals.** He assigns the project, routes every task across the 15 rooms, and injects the context. You give the goal — he runs the company.

---

## 1. How to start (3 steps)

### Step 1 — Boot the brain
In Claude Code, spawn the CEO, or orient on the active project:
```
Use the brd-ceo agent
/sofi-boot                 ← syncs git + loads STATE/CONTEXT/HANDOFFS, reports gate·branch·head_sha·next ticket
```

### Step 2 — Give an idea
```
New project: <your idea in one sentence>. Start onboarding.
```
The CEO assigns the next `PRJ-XXXX`, scaffolds the brain, registers a clean `<slug>.local` domain, and hands the idea to **01-strategy**, which asks you the **5 deep questions**. Answer them → the cascade runs.

### Step 3 — Let the rooms work
Each gate produces frozen artifacts under `projects/PRJ-XXXX/`. You review and decide whether to continue. Work flows **room → room** behind frozen inputs; nothing skips a gate.

---

## 2. The professional request format (copy and fill)

The closer your request is to this shape, the better the context and the sharper the result:

```
Goal:     <what you want, in one sentence>
Project:  PRJ-XXXX        (or "new")
Gate:     <if you know it; otherwise leave it to the CEO>
Limits:   <budget / platform / stack / deadline>
Priority: CRITICAL | HIGH | MEDIUM | LOW
Success:  <when you'll call it done>
```

**Good example:**
```
Goal: Add fingerprint login to the app.
Project: PRJ-0001. Priority: HIGH.
Limits: Flutter, must work offline.
Success: User logs in by fingerprint, PIN fallback, covered by tests.
```

**Bad example (wastes tokens):** "Make me a nice app." ← vague; the CEO will run 01-strategy's 5 questions before any work.

This four-field shape *is* the **RCCF Work Order** the CEO freezes before spawning anyone (Role · Context · Command · Format). A frozen brief means no instruction-drip; a vague one means the CEO clarifies first, never spawns blind.

---

## 3. Core commands

| You want… | Tell the CEO |
|-----------|--------------|
| New project | `New project: <idea>. Start onboarding` |
| Advance to the next gate | `continue` |
| Run through without pausing | `assume reasonable answers and proceed to gate <n>` |
| Know where we are | `where are we?` (reads `STATE.md`) — or `/sofi-boot` |
| Activate a specific agent | `Use the <roomcode>-<role> agent` (e.g. `sec-pentester`) |
| Review a whole feature | `/sofi-spec-review "<feature>"` → `arc-review-architect`'s 4-pillar hard gate |
| Inspect a layer | `/sofi-audit <layer>` (ui/blade/css/js/db/api/integration/agents/all) |
| Do everything for a feature | `/sofi-feature "<feature>"` → scan → review → fix → verify → report → gate → handoff |
| Save tokens | `/caveman ultra` |
| Stop compressed mode | `normal mode` |

---

## 4. The skills — your control panel (`/sofi-*`)

Skills are the disciplined, token-frugal way to drive the company. Type the slash command; it wires the right rooms and tools.

**Discipline core**
| Skill | Does |
|-------|------|
| `/sofi-boot` | orient — git sync + load the brain, report gate·branch·head_sha·next ticket (no blind start) |
| `/sofi-team` | show the roster (15 rooms · 105 agents) and pick the right agent for a task |
| `/sofi-delegate <agent> "<task>"` | build a paste-ready 4-part **RCCF Work Order** for any agent |
| `/sofi-gate` | check the current gate's exit bar, run the fresh-context adversarial verify, then advance (no skipping) |
| `/sofi-handoff` | close a unit of work the disciplined way — artifact → checkpoint → CONTEXT → STATE → next ticket |
| `/sofi-reflect` | scheduled "dreaming" — distil HANDOFFS history into `_context/LESSONS.md` (never per-turn) |

**Power tools** (flexible · grep-first · Python locates, model judges)
| Skill | Does |
|-------|------|
| `/sofi-audit <layer>` | comprehensive, token-frugal inspection of any layer of the codebase |
| `/sofi-spec-review "<feature>"` | architect 4-pillar cross-layer review + 7 steel rules, SEV-report-first |
| `/sofi-feature "<feature>"` | the big one — full loop on one feature end-to-end in a single invocation |
| `/sofi-secure <mode>` | the security room — threat / pentest / scan / verify, wired to the vendored cyber armory |
| `/sofi-fix <target>` | turn findings into applied, checkpointed fixes routed to the cheapest specialist |
| `/sofi-report <kind>` | durable, evidence-backed writeup to the brain (bilingual EN/AR ready) |
| `/sofi-design-taste` | anti-generic-UI dials (variance · motion · density) at Gate 2 / Gate 4 |

Loop: **audit / secure → fix → report → gate → handoff.**

---

## 5. Calling agents by name (when to bypass the CEO)

Usually **don't call individuals** — the CEO knows the sequence and the Room Isolation Law keeps context clean. But if you want a specialist directly, use its id `<roomcode>-<role>`:

```
Use the <roomcode>-<role> agent: <task>
```

| Room | Lead (gateway) | Reach for… |
|------|----------------|------------|
| 00-boardroom | `brd-ceo` (Magnus Holt) | **default — everything: routing, arbitration, gates** |
| 01-strategy | `str-lead` (Amara Okafor) | problem definition, scope, requirements, roadmap, risk |
| 02-research | `res-lead` (Hiroshi Tanaka) | personas, the Journey Map, competitor teardowns, fact-checking |
| 03-design | `dsn-lead` (Dan Kim) | prototypes, flows, tokens, copy, taste dials, a11y |
| 04-architecture | `arc-lead` (Vikram Rao) | stack, schema, the frozen API contract, integrations, infra |
| 05-backend | `bck-lead` (Elif Kaya) | endpoints, domain logic, Blade views, jobs, integrations |
| 06-frontend | `fnt-lead` (Grace Achieng) | Vue3/React, CSS taste, micro-interactions, a11y-in-code, perf |
| 07-mobile | `mob-lead` (João Silva) | Flutter/Bloc, platform channels, perf profiling, store releases |
| 08-data | `dat-lead` (Günther Weber) | migrations, cache, analytics, ML, ETL, PII privacy |
| 09-security | `sec-lead` (Ruth Goldberg) | threat model, appsec review, pentest, secrets, compliance |
| 10-quality | `qa-lead` (Barb Jensen) | the ONE PASS/BLOCK verdict, coverage, perf, design-fidelity audit |
| 11-devops | `ops-lead` (Linda Schmidt) | CI/CD, environments, Blue/Green + rollback, domains & tunnels |
| 12-observability | `obs-lead` (Naomi Brooks) | SLI/SLO, instrumentation, alerting, incident command |
| 13-knowledge | `knw-lead` (the Librarian) | MEMORY.md routing, brain hygiene, LESSONS, docs, ADR history |
| 14-gateway | `gtw-dispatcher` (Astrid Lindqvist) | Work-Order dispatch, cost routing, fresh-context gate checks, oracle desk |

> A room has more specialists than its Lead — reach the Lead and let the wall do its job. Full roster with personas + routes: `company/ORG.md`. Pick the exact id fast with `/sofi-team`.

---

## 6. The nine gates (what each `continue` does)

```
0 Inception    → 01-strategy: problem statement + 5 questions
1 Discovery    → 02-research: evidence-grounded personas + the Journey Map (the Design Truth)
2 Design       → 03-design: prototype spec + tokens + copy + taste dials — WCAG 2.2 AA wins
3 Architecture → 04-architecture (+ 08-data + 09-security): stack + schema + frozen API contract + threat model
4 Build        → 05-backend · 06-frontend · 07-mobile, parallel behind the frozen Gate-3 bundle
5 Quality      → 10-quality (+ 09-security): ONE aggregated PASS/BLOCK verdict
6-7 Deploy     → 11-devops: staging/UAT + Blue/Green production + tested rollback
8 Observe      → 12-observability: SLI/SLO + alerts → any breach re-opens Gate 1
```
Never skip a gate. Advancement is only through `gtw-gatekeeper`'s **fresh-context adversarial check** against the *original* exit bar + mechanical evidence (`sofi gate-check`) — the implementer never grades itself.

**Two-track sizing:** low-risk work (copy, i18n, a field, non-money validation) can take the **Fast-Track**; anything touching **money / credentials / auth / PII** is **Deep-Audit** — full 9 gates, no exception. Unsure → Deep-Audit.

---

## 7. The brain & isolation (how memory works)

- Every project has its own brain under `projects/PRJ-XXXX/_context/`: **STATE** (live head — branch·head_sha·gate) · **CONTEXT** (running log) · **DECISIONS** (irreversible calls) · **HANDOFFS** (the ticket bus) · **LESSONS** (distilled learning).
- Projects are **isolated by `PRJ-XXXX`** — no cross-project bleed, each its own git repo.
- **The universal contract:** before acting, an agent runs `sofi sync <PRJ>` → reads STATE → its ticket in HANDOFFS → CONTEXT. After acting, it writes the artifact → `sofi checkpoint` → appends CONTEXT → updates STATE (`head_sha`) → writes the next ticket. **An uncommitted session is invisible to the next one.**
- `MEMORY.md` (root) is the routing map — *"where do I find X?"* — pointers only, never content. Ask `where are we?` and the CEO reads the brain instead of re-explaining.

---

## 8. Token-frugality (cheapest route, biggest brain)

The company is deliberately token-miserly. You benefit by leaning into it:

✅ **Do**
- Give a goal + limits + success (format in §2) — a frozen brief costs the fewest tokens.
- Ask `where are we?` / `/sofi-boot` before a big request — it reads the brain instead of re-explaining.
- Trust the **cheapest-route-that-clears-the-bar** rule: mechanical (haiku) does ~80% of routine ops; only cross-layer sweeps and hard gates reach the gatekeeper tier.
- Prefer the power skills — **Python locates and pre-flags** (free), the **model spends tokens only on judgment**.
- One project = one `PRJ`. Don't mix.

❌ **Don't**
- No vague requests ("make something nice") — they burn tokens on clarifying questions.
- Don't skip gates manually — it breaks traceability and the verify chain.
- Don't mix two projects in one request — isolation breaks.
- Don't ask a specialist for a decision above their authority — that goes UP the chain to the Lead / CEO, never sideways, never guessed.

**Caveman** compresses chatter (`/caveman lite|full|ultra`, `normal mode`) — but **code, commits, and security warnings are always written in normal prose, never compressed.**

---

## 9. Where to find everything

| You want | File |
|----------|------|
| The supreme law | `company/CONSTITUTION.md` |
| The articles (operating system) | `company/constitution/00–10` |
| The org — 15 rooms · 105 agents | `company/ORG.md` |
| How rooms connect | `company/nexus/NEXUS.md` |
| Cost per task | `company/nexus/routing.yaml` |
| How the CEO drives a project | `company/RUNBOOK.md` |
| The script layer | `company/os/` (+ `company/os/GOVERNANCE.md`) |
| Your project's live state | `projects/PRJ-XXXX/_context/STATE.md` |
| The routing map ("where is X?") | `MEMORY.md` |
| Quick shortcuts | `COMMANDS.md` |

---

*Start now: `New project: <your idea>. Start onboarding`*
