# ⚡ SOFI AI — Quick Command Cheat-Sheet (v6)

Keep it nearby. Full detail in `USER_GUIDE.md`.

## 🚀 Start
```
Use the brd-ceo agent
New project: <idea>. Start onboarding
```

## ▶️ Flow control
| Command | Does |
|---------|------|
| `continue` | advance to the next gate |
| `assume reasonable answers and proceed to gate 4` | run straight through, no pauses |
| `where are we?` | read STATE.md (don't re-explain) — or `/sofi-boot` |
| `revisit the decision` | loop back to the right gate |
| `give me the project summary` | state + tickets + ADRs |

## 🎯 Ideal request format
```
Goal:     <one sentence>
Project:  PRJ-XXXX | new
Limits:   <stack / platform / deadline>
Priority: CRITICAL | HIGH | MEDIUM | LOW
Success:  <when it's done>
```

## 🛠️ The 13 skills (`/sofi-*`)
| Skill | One-liner |
|-------|-----------|
| `/sofi-boot` | orient — git sync + load the brain, report gate·branch·head_sha·next ticket |
| `/sofi-team` | show the roster (15 rooms · 105 agents) and pick the right agent |
| `/sofi-delegate <agent> "<task>"` | build a paste-ready 4-part RCCF Work Order |
| `/sofi-gate` | check the gate's exit bar, fresh-context verify, then advance (no skip) |
| `/sofi-handoff` | close work the disciplined way — artifact → checkpoint → CONTEXT → STATE → next ticket |
| `/sofi-reflect` | scheduled dreaming — distil HANDOFFS into `_context/LESSONS.md` |
| `/sofi-audit <layer>` | token-frugal layered inspection (ui/blade/css/js/db/api/integration/agents/all) |
| `/sofi-spec-review "<feature>"` | architect 4-pillar review + 7 steel rules, SEV-report-first |
| `/sofi-feature "<feature>"` | the big one — scan → review → fix → verify → report → gate → handoff |
| `/sofi-secure <mode>` | security room — threat / pentest / scan / verify |
| `/sofi-fix <target>` | findings → cheapest specialist → checkpoint each |
| `/sofi-report <kind>` | durable, evidence-backed writeup to the brain (EN/AR) |
| `/sofi-design-taste` | anti-generic-UI dials (variance · motion · density), Gate 2/4 |

## 🧑‍💼 Direct agent call (rare)
```
Use the <roomcode>-<role> agent: <task>
```
Common: `sec-lead` (security) · `qa-lead` (quality) · `arc-lead` (architecture) · `bck-api-engineer` (backend) · `gtw-dispatcher` (routing). Reach a room via its **Lead** — the sole gateway. Full roster: `company/ORG.md`.

## 🖥️ The `sofi` CLI (Bash-holding roles · `company/os/bin/sofi <verb>`)
```
sofi sync <PRJ>            git orient — never a blind start   (/sofi-boot wraps this)
sofi checkpoint <PRJ> "…"  commit a milestone to the project's own repo
sofi brain <PRJ>           STATE + next open ticket
sofi brain-query …         structured brain retrieval (filter by status/type/gate)
sofi route <id>            cheapest clearing route for an agent
sofi rooms                 list the 15 rooms
sofi registry …            query the machine index (rooms → agents → skills → tools)
sofi gate-check <PRJ>      validate gate order + artifacts (mechanical evidence)
sofi dispatch <PRJ>        delegation prompt for the open ticket
sofi squad <PRJ> …         fan a gate's parallel squad behind a frozen input
sofi handoff <PRJ> …       record a handoff ticket
sofi escalate <PRJ> <TKT> <to> "…"   send a decision UP the chain (never sideways)
sofi worktree <PRJ> …      parallel-squad git worktree
sofi gate-merge <PRJ>      merge a room's worktree at gate close
sofi gate-tag <PRJ>-gate<N>-done     stamp the immutable gate tag
sofi git-check             secret scan + commit-format guard
sofi domain <op> <PRJ>     local domain — init/register/up/down (<slug>.local)
sofi tunnel up|down <PRJ>  bounded public URL — seed data only, kill when done
sofi oracle <op> …         external review desk (review·capture·status; alias: sofi gemini)
sofi budget …              token budgets, circuit breakers, waste audit
sofi doctor                self-check — enforces 105 ↔ 105 agent parity
```

## 🏢 The 15 room codes
```
brd  boardroom        القيادة — orchestrate · route · arbitrate (CEO never writes code)
str  strategy         gates 0-1 — problem · requirements · market · roadmap · risk · monetization
res  research         gate 1   — personas · the Journey Map (the Design Truth) · fact-checking
dsn  design           gate 2   — prototype · flows · tokens · copy · taste dials · a11y (WCAG wins)
arc  architecture     gate 3   — stack · schema · frozen API contract · integrations · infra · spec review
bck  backend          gate 4   — API · domain · Blade · queue · integration + code review
fnt  frontend         gate 4   — Vue3/React · CSS taste · micro-interactions · a11y · perf
mob  mobile           gate 4   — Flutter/Bloc · platform channels · perf · store releases
dat  data             gates 3-4 — reversible migrations · cache · analytics · ML · ETL · PII
sec  security         gates 3+5 — STRIDE · appsec · pentest · authn · secrets · compliance (veto everywhere)
qa   quality          gate 5   — ONE PASS/BLOCK verdict · ≥90% coverage · perf budgets · design audit
ops  devops           gates 6-7 — CI/CD · IaC · Blue/Green + tested rollback · domains & tunnels · cost
obs  observability    gate 8   — SLI/SLO · instrumentation · alerting · incident command · journey insights
knw  knowledge        cross    — MEMORY.md · brain hygiene · LESSONS dreaming · docs · ADR history · retrieval
gtw  gateway          cross    — dispatch · cost routing · fresh-context gate checks · oracle desk · budget
```

## 🔮 Routing ladder (cheapest that clears the bar)
`🟢 mechanical (haiku)` → `🔵 workhorse (sonnet)` → `🔮 gatekeeper (inherit)` → `🟣 deep (opus, last resort)`

## 🪨 Tokens
```
/caveman lite|full|ultra
normal mode
/caveman-stats
```

## 🗂️ Gates
`0 Inception → 1 Discovery → 2 Design → 3 Architecture → 4 Build → 5 Quality → 6-7 Deploy → 8 Observe`

## ✅ Remember
- Talk to the CEO (`brd-ceo`), not the individuals; reach a room via its **Lead**.
- Goal + limits + success = best context (a frozen RCCF Work Order).
- One project per `PRJ`; no cross-project bleed.
- Code / security / commits are never compressed.
- No skip gates — advancement is a fresh-context verify + mechanical evidence.
- `where are we?` / `/sofi-boot` before any big request.
